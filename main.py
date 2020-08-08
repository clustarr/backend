from flask import Flask, jsonify, request
import os
import sys
import json
import subprocess
from config import *


app = Flask(__name__)


@app.route("/api/playbook", methods=["POST"])
def execute():
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
        "\"{}\"".format(extra_vars_str)
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
def inventory():
    command = [
        "ansible-inventory",
        "--list"
    ]
    output = subprocess.check_output(
        command,
        cwd=ANSIBLE_PROJECT_PATH
    )
    output = output.decode()
    return json.loads(output)


if __name__ == "__main__":
    app.run(debug=True)
