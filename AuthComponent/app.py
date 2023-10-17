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

    contrasena = data.get("contrasena")
    nombre_usuario = data.get("nombre_usuario")

    contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

    usuario = search_user(
        data={"nombre_usuario": nombre_usuario, "contrasena": contrasena_encriptada}
    )

    if usuario is None:
        insert_user(data={"nombre_usuario": nombre_usuario, "contrasena": contrasena_encriptada})
        return {"token": __generar_token(user_name=nombre_usuario)}
    else:
        return {"msg": "El usuario ya existe"}, 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    contrasena = data.get("contrasena")
    nombre_usuario = data.get("nombre_usuario")

    contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

    usuario = search_user(
        data={"nombre_usuario": nombre_usuario, "contrasena": contrasena_encriptada}
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
        dbname="security_db", user="admin", password="password", host="postgres"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT * 
                    FROM usuarios 
                    WHERE nombre_usuario = '{data.get("nombre_usuario")}'
                    AND contrasena = '{data.get("contrasena")}';
                """
            )
            result = cur.fetchone()
            return result

def insert_user(data):
    with psycopg2.connect(
        dbname="security_db", user="admin", password="password", host="postgres"
    ) as conn:
        with conn.cursor() as cur:
            result = cur.execute (
                f"""
                    INSERT INTO usuarios (nombre_usuario, contrasena)
                    VALUES ('{data.get("nombre_usuario")}', '{data.get("contrasena")}');
                """
            )
            return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
