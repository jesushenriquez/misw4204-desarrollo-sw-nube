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

### Endpoints
Los endpoints disponibles en nuestro sistema se pueden encontrar en la documentación del siguiente [link](https://www.postman.com/blue-crescent-52144/workspace/misw4204-desarrollo-de-sw-en-la-nube/collection/10850197-6efc143a-0114-4017-8150-4830a8cbe3db?action=share&creator=30445933)

![image](https://github.com/jesushenriquez/misw4204-desarrollo-sw-nube/assets/124113463/ecd61599-c53c-4a36-ba91-3d287d7648ed)
El link lo redireccionará a la plataforma de Postman.

## Construido con:
El sistema esta construido con las siguientes tecnologias:

* Python
* Flask
* Celery
* PostgreSQL
* Redis
