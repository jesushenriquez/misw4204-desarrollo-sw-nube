import json
from datetime import datetime
import os
import uuid
from google.cloud import pubsub_v1

from flask import Flask, request, jsonify, send_file
#import datetime
import logging
import requests
from celery import Celery
import time
import psycopg2
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager,create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '43141-123-csdf-1-xcvsdf-12asdf-1234%$'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['JWT_AlGORITHM'] = 'HS256'
jwt_manager = JWTManager(app)

def get_env():
    # Obtener el environment del parámetro del comando
    env = os.getenv("ENV", "local")

    # Cargar el archivo de entorno correspondiente
    if env == "local":
        env_file = "/app/env/.env"
    elif env == "cloud":
        env_file = "/app/env/.env.cloud"
    else:
        raise ValueError("Environment no válido")

    # Cargar las variables de entorno
    load_dotenv(env_file, verbose=True)

get_env()

DATABASE_HOST=os.getenv("DATABASE_HOST")
DATABASE_PORT=os.getenv("DATABASE_PORT")
DATABASE_USERNAME=os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
DATABASE_NAME=os.getenv("DATABASE_NAME")

REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")

#logging.basicConfig(
#    filename="app.log",
#    level=logging.INFO,
#    format="%(asctime)s - %(levelname)s - %(message)s",
#)

# Configura la conexión a la base de datos PostgreSQL
db_connection = psycopg2.connect(
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    database=DATABASE_NAME
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

celery_app = Celery("taskManager", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0", backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

celery_app.conf.task_default_queue = "converted_queue"

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'  # Reemplaza con tu configuración
db = SQLAlchemy(app)

MATCHING_SERVICE_URL = "http://motor-emparejamiento:6000/matching"
CIRCUIT_BREAKER_STATE = "closed"

CONTEXT_PATH= "/api"
TASKS_PATH= "/tasks"
LOCAL_URL = "http://localhost:9000"

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_uuid = db.Column(db.String, nullable=False)
    source_name = db.Column(db.String(1000))
    source_format = db.Column(db.String(5))
    target_format = db.Column(db.String(5))
    create_datetime = db.Column(db.TIMESTAMP)
    start_convert = db.Column(db.TIMESTAMP)
    end_convert = db.Column(db.TIMESTAMP)
    status = db.Column(db.String(20))
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["GET"])
def getTask(task_id):

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()

    video_folder_path = '/api/tasks/file/'
    in_video_folder_path = video_folder_path
    out_video_folder_path = video_folder_path
    source_unique_filename = task[1] + "." + task[3]
    target_unique_filename = task[1] + "." + task[4]
    target_url = LOCAL_URL + out_video_folder_path + target_unique_filename
    source_url = LOCAL_URL + in_video_folder_path + source_unique_filename

    if task is not None and task[8] != "disponible":
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
        return jsonify(task_dict), 200
    elif task is not None and task[8] == "disponible":
        task_dict = {
            'id': task[0],
            'source_uuid': task[1],
            'source_name': task[2],
            'source_format': task[3],
            'target_format': task[4],
            'create_datetime': task[5],
            'start_convert': task[6],
            'end_convert': task[7],
            'status': task[8],
            'source_url': source_url,
            'target_url': target_url
        }
        return jsonify(task_dict), 200
    else:
        return "Task not found", 404

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["DELETE"])
def deleteTask(task_id):
    try:

        cursor = db_connection.cursor()

        check_query = "SELECT id FROM tasks WHERE id = %s"
        cursor.execute(check_query, (task_id,))
        existing_task = cursor.fetchone()

        if existing_task:
            delete_query = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(delete_query, (task_id,))
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Task eliminado correctamente"}), 200
        else:
            cursor.close()
            return jsonify({"message": "Task NO existe"}), 404

    except Exception as e:
        return jsonify({"message": "Error al eliminar task", "error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    # Verifica si se ha proporcionado el encabezado de autorización
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401

    # Extrae el token del encabezado de autorización
    token = auth_header.split(' ')[1]

    # Verifica el token aquí si es necesario

    # Obtiene el archivo de video desde la solicitud
    video_file = request.files.get('fileName')

    if video_file is None:
        return jsonify({'error': 'No video file provided'}), 400

    # Genera un nombre de archivo único (UUID) con la extensión del archivo original
    file_extension = os.path.splitext(video_file.filename)[-1]
    source_format = file_extension[1:]
    source_uuid = str(uuid.uuid4())
    app.logger.error(f'Info: {source_uuid}')
    unique_filename = source_uuid + file_extension

    target_format = request.form.get('newFormat').lower()

    allowed_formats = {'mp4', 'webm', 'avi', 'mpeg', 'wmv'}

    if source_format == target_format:
        return jsonify({'error': 'Source and target formats cannot be the same'}), 400

    # Valida que los formatos estén en la lista de formatos permitidos
    if source_format not in allowed_formats or target_format not in allowed_formats:
        return jsonify({'error': 'Invalid source or target format'}), 400

    # Ruta donde se almacenarán los archivos de video
    video_folder_path = '/app/video_files'
    source_video_folder_path = video_folder_path + "/in"

    # Asegúrate de que la carpeta de destino exista
    os.makedirs(source_video_folder_path, exist_ok=True)

    # Guarda el archivo en la carpeta de destino con el nombre único
    video_file.save(os.path.join(source_video_folder_path, unique_filename))

    try:
        # Crea una nueva tarea en la base de datos
        new_task = Tasks(
            source_uuid=source_uuid,
            source_name=video_file.filename,
            source_format=source_format.lower(),
            target_format=target_format.lower(),
            create_datetime=datetime.now(),
            status='uploaded'
            #user_id=1
        )

        db.session.add(new_task)
        db.session.commit()

        # GCP PUB SUB Integration
        project_id = "cloud-w3-403103"
        topic_name = "converter-pubsub"

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)

        # Enviar evento a file conversor
        eventData = {
            "uuid": source_uuid,
            "file_path": source_video_folder_path + "/" + unique_filename,
            "file_name": source_uuid + "." + target_format.lower(),
            "format": target_format.lower()
        }

        data = json.dumps(eventData).encode("utf-8")

        publish_data = publisher.publish(topic_path, data)

        celery_app.send_task(
            "app.convert", args=[eventData], queue="task_queue"
        )

        #return jsonify({'message': 'Video uploaded successfully', 'filename': unique_filename}), 200

        return jsonify({
            'message': 'Video uploaded successfully',
            'task_id': new_task.id,
            'source_uuid': source_uuid,
            'source_format': source_format,
            'target_format': target_format
        }), 200

    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Failed to insert data into the database'}), 500

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Failed to upload video: ' + str(e)}), 500

@app.route(CONTEXT_PATH + TASKS_PATH + '/file/<filename>', methods=['GET'])
def download_file(filename):
    in_path = "/app/video_files/in/"
    out_path = "/app/video_files/out/"

    if os.path.exists(out_path + "/" + filename):
        filepath = out_path + "/" + filename
    elif os.path.exists(in_path + "/" + filename):
        filepath = in_path + "/" + filename
    else:
        return jsonify({"message": "Archivo no encontrado"}), 404

    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/octet-stream')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
