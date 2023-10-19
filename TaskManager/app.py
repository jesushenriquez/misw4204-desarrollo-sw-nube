import datetime
import logging
from flask import Flask, request, jsonify
import requests
from celery import Celery
import time
import psycopg2 
from flask_jwt_extended import JWTManager,create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '43141-123-csdf-1-xcvsdf-12asdf-1234%$'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['JWT_AlGORITHM'] = 'HS256'
jwt_manager = JWTManager(app)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configura la conexión a la base de datos PostgreSQL
db_connection = psycopg2.connect(
    host="postgres",
    port=5432,
    user="admin",
    password="password",
    database="cloud_db"
)

celery_app = Celery("informacionHvBuscadores", broker="redis://redis:6379/0")

app = Flask(__name__)

MATCHING_SERVICE_URL = "http://motor-emparejamiento:6000/matching"
CIRCUIT_BREAKER_STATE = "closed"

CONTEXT_PATH= "/api"
TASKS_PATH= "/tasks"

@app.route("/")
def hello():
    return "Hello from tasks!"

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["GET"])
def getTasks():

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM tasks")

    tasks = cursor.fetchall()

    cursor.close()

    # Convierte los resultados en una lista de diccionarios
    task_list = []
    for task in tasks:
        task_dict = {
            'id': task[0],
            'source_uuid': task[1],
            'source_name': task[2],
            'source_format': task[3],
            'target_format': task[4],
            'create_datetime': task[5],
            'start_convert': task[6],
            'end_convert': task[7],
            'status': task[8]
        }
        task_list.append(task_dict)

    return jsonify({"tasks": task_list}), 200

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["DELETE"])
def deleteTask(task_id):
    try:

        cursor = db_connection.cursor()

        delete_query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(delete_query, (task_id,))

        db_connection.commit()
        cursor.close()

        return jsonify({"message": "Task eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"message": "Error al eliminar task", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
