import os

ANSIBLE_PROJECT_PATH = os.environ.get("ANSIBLE_PROJECT_PATH", "/home/lucas/Projects/clustarr/ansible")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
