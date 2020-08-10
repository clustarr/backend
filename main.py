import json
import os
import subprocess
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import *

app = Flask(__name__)
CORS(app)


@app.route("/api/playbook", methods=["POST"])
def route_playbook():
    data = request.json

    # check for missing keys
    for key in ["playbook", "extra_vars"]:
        if key not in data:
            return jsonify({
                "error": "{} not specified".format(key)
            })

    # check if playbook exists
    playbook = data.get("playbook")
    playbook_path = os.path.join(ANSIBLE_PROJECT_PATH, playbook)
    if not os.path.isfile(playbook_path):
        return jsonify({
            "error": "Playbook does not exist"
        })

    # build variables string
    extra_vars = data.get("extra_vars")
    extra_vars_str = ""
    for key, value in extra_vars.items():
        extra_vars_str += "{}={} ".format(key, value)
    extra_vars_str = extra_vars_str.strip()

    command = [
        "ansible-playbook",
        playbook,
        "--extra-vars",
        extra_vars_str
    ]
    process = subprocess.Popen(
        command,
        cwd=ANSIBLE_PROJECT_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    lines = []
    # read new lines while process is running
    while process.poll() is None:
        line = process.stdout.readline().decode()
        sys.stdout.write(line)
        lines.append(line)
    # read the rest after process has stopped
    line = process.stdout.read().decode()
    sys.stdout.write(line)
    lines.append(line)

    return jsonify(lines)


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
    app.run(debug=True)
