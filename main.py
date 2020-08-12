import json
import os
import subprocess

from celery import Celery
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS

from config import ANSIBLE_PROJECT_PATH, CELERY_BROKER_URL, CELERY_RESULT_BACKEND

app = Flask(__name__)

CORS(app)

app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND
celery = Celery(app.name, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.update(app.config)


@celery.task(bind=True)
def run_playbook(self, data):
    playbook = data.get("playbook")
    extra_vars = data.get("extra_vars")

    # check if playbook exists
    playbook_path = os.path.join(ANSIBLE_PROJECT_PATH, playbook)
    if not os.path.isfile(playbook_path):
        raise Exception("Playbook does not exist")

    command = [
        "ansible-playbook",
        playbook
    ]

    # add extra-vars to command
    if extra_vars:
        extra_vars_str = ""
        for key, value in extra_vars.items():
            extra_vars_str += "{}={} ".format(key, value)
        extra_vars_str = extra_vars_str.strip()
        command.append("--extra-vars")
        command.append(extra_vars_str)

    # execute command
    process = subprocess.Popen(
        command,
        cwd=ANSIBLE_PROJECT_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    output = ""
    # read new lines while process is running
    while process.poll() is None:
        line = process.stdout.readline().decode()
        output += line
        self.update_state(state='PROGRESS', meta={'output': output.strip()})
        self.send_event('task-custom', output=output.strip())
    # read the rest after process has stopped
    line = process.stdout.read().decode()
    output += line
    return {
        'output': output.strip()
    }


@app.route("/api/playbook", methods=["POST"])
def route_playbook():
    data = request.json
    task = run_playbook.delay(data)
    return jsonify({}), 202, {'Location': url_for('route_playbook_status', task_id=task.id)}


@app.route('/api/playbook/<task_id>')
def route_playbook_status(task_id):
    task = run_playbook.AsyncResult(task_id)
    if task.state == 'FAILURE':
        response = {
            'state': task.state,
            'output': str(task.info),  # exception message
        }
    else:
        response = {
            'state': task.state,
            'output': task.info.get('output', ""),
        }
    return jsonify(response)


@app.route("/api/inventory")
def route_inventory():
    command = [
        "ansible-inventory",
        "--list"
    ]
    inventory = request.args.get('inventory')
    if inventory:
        command.append("-i")
        command.append(inventory)
    output = subprocess.check_output(
        command,
        cwd=ANSIBLE_PROJECT_PATH
    )
    output = output.decode()
    return json.loads(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
