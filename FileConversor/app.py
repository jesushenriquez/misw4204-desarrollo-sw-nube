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
    path = data.get('file_path')
    name = data.get('file_name')
    id = data.get('id')
    creation_date = datetime.datetime.now()
    print("------------------------")
    print(data)
    print("------------------------")
"""
    with psycopg2.connect(
            dbname="security_db", user="admin", password="password", host="postgres"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
"""
"""                INSERT INTO employer_audit (employer_username, candidate, data_extraction_date, creation_date)
                VALUES (%s, %s, %s, %s);
"""
""",
                (employer_username, candidate, data_extraction_date, creation_date),
            )
"""

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
    except Exception as e:
        print(f'Error al convertir el video: {str(e)}')

if __name__ == '__main__':
    formats = ['mp4', 'webm', 'avi', 'mpeg', 'wmv']
    for format in formats:
        convertir_video('video.mp4', f'video_convertido.{format}', format)