import datetime

from flask import Flask, request
import requests
from celery import Celery
import time

celery_app = Celery("informacionHvBuscadores", broker="redis://redis:6379/0")

app = Flask(__name__)

MATCHING_SERVICE_URL = "http://motor-emparejamiento:6000/matching"
CIRCUIT_BREAKER_STATE = "closed"

CONTEXT_PATH= "/api"
AUTH_PATH= "/auth"
TASKS_PATH= "/tasks"

@app.route("/")
def hello():
    return "Hello from tasks!"

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["GET"])
def getTasks():
    return "Hello from" + CONTEXT_PATH + TASKS_PATH, 200

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["DELETE"])
def deleteTasks():
    return "Hello from" + CONTEXT_PATH + TASKS_PATH, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
