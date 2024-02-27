import mysql.connector
import pandas as pd
import hashlib


conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='German530060+',
    database='app_db'
)

cursor = conexion.cursor()

archivo_csv = 'Listado de comerciante.csv'


columnas_interes = ['Comercio']
# columnas_interes = ['LEGAJO']

datos_afiliados = pd.read_csv(archivo_csv, encoding='utf-8', usecols=columnas_interes)

# datos_afiliados = datos_afiliados.where(pd.notna(datos_afiliados), None)
# datos_afiliados = pd.read_csv(archivo_csv)



# for _, fila in datos_afiliados.iterrows():
#     consulta = """
#         INSERT INTO afiliados (nombre, documento, legajo)
#         VALUES (%s, %s, %s)
#     """
#     valores = (fila['APELLIDO Y NOMBRE'], fila['CUIL'], fila['LEGAJO'])
    
#     cursor.execute(consulta, valores)

# # Confirmar los cambios y cerrar la conexión
# conexion.commit()
# conexion.close()


usuarios_y_constrasenia = []

for _, nombre in datos_afiliados.iterrows():
    usuario = ''.join(e for e in nombre['Comercio'] if e.isalnum()).lower()

    hash_completo = hashlib.sha256(usuario.encode()).hexdigest()
    contraseña = hash_completo[:5]

    usuarios_y_constrasenia.append({"nombre":nombre['Comercio'],"user": usuario, "password":contraseña})

for user in usuarios_y_constrasenia:
    consulta = """
        INSERT INTO comerciantes (nombre, user, password, rol_id)
        VALUES (%s, %s, %s, %s)
    """
    valores = (user['nombre'], user['user'], user['password'], 2)
    
    cursor.execute(consulta, valores)

# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()


# print(usuarios_y_constrasenia)