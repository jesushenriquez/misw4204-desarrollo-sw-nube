import os

import psycopg2
import datetime
from celery import Celery
from moviepy.editor import VideoFileClip


app = Celery(
    "fileConversor", broker="redis://10.128.0.3:6379/0", backend="redis://10.128.0.3:6379/0"
)

app.conf.task_default_queue = "task_queue"

# Configura la conexión a la base de datos PostgreSQL
db_connection = psycopg2.connect(
    host="10.128.0.3",
    port=5432,
    user="admin",
    password="password",
    database="cloud_db"
)

@app.task
def convert(data):
    path = data.get('file_path', 'video_files/in/video.mp4')
    name = data.get('file_name', 'video.mp4')
    uuid = data.get('uuid', 1)
    format = data.get('format', 'mp4')
    creation_date = datetime.datetime.now()
    convertir_video(uuid,path, f'video_files/out/{name}', format)
    print("------------------------")
    print(data)
    print("------------------------")



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
        out_path = "/app/video_files/out/"
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        startTime = datetime.datetime.now()
        video = VideoFileClip(input_path)
        convert_video(output_path, formato_salida, video)
        print(f'Video convertido exitosamente a {formato_salida}')
        endTime = calc_time(startTime)
        update_task(uuid, startTime, endTime, 'success')
    except Exception as e:
        print(f'Error al convertir el video: {str(e)}')
        update_task(uuid, None, None, 'failure')

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

def convert_video(output_path, formato_salida, video):
    if formato_salida == 'mp4':
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    elif formato_salida == 'webm':
        video.write_videofile(output_path, codec='libvpx', audio_codec='libvorbis')
    elif formato_salida == 'avi':
        video.write_videofile(output_path, codec='libxvid', audio_codec='mp3')
    elif formato_salida == 'mpeg':
        video.write_videofile(output_path, codec='mpeg4', audio_codec='mp3')
    elif formato_salida == 'wmv':
        video.write_videofile(output_path, codec='wmv2', audio_codec='wmav2')
    else:
        print("Formato de salida no válido.")
        AssertionError("Formato de salida no válido.")
        

def send_convert_event(uuid, startTime, endTime,state="success"):
    print(f'Enviando evento de conversión de video: {uuid}')
    eventData = {
            "uuid": uuid,
            "start_convert": startTime,
            "end_convert": endTime,
            "status": state
        }
    app.send_task(
            "celery_app.update_task", args=[eventData], queue="converted_queue"
        )
    print(f'Enviado: {uuid}')

def calc_time(startTime):
    endTime = datetime.datetime.now()
    milliseconds = (endTime - startTime).total_seconds() * 1000
    print(f'Tiempo de conversión: {milliseconds} ms')
    return endTime

if __name__ == '__main__':
    formats = ['mp4', 'webm', 'avi', 'mpeg', 'wmv']
    for format in formats:
        convertir_video('video_files/in/video.mp4', f'video_files/out/video_convertido.{format}', format)