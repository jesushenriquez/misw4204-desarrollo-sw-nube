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
    id = data.get('id', 1) 
    format = data.get('format', 'mp4')
    creation_date = datetime.datetime.now()
    convertir_video(path, f'video_files/out/{name}', format)
    print("------------------------")
    print(data)
    print("------------------------")
def record(id, path, start_date,end_date, format = 'mp4'):
    with psycopg2.connect(
            dbname="security_db", user="admin", password="password", host="postgres"
    ) as conn:
        """
        

        """
        with conn.cursor() as cur:
            cur.execute(

                """INSERT INTO process_video (video_id, file_path, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s);""",
                (id, path, start_date,end_date, 'success'),
                
            )


class FileRetriever:
    def __init__(self, path, id):
        self.path = path
        self.id = id

    def get_path(self):
        return self.path

    def get_id(self):
        return self.id


def convertir_video(input_path, output_path, formato_salida='mp4'):
    try:
        startTime = datetime.datetime.now()
        video = VideoFileClip(input_path)
        
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
            return

        print(f'Video convertido exitosamente a {formato_salida}')
        endTime = datetime.datetime.now()
        milliseconds = (endTime - startTime).total_seconds() * 1000
        print(f'Tiempo de conversión: {milliseconds} ms')
    except Exception as e:
        print(f'Error al convertir el video: {str(e)}')

if __name__ == '__main__':
    formats = ['mp4', 'webm', 'avi', 'mpeg', 'wmv']
    for format in formats:
        convertir_video('video_files/in/video.mp4', f'video_files/out/video_convertido.{format}', format)