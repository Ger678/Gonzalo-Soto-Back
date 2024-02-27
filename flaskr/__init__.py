from flask import Flask
from flask_mysql_connector import MySQL
from flask_cors import CORS
from config import DB_CONFIG
from flask_jwt_extended import JWTManager

flaskr = Flask(__name__)

mysql = MySQL(flaskr)

jwt = JWTManager(flaskr)

# Configuración de la conexión a la base de datos
flaskr.config['MYSQL_HOST'] = DB_CONFIG['host']
flaskr.config['MYSQL_USER'] = DB_CONFIG['user']
flaskr.config['MYSQL_PASSWORD'] = DB_CONFIG['password']
flaskr.config['MYSQL_DATABASE'] = DB_CONFIG['database']

flaskr.config['JWT_SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esto con una clave segura en un entorno de producción
flaskr.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
flaskr.config['JWT_HEADER_NAME'] = 'Authorization'
flaskr.config['JWT_HEADER_TYPE'] = 'Bearer'
flaskr.config['JWT_BLACKLIST_ENABLED'] = True
flaskr.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# Configuración CORS más específica
CORS(flaskr)


from flaskr import routes