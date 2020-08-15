import json
import subprocess
from flask import jsonify, request, url_for
from config import ANSIBLE_PROJECT_PATH

from clustarr_backend import app
from clustarr_backend.tasks import run_playbook


@app.route("/api/playbook", methods=["POST"])
def route_playbook():
    data = request.json
    playbook = data.get("playbook")
    extra_vars = data.get("extra_vars")
    task = run_playbook.delay(playbook=playbook, extra_vars=extra_vars)
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
        output = ""
        if task.info:
            output = task.info.get('output', "")
        response = {
            'state': task.state,
            'output': output,
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
    process = subprocess.Popen(
        command,
        cwd=ANSIBLE_PROJECT_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    if error:
        return jsonify({"error": error.decode()}), 500

    output = output.decode()
    return json.loads(output)
