from flask import Flask, request, jsonify, Response
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
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401
    
    try:
        response_tasks = requests.get(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH, json=request.json)
        logging.info("response_tasks:", response_tasks)
        return response_tasks.content, response_tasks.status_code
    except Exception as e:
        logging.error("Error get tasks: %s", e)
        return str(e), 500

@app.route(CONTEXT_PATH + TASKS_PATH, methods=["POST"])
def newTasks():
    # Asegúrate de que se haya proporcionado el encabezado de autorización
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401

    # Extrae el token del encabezado de autorización
    token = auth_header.split(' ')[1]

    # Obtiene el archivo de video desde la solicitud
    video_file = request.files.get('fileName')

    if video_file is None:
        return jsonify({'error': 'No video file provided'}), 400

    # Datos adicionales en el cuerpo de la solicitud
    new_format = request.form.get('newFormat')

    # Define la URL del endpoint de carga de archivos
    UPLOAD_URL = "http://task-manager:5000/api/tasks"

    # Define los datos para la solicitud
    files = {'fileName': (video_file.filename, video_file, 'multipart/form-data')}
    data = {'newFormat': new_format}

    # Define el encabezado de autorización
    headers = {'Authorization': auth_header}

    # Realiza la solicitud POST al endpoint de carga
    response = requests.post(UPLOAD_URL, files=files, data=data, headers=headers)

    if response.status_code == 200:
        return "File uploaded successfully"
    else:
        return "Failed to upload file"

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["GET"])
def getTask(task_id):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401
    try:
        response_task = requests.get(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH + "/" + task_id, json=request.json)
        logging.info("response_task:", response_task)
        return response_task.content, response_task.status_code
    except Exception as e:
        logging.error("Error get tasks: %s", e)
        return str(e), 500
    # return "Hello from" + CONTEXT_PATH + TASKS_PATH

@app.route(CONTEXT_PATH + TASKS_PATH + "/<task_id>", methods=["DELETE"])
def deleteTask(task_id):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401
    try:
        response_task = requests.delete(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH + "/" + task_id, json=request.json)
        logging.info("response_tasks:", response_task)
        return response_task.content, response_task.status_code
    except Exception as e:
        logging.error("Error delete tasks: %s", e)
        return str(e), 500

@app.route(CONTEXT_PATH + TASKS_PATH + '/file/<filename>', methods=['GET'])
def get_file(filename):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401

    try:
        response = requests.get(TASK_SERVICE_URL+ CONTEXT_PATH + TASKS_PATH + "/file" + "/" + filename, json=request.json)

        # Verifica que la solicitud sea exitosa (código de respuesta 200)
        if response.status_code == 200:
            file_content = response.content

            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename={filename}'
            }

            # Devuelve el contenido de la respuesta con las cabeceras adecuadas
            return Response(file_content, headers=headers)
        else:
            response_json = {
                "message" : "Error al descargar el archivo"
            }
            return jsonify(response_json), 404

    except Exception as e:
        logging.error("Error delete tasks: %s", e)
        return str(e), 500


if __name__ == "__main__":
    print("Starting apigateway...")
    app.run(host="0.0.0.0", port=9000)