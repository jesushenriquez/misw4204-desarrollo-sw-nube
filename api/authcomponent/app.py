import hashlib
import logging
import os
import psycopg2
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '43141-123-csdf-1-xcvsdf-12asdf-1234%$'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['JWT_AlGORITHM'] = 'HS256'
jwt_manager = JWTManager(app)

def get_env():
    # Obtener el environment del parámetro del comando
    env = os.getenv("ENV", "development")

    # Cargar el archivo de entorno correspondiente
    if env == "local":
        env_file = "/app/env/.env"
    elif env == "cloud":
        env_file = "/app/env/.env.cloud"
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


#logging.basicConfig(
#    filename="app.log",
#    level=logging.INFO,
#    format="%(asctime)s - %(levelname)s - %(message)s",
#)
@app.route("/")
def hello():
    return "Hello from auth!"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password1 = data.get("password1")
    password2 = data.get("password2")
    email = data.get("email")

    encrypt_password = hashlib.md5(password1.encode('utf-8')).hexdigest()

    usuario = search_user(
        data={"username": username, "password": encrypt_password}
    )

    if usuario is None:
        insert_user(data={"username": username, "password": encrypt_password, "email": email})
        return {"token": __generar_token(user_name=username)}
    else:
        return {"msg": "El usuario ya existe"}, 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    encrypt_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    usuario = search_user(
        data={"username": username, "password": encrypt_password}
    )

    if usuario is None:
        return {"msg": "El usuario no existe"}, 400
    else:
        return {"token": __generar_token(user_name=usuario)}

def __generar_token(user_name: str):
    return create_access_token(identity=user_name)

def search_user(data):
    print("Buscando usuario...")
    with psycopg2.connect(
        dbname=DATABASE_NAME, user=DATABASE_USERNAME, password=DATABASE_PASSWORD, host=DATABASE_HOST
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT * 
                    FROM users 
                    WHERE username = '{data.get("username")}'
                    AND password = '{data.get("password")}';
                """
            )
            result = cur.fetchone()
            return result

def insert_user(data):
    with psycopg2.connect(
        dbname=DATABASE_NAME, user=DATABASE_USERNAME, password=DATABASE_PASSWORD, host=DATABASE_HOST
    ) as conn:
        with conn.cursor() as cur:
            result = cur.execute (
                f"""
                    INSERT INTO users (username, password, email)
                    VALUES ('{data.get("username")}', '{data.get("password")}', '{data.get("email")}');
                """
            )
            return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
