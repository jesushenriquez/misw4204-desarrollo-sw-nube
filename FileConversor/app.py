import os

import psycopg2
import datetime
from celery import Celery
from moviepy.editor import VideoFileClip


app = Celery(
    "fileConversor", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

app.conf.task_default_queue = "task_queue"


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
        send_convert_event(uuid, startTime, endTime)
    except Exception as e:
        print(f'Error al convertir el video: {str(e)}')
        send_convert_event(uuid, None, None, "failure")

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
    eventData = {
            "uuid": uuid,
            "start_convert": startTime,
            "end_convert": endTime,
            "state": state
        }
    app.send_task(
            "app.update_task", args=[eventData], queue="converted_file_queue"
        )

def calc_time(startTime):
    endTime = datetime.datetime.now()
    milliseconds = (endTime - startTime).total_seconds() * 1000
    print(f'Tiempo de conversión: {milliseconds} ms')
    return endTime

if __name__ == '__main__':
    formats = ['mp4', 'webm', 'avi', 'mpeg', 'wmv']
    for format in formats:
        convertir_video('video_files/in/video.mp4', f'video_files/out/video_convertido.{format}', format)