from flaskr import flaskr, mysql
from flask import jsonify, request
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, verify_jwt_in_request


@flaskr.route('/')
def index():
    return '¡Hola desde Flask!'

@flaskr.route('/login', methods=['POST'])
def login():
    datos_inicio_sesion = request.get_json()
    user = datos_inicio_sesion['user']
    password = datos_inicio_sesion['password']


    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM comerciantes WHERE user= %s AND password= %s' , (user, password))
    usuario = cur.fetchone()
    rol_id = usuario[4]
    
    if(rol_id == 1):
        identity = {
            'id': usuario[0],
            'role':'admin'
        }
    else:
        identity={
            'id': usuario[0],
            'role':'comerciante'
        }

    comerciante ={
        'id': usuario[0],
        'nombre':usuario[1],
        'alias':usuario[2]
    }

    print(rol_id)
    cur.close()
    if usuario:
        token_acceso = create_access_token(identity=identity, fresh=True)
        return jsonify(access_token=token_acceso, usuario = comerciante), 200
    else:
        return jsonify({'error': 'Usuario invalido'}), 401
    
@flaskr.route('/refresh', methods=['POST'])
def refresh_token():

    
    refresh_token = create_refresh_token(identity=get_jwt_identity())

    return verify_jwt_in_request(fresh=True)
    # return jsonify(refresh_token=refresh_token), 200


@flaskr.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    usuario_actual = get_jwt_identity()
    # TODO: logic to get user
    return jsonify({'mensaje': 'Perfil obtenido'})

@flaskr.route('/password/<int:id>', methods=['GET'])
@jwt_required()
def get_password(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM comerciantes WHERE id =%s", (id,))  # Ajusta la consulta según tu esquema de base de datos
    password = cur.fetchone()
    cur.close()
    if password:
        return jsonify(password), 200
    else:
        return jsonify({'mensaje': 'Error'}), 404
        
    # print(jsonify(password))
    # Convierte los resultados a un formato JSON y responde

@flaskr.route('/newpassword/<int:id>', methods=['POST'])
@jwt_required()
def newPassword(id):
    json = request.get_json()
    password = json['password']
    print('<<<<<<<<<<', json)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE comerciantes SET password = %s WHERE id = %s;", (password, id))  # Ajusta la consulta según tu esquema de base de datos
    mysql.connection.commit()
    cur.close()
    return jsonify({'message':'Contraseña cambiada con exito'})

@flaskr.route('/afiliados', methods=['GET'])
@jwt_required()
def obtener_afiliados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM afiliados")  # Ajusta la consulta según tu esquema de base de datos
    afiliados = cur.fetchall()
    cur.close()

    print(jsonify(afiliados))

    # Convierte los resultados a un formato JSON y responde
    return jsonify(afiliados)

# Ruta para obtener un usuario por ID
@flaskr.route('/afiliados/<int:id>', methods=['GET'])
def obtener_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM afiliados WHERE legajo = %s", (id,))
    usuario = cur.fetchone()
    cur.close()
    
    if usuario:
        afiliado = {
            'id': usuario[0],
            'nombre': usuario[1],
            'documento': usuario[2],
            'monto_disponible': float(usuario[3]),
            'legajo': usuario[4],
        }
        return jsonify(afiliado)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

# Ruta para obtener comprobantes de comerciantes
@flaskr.route('/comprobantes-comerciante/<int:id>', methods=['GET'])
def obtener_comprobantes(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_transaccion, monto_transaccion, fecha_transaccion, a.nombre, a.documento, a.legajo FROM transacciones INNER JOIN afiliados AS a ON a.id = transacciones.id_afiliado WHERE id_comerciante = %s ORDER BY fecha_transaccion DESC", (id,))
    transacciones = cur.fetchall()
    cur.close()
    
    if transacciones:
        return jsonify(transacciones)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

@flaskr.route('/afiliados/<int:id>/saldo', methods=['GET'])
def saldo(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT monto_disponible FROM afiliados WHERE legajo = %s", (id,))
    usuario = cur.fetchone()
    cur.close()
    
    if usuario:
        afiliado = {
            'id': usuario[0],
            'nombre': usuario[1],
            'documento': usuario[2],
            'monto_disponible': float(usuario[3]),
        }
        return jsonify(afiliado)
    else:
        return jsonify({'mensaje': 'Usuario no encontrado'}), 404

# Ruta para agregar un nuevo usuario
@flaskr.route('/afiliados', methods=['POST'])
def agregar_usuario():
    nuevo_usuario = request.get_json()
    nombre = nuevo_usuario['nombre']
    documento = nuevo_usuario['documento']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO afiliados (nombre, documento) VALUES (%s, %s)", (nombre, documento))
    mysql.connection.commit()
    cur.close()

    return jsonify({'mensaje': 'Usuario agregado correctamente'})

# Ruta para actualizar un usuario por ID
@flaskr.route('/afiliados/<int:id>/saldo', methods=['PUT'])
def actualizar_usuario(id):
    json = request.get_json()
    monto = json['monto']
    id_afiliado = json['id_afiliado']
    id_comerciante = json['id_comerciante']

    cur = mysql.connection.cursor(buffered=True)
    cur.execute("SELECT monto_disponible FROM afiliados WHERE legajo = %s", (id,))
    resultado = cur.fetchone()
    
    if resultado:
        monto_actual = resultado[0]
        nuevo_monto = monto_actual - int(monto)

        cur.execute("INSERT INTO transacciones (id_afiliado, id_comerciante, monto_transaccion) values(%s,%s,%s)", (int(id_afiliado), int(id_comerciante), int(monto)))
        cur.execute("SELECT * FROM transacciones WHERE id_afiliado = %s AND id_comerciante = %s AND monto_transaccion = %s ORDER BY fecha_transaccion DESC;",  (int(id_afiliado), int(id_comerciante), int(monto)))
        transaccion = cur.fetchone()
        print(transaccion)

        if transaccion:
            id_transaccion = transaccion[0]
            cur.execute("UPDATE afiliados SET monto_disponible = %s WHERE legajo = %s ;", (int(nuevo_monto), str(id)))
            print(nuevo_monto, id)
            cur.execute("INSERT INTO cuentas (id_transaccion, id_afiliado, monto, id_comerciante) values(%s,%s,%s,%s);", (id_transaccion, id_afiliado, monto, id_comerciante))

        
            cur.execute("SELECT * FROM transacciones WHERE id_transaccion = %s ;", (int(id_transaccion),))
            trans = cur.fetchone()
            print(id_transaccion, trans)
        mysql.connection.commit()
        cur.close()

        transaccionObject = {
            'id':trans[0],
            'legajo':trans[1],
            'comerciante':trans[2],
            'monto':trans[3],
            'fecha': trans[4],
        }
        
        return jsonify(transaccionObject, 200 )
    else:
        cur.close()
        return jsonify({'mensaje': 'Error en la operacion'}, 401)



# Ruta para eliminar un usuario por ID
@flaskr.route('/afiliados/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM afiliados WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'mensaje': 'Usuario eliminado correctamente'})


@flaskr.route('/comerciantes', methods=['GET'])
@jwt_required()
def obtener_comerciantes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comerciantes")  # Ajusta la consulta según tu esquema de base de datos
    afiliados = cur.fetchall()
    cur.close()

    print(jsonify(afiliados))

    # Convierte los resultados a un formato JSON y responde
    return jsonify(afiliados)

@flaskr.route('/deudas', methods=['GET'])
@jwt_required()
def obtener_deudas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM deudas")  # Ajusta la consulta según tu esquema de base de datos
    deudas = cur.fetchall()
    cur.close()

    # Convierte los resultados a un formato JSON y responde
    return jsonify(deudas)