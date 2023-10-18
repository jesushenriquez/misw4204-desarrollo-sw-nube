import hashlib
import logging
import psycopg2
from flask_jwt_extended import JWTManager


from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token

from exceptions import UsuarioNoExiste, UsuarioYaExiste


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '43141-123-csdf-1-xcvsdf-12asdf-1234%$'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['JWT_AlGORITHM'] = 'HS256'
jwt_manager = JWTManager(app)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
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
        dbname="cloud_db", user="admin", password="password", host="postgres"
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
        dbname="cloud_db", user="admin", password="password", host="postgres"
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
