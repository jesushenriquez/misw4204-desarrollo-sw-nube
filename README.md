# Video File Conversor - Grupo 13

Este proyecto permite realizar la conversión de archivos de video desde y hacia los siguientes formatos de video:
* mp4
* webm
* avi
* mpeg
* wmv

### Pre-requisitos
* Docker 4.20.1
* Python 3.9.13

### Ejecución del proyecto en un ambiente local
Para poder ejecutar el proyecto de forma local va a ser necesario que tengas instalado y ejecutando docker desktop y ubicarte desde una terminal al mismo nivel donde se encuentre el archivo docker-compose.yml y ejecutar el siguiente comando:

```
docker-compose up
```
Con esto se ejecutaran todos los componentes del sistema de conversión de archivos de video.

## Construido con:
El sistema esta construido con las siguientes tecnologias:

* Python
* Flask
* Celery
* PostgreSQL
* Redis