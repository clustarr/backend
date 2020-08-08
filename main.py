from flask import Flask
import json
import subprocess
from config import *


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


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
