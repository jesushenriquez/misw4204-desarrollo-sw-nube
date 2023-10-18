from flask import Flask, request, jsonify
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

INTEGRITY_MANAGER_SERVICE_URL = "http://integrity-manager:6000/"
INFORMACION_HV_BUSCADOR_URL = "http://informacion-hv-buscadores:5000/"
AUTH_SERVICE_URL = "http://auth-component:8080/"

CONTEXT_PATH= "/api"
AUTH_PATH= "/auth"

@app.route("/")
def hello():
    return "Hello from apigateway v6!"



@app.route("/cifrarinformacion", methods=["POST"])
def cifrarinformacion():
    try:
        jwt_token = request.headers.get('Authorization')
        response = requests.post(
            INTEGRITY_MANAGER_SERVICE_URL + 'cifrarinformacion',
            json=request.json,
            headers={'Authorization': jwt_token}
        )
        logging.info("Información cifrada: %s", response.json())

        if response.status_code == 200:
            if response.text:  # Verificar si la respuesta no está vacía
                data = response.json()
                return jsonify(data), 200
            else:
                logging.error("Respuesta vacía del servicio externo")
                return jsonify({'error': 'Respuesta vacía del servicio externo'}), 500
        else:
            logging.error("Error: %s", response.json())
            return jsonify({'error': 'Error en el servicio de Integrity Manager'}), response.status_code

    except Exception as e:
        logging.error("Error: %s", e)
        return str(e), 500

@app.route("/getsecret", methods=["POST"])
def getsecret():
    try:
        jwt_token = request.headers.get('Authorization')
        response = requests.post(
            INTEGRITY_MANAGER_SERVICE_URL + 'getsecret',
            json=request.json,
            headers={'Authorization': jwt_token}
        )
        logging.info("secret: %s", response.json())

        if response.status_code == 200:
            data = response.json()
            logging.info("Secret: %s", data)
            return jsonify(data), 200
        else:
            logging.error("Error getsecret: %s", response.json())
            return jsonify({'error': 'Error en el servicio de Integrity Manager'}), response.status_code
    except Exception as e:
        logging.error("Error getsecret: %s", e)
        return str(e), 500

@app.route("/getInformacionBuscador", methods=["GET"])
def getInformacionBuscador():
    try:
        jwt_token = request.headers.get('Authorization')
        logging.info("jwt_token:", jwt_token)
        response_info_buscador = requests.get(INFORMACION_HV_BUSCADOR_URL+'getInformacionBuscador')
        logging.info("response_info_buscador:", response_info_buscador)
        response = requests.post(
            INTEGRITY_MANAGER_SERVICE_URL + 'cifrarinformacion',
            json=response_info_buscador.json(),
            headers={'Authorization': jwt_token}
        )
        logging.info("Información cifrada buscador: %s", response)
        response_data = {
            "data": response.text
        }
        return response_data, response.status_code
    except Exception as e:
        logging.error("Error getInformacionBuscador: %s", e)
        return str(e), 500

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

if __name__ == "__main__":
    print("Starting apigateway...")
    app.run(host="0.0.0.0", port=9000)
