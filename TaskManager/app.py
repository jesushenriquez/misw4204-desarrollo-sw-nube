from datetime import datetime
import os
import uuid

from flask import Flask, request, jsonify
import requests
from celery import Celery
import time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

celery_app = Celery("informacionHvBuscadores", broker="redis://redis:6379/0")

app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:password@postgres/cloud_db'  # Reemplaza con tu configuración
db = SQLAlchemy(app)

MATCHING_SERVICE_URL = "http://motor-emparejamiento:6000/matching"
CIRCUIT_BREAKER_STATE = "closed"


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
    return "Hello from informacionHvBuscadores!"


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
    source_uuid = str(uuid.uuid4())
    app.logger.error(f'Info: {source_uuid}')
    unique_filename = source_uuid + file_extension

    # Ruta donde se almacenarán los archivos de video
    video_folder = '/app/video_files'

    # Asegúrate de que la carpeta de destino exista
    os.makedirs(video_folder, exist_ok=True)

    # Guarda el archivo en la carpeta de destino con el nombre único
    video_file.save(os.path.join(video_folder, unique_filename))

    try:
        # Crea una nueva tarea en la base de datos
        new_task = Tasks(
            source_uuid=f"{{{source_uuid}}}",
            source_name=video_file.filename,
            source_format=file_extension,
            target_format=request.form.get('newFormat'),
            create_datetime=datetime.now(),
            status='uploaded'
            #user_id=1
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({'message': 'Video uploaded successfully', 'filename': unique_filename}), 200

    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Failed to insert data into the database'}), 500

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': 'Failed to upload video: ' + str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
