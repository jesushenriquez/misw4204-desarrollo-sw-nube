from flask import Flask, request, jsonify
import requests
from celery import Celery
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

celery_app = Celery("apigateway", broker="redis://redis:6379/0")

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# INTEGRITY_MANAGER_SERVICE_URL = "http://integrity-manager:6000/"
# INFORMACION_HV_BUSCADOR_URL = "http://informacion-hv-buscadores:5000/"
TASK_SERVICE_URL = "http://task-manager:5000/"
AUTH_SERVICE_URL = "http://auth-component:8080/"

CONTEXT_PATH= "/api"
AUTH_PATH= "/auth"
TASKS_PATH= "/tasks"
@app.route("/")
def hello():
    return "Hello from apigateway v6!"

@app.route(CONTEXT_PATH + AUTH_PATH + "/login", methods=["POST"])
def login():
    try:
        response = requests.post(AUTH_SERVICE_URL+'login', json=request.json)
        logging.info("Login: %s", response.json())
        return response.content, response.status_code
    except Exception as e:
        logging.error("Error login: %s", e)
        return str(e), 500

@app.route(CONTEXT_PATH + AUTH_PATH + "/signup", methods=["POST"])
def register():
    try:

        response = requests.post(AUTH_SERVICE_URL+'register', json=request.json)
        logging.info("Register: %s", response.json())
        return response.content, response.status_code
    except Exception as e:
        logging.error("Error register: %s", e)
        return str(e), 500

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["GET"])
def getTasks():
    try:
        # jwt_token = request.headers.get('Authorization')
        # logging.info("jwt_token:", jwt_token)
        response_tasks = requests.get(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH, json=request.json)
        logging.info("response_tasks:", response_tasks)
        return response_tasks.content, response_tasks.status_code
    
        # response = requests.get(AUTH_SERVICE_URL+'tasks', json=request.json)
        # logging.info("Get tasks: %s", response.json())
        # return response.content, response.status_code
    except Exception as e:
        logging.error("Error get tasks: %s", e)
        return str(e), 500

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["POST"])
def newTasks():
    return "Hello from" + CONTEXT_PATH + TASKS_PATH

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["GET"])
def getTask(task_id):
    return "Hello from" + CONTEXT_PATH + TASKS_PATH

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["DELETE"])
def deleteTask(task_id):
    try:

        response_tasks = requests.delete(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH, json=request.json)
        logging.info("response_tasks:", response_tasks)
        return response_tasks.content, response_tasks.status_code
    
    except Exception as e:
        logging.error("Error get tasks: %s", e)
        return str(e), 500

if __name__ == "__main__":
    print("Starting apigateway...")
    app.run(host="0.0.0.0", port=9000)
