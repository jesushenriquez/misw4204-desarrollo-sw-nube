import os
import datetime
import threading

from google.cloud import pubsub_v1
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
import psycopg2
import logging
from flask import Flask
from google.cloud import storage
from io import BytesIO
import tempfile
import threading

logger = logging.getLogger(__name__)

def get_env():
    # Obtener el environment del parámetro del comando
    env = os.getenv("ENV", "local")

    # Cargar el archivo de entorno correspondiente
    if env == "local":
        env_file = ".env"
    elif env == "cloud":
        env_file = ".env.cloud"
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


# Configura la conexión a la base de datos PostgreSQL
db_connection = psycopg2.connect(
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    database=DATABASE_NAME
)

class FileRetriever:
    def __init__(self, path, id):
        self.path = path
        self.id = id

    def get_path(self):
        return self.path

    def get_id(self):
        return self.id

def convertir_video(uuid,input_path, output_path, formato_salida='mp4'):
    try:
        print("Entra a convertir video")
        bucket_name = "video_files_cloud_w3"
        archivo_destino = output_path
        print(f'Video descargado exitosamente')
        startTime = datetime.datetime.now()
        descargar_video(bucket_name, input_path, formato_salida, uuid)
        # convert_video(output_path, formato_salida, video_bytes, input_path, bucket_name)

        print(f'Video convertido exitosamente a {formato_salida}')
        endTime = calc_time(startTime)
        update_task(uuid, startTime, endTime, 'success')
    except Exception as e:
        print(f'Error al convertir el video: {str(e)}')
        update_task(uuid, None, None, 'failure')

def descargar_video(bucket_name, input_path, formato_salida, uuid):

    input_path = input_path.replace("/app/video_files/", "")

    bucket_origen = cliente.bucket(bucket_name)
    print("Obtención del bucket")

    blob_origen = bucket_origen.blob(input_path)
    print("Obtención del blob", blob_origen)

    try:
        video_bytes = BytesIO(blob_origen.download_as_bytes())
        print("Descarga del archivo")
        _, input_extension = os.path.splitext(os.path.basename(input_path))
        # Crear un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=input_extension, delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(video_bytes.getvalue())

        # Convierte el archivo temporal a VideoFileClip
        video_clip = VideoFileClip(temp_filename)
        try:
            # Definir el nombre del archivo de salida en el mismo bucket
            output_filename = f'out/{os.path.basename(uuid)}.{formato_salida}'

            # Subir el archivo convertido al bucket
            with tempfile.NamedTemporaryFile(suffix=f".{formato_salida}", delete=False) as output_temp_file:
                # Realiza la conversión y guarda el resultado
                if formato_salida == 'mp4':
                    video_clip.write_videofile(output_temp_file.name, codec='libx264', audio_codec='aac')
                elif formato_salida == 'webm':
                    video_clip.write_videofile(output_temp_file.name, codec='libvpx', audio_codec='libvorbis')
                elif formato_salida == 'avi':
                    video_clip.write_videofile(output_temp_file.name, codec='libxvid', audio_codec='mp3')
                elif formato_salida == 'mpeg':
                    video_clip.write_videofile(output_temp_file.name, codec='mpeg4', audio_codec='mp3')
                elif formato_salida == 'wmv':
                    video_clip.write_videofile(output_temp_file.name, codec='wmv2', audio_codec='wmav2')
                else:
                    print("Formato de salida no válido.")
                    raise AssertionError("Formato de salida no válido.")
                
                print('output_temp_file.name', output_temp_file.name)
                blob = bucket_origen.blob(output_filename)
                blob.upload_from_filename(output_temp_file.name)

            print(f"Video convertido y almacenado en {output_filename}")
            
        finally:
            # Elimina el archivo temporal después de la conversión
            video_clip.close()
            temp_file.close()
            os.remove(temp_filename)
            os.remove(output_temp_file.name)
        return video_bytes
    except Exception as e:
        print(f"Error al convertir el video: {e}")
        # Puedes manejar el error de manera adecuada (por ejemplo, lograrlo o lanzar una excepción)
        # dependiendo de los requisitos de tu aplicación.
        raise

def update_task(uuid, startTime, endTime, status):
    print(f'Recibiendo evento de actualización')
    # Realiza las operaciones de actualización en la base de datos
    db_cursor = db_connection.cursor()
    try:
        if status == 'success':
            start_convert = startTime
            end_convert = endTime

            # Realiza la actualización en la base de datos
            update_query = "UPDATE tasks SET start_convert = %s, end_convert = %s, status = %s WHERE source_uuid = %s"
            db_cursor.execute(update_query, (start_convert, end_convert, 'disponible', uuid))
        elif status == 'failure':
            # Actualiza el estado a "failed"
            update_query = "UPDATE tasks SET status = %s WHERE source_uuid = %s"
            db_cursor.execute(update_query, ('failed', uuid))
        else:
            raise AssertionError("Invalid status")

        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f'Error: {str(e)}')
    finally:
        db_cursor.close()

def calc_time(startTime):
    endTime = datetime.datetime.now()
    milliseconds = (endTime - startTime).total_seconds() * 1000
    print(f'Tiempo de conversión: {milliseconds} ms')
    return endTime

lock = threading.Lock()

def procesar_mensaje(message):
    try:
        with lock:
            print((f"Procesando mensaje: {message.data}"))

            data = message.data.decode("utf-8")
            # print(f"Mensaje recibido: {data}")
            data_dict = eval(data)  # Asumiendo que el mensaje es un diccionario en forma de cadena
            # print(f"Mensaje recibido: {data_dict}")
            print(f"uuid recibido: {data_dict['uuid']}")
            print(f"file_path recibido: {data_dict['file_path']}")
            convertir_video(data_dict['uuid'], data_dict['file_path'], f'out/{data_dict["file_name"]}',
                            data_dict['format'])
            message.ack()
            lock.release()

    except Exception as e:
        # Si ocurre un error, no confirmar el mensaje y manejar el error (opcional)
        print(f"Error al procesar mensaje: {str(e)}")
        # No confirmar el mensaje para que sea reencolado
        message.nack()

app = Flask(__name__)

@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

def callback(message):
    try:
        print(f"Mensaje recibido: {message.data}")
        procesar_mensaje(message)
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")
    finally:
        message.ack()

def recibir_mensajes(project_id, subscription_name):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Escuchando mensajes en {subscription_path}...")

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Error al recibir mensajes: {e}")
        streaming_pull_future.cancel()

def run():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloud-w3-403103-d05bfab17c67.json"
    project_id = "cloud-w3-403103"
    subscription_name = 'converter-subscription'
    recibir_mensajes(project_id, subscription_name)

if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloud-w3-403103-d05bfab17c67.json"
    project_id = "cloud-w3-403103"
    subscription_name = 'converter-subscription'
    cliente = storage.Client()
    print("Creación del cliente de almacenamiento")
    thread_B = threading.Thread(target = run)
    thread_B.start()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


    