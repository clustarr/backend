import os
import subprocess

from clustarr_backend import celery
from clustarr_backend.exceptions import PlaybookException
from config import ANSIBLE_PROJECT_PATH


@celery.task(bind=True)
def run_playbook(self, playbook, extra_vars=None):
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
    # read the rest after process has stopped
    line = process.stdout.read().decode()
    output += line
    if process.returncode != 0:
        raise PlaybookException(output.strip())
    return {
        'output': output.strip()
    }
