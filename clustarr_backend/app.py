from celery import Celery
from flask import Flask
from flask_cors import CORS

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

app = Flask(__name__)
CORS(app)

app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND
celery = Celery(app.name, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.update(app.config)
