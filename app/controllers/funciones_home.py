import base64
import matplotlib.pyplot as plt
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os
import io
from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file


def procesar_form_paciente(dataForm, foto_perfil):
    result_foto_perfil = procesar_imagen_perfil(foto_perfil)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:

                sql = "INSERT INTO users (nombre_paciente, apellido_paciente, sexo_paciente, email_paciente, foto_paciente) VALUES (%s, %s, %s, %s, %s)"

                # Creando una tupla con los valores del INSERT
                valores = (dataForm['nombre_paciente'], dataForm['apellido_paciente'], dataForm['sexo_paciente'],
                           dataForm['telefono_paciente'], dataForm['email_paciente'], dataForm['profesion_paciente'], result_foto_perfil)
                cursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = cursor.rowcount
                return resultado_insert
    except Exception as e:
        return f'Se produjo un error en procesar_form_paciente: {str(e)}'


def procesar_imagen_perfil(foto):
    try:
        # Nombre original del archivo
        filename = secure_filename(foto.filename)
        extension = os.path.splitext(filename)[1]

        # Creando un string de 50 caracteres
        nuevoNameFile = (uuid.uuid4().hex + uuid.uuid4().hex)[:100]
        nombreFile = nuevoNameFile + extension

        # Construir la ruta completa de subida del archivo
        basepath = os.path.abspath(os.path.dirname(__file__))
        upload_dir = os.path.join(basepath, f'../static/fotos_paciente/')

        # Validar si existe la ruta y crearla si no existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            # Dando permiso a la carpeta
            os.chmod(upload_dir, 0o755)

        # Construir la ruta completa de subida del archivo
        upload_path = os.path.join(upload_dir, nombreFile)
        foto.save(upload_path)

        return nombreFile

    except Exception as e:
        print("Error al procesar archivo:", e)
        return []


# Lista de paciente
def sql_lista_pacienteBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = (f"""
                    SELECT 
                        id,
                        first_name, 
                        last_name,
                        email
                    FROM users where type_user='regular'
                    """)
                cursor.execute(querySQL,)
                pacienteBD = cursor.fetchall()
                print(pacienteBD)
        return pacienteBD
    except Exception as e:
        print(
            f"Errro en la función sql_lista_pacienteBD: {e}")
        return None


# Detalles del paciente
def sql_detalles_pacienteBD(idpaciente):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        id,
                        first_name,
                        last_name,
                        email,
                        password,
                        type_user,
                        created_at,
                        updated_at,
                        photo
                    FROM users
                    WHERE id = %s;
                    """)
                cursor.execute(querySQL, (idpaciente,))
                pacienteBD = cursor.fetchone()
                #print (pacienteBD)
        return pacienteBD
    except Exception as e:
        print(
            f"Errro en la función sql_detalles_pacienteBD: {e}")
        return None

#generar grafica
def grafica():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        DATE(l.timestamp) as fecha,
                        COUNT(*) as cantidad_accesos
                    FROM users as u
                    LEFT JOIN login_logs as l ON u.id = l.user_id
                    WHERE l.accessed_url LIKE '%examen%'
                    GROUP BY fecha
                    ORDER BY fecha
                """
                cursor.execute(querySQL,)
                datos_accesos = cursor.fetchall()

        if datos_accesos:
            # Extraer fechas y cantidades
            fechas = [registro['fecha'] for registro in datos_accesos]
            cantidades = [registro['cantidad_accesos'] for registro in datos_accesos]
            # Ajustar el tamaño de la gráfica
            plt.figure(figsize=(4, 4))
            # Crear la gráfica
            plt.plot(fechas, cantidades, linestyle='-', marker='o', label='Accesos')

            # Personalizar título y etiquetas
            plt.title('Accesos por Fecha', fontsize=7, fontweight='bold')
            plt.xlabel('Fecha', fontsize=7)
            #plt.ylabel('Cantidad de Accesos', fontsize=7)

            # Rotar las etiquetas del eje x para mayor claridad
            plt.xticks(rotation=45, ha='right', fontsize=7)

            # Añadir leyenda
            plt.legend(loc='upper left', fontsize=7)

            # Guardar la gráfica en formato PNG
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()

            # Devolver el código HTML para incrustar la gráfica
            graph_html = f'<img src="data:image/png;base64,{image_base64}" alt="Gráfica de Accesos">'
            return datos_accesos, graph_html
        else:
            return datos_accesos, None
    except Exception as e:
        print(f"Error en la función grafica: {e}")
        return None, None



# Funcion paciente Informe (Reporte)
def pacienteReporte():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        u.first_name as nombre_paciente,
                        u.last_name as apellido_paciente,
                        u.email as email_paciente,
                        u.created_at as fecha_registro,
                        u.type_user,
                        l.accessed_url,
                        l.timestamp
                    FROM users as u
                    LEFT JOIN login_logs as l ON u.id = l.user_id
                    WHERE l.accessed_url LIKE '%examen%'
                    ORDER BY u.id DESC
                    """)
                cursor.execute(querySQL,)
                usuarios = cursor.fetchall()
        return usuarios
    except Exception as e:
        print(f"Error en la función obtener_datos_usuarios: {e}")
        return None

def generarReporteExcel():
    datos_usuarios = pacienteReporte()
    
    if not datos_usuarios:
        # Manejar el caso en el que no se obtengan datos de usuarios
        return "No hay datos para generar el informe."

    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("Nombre", "Apellido", "Email", "Fecha de Ingreso", "Tipo de Usuario", "Acceso URL", "Fecha de Acceso")

    hoja.append(cabeceraExcel)

    # Agregar los registros a la hoja
    for registro in datos_usuarios:
        nombre_paciente = registro['nombre_paciente']
        apellido_paciente = registro['apellido_paciente']
        email_paciente = registro['email_paciente']
        fecha_registro = registro['fecha_registro']
        tipo_usuario = registro['type_user']
        accessed_url = registro['accessed_url']
        timestamp = registro['timestamp']

        # Agregar los valores a la hoja
        hoja.append((nombre_paciente, apellido_paciente, email_paciente, fecha_registro, tipo_usuario, accessed_url, timestamp))

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_usuarios_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "static/downloads-excel"  # Ruta relativa a la carpeta del proyecto
    ruta_descarga = os.path.join(os.path.dirname(os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)



def buscarpacienteBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            e.id_paciente,
                            e.nombre_paciente, 
                            e.apellido_paciente,
                            e.salario_paciente,
                            CASE
                                WHEN e.sexo_paciente = 1 THEN 'Masculino'
                                ELSE 'Femenino'
                            END AS sexo_paciente
                        FROM tbl_paciente AS e
                        WHERE e.nombre_paciente LIKE %s 
                        ORDER BY e.id_paciente DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarpacienteBD: {e}")
        return []


def buscarpacienteUnico(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            id,
                            first_name,
                            last_name,
                            email,
                            password,
                            type_user,
                            created_at,
                            updated_at,
                            photo
                        FROM users AS e
                        WHERE id =%s LIMIT 1
                    """)
                mycursor.execute(querySQL, (id,))
                paciente = mycursor.fetchone()
                return paciente

    except Exception as e:
        print(f"Ocurrió un error en def buscarpacienteUnico: {e}")
        return []


def procesar_actualizacion_form(data):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                nombre_paciente = data.form['nombre_paciente']
                apellido_paciente = data.form['apellido_paciente']
                sexo_paciente = data.form['sexo_paciente']
                telefono_paciente = data.form['telefono_paciente']
                email_paciente = data.form['email_paciente']
                profesion_paciente = data.form['profesion_paciente']

                salario_sin_puntos = re.sub(
                    '[^0-9]+', '', data.form['salario_paciente'])
                salario_paciente = int(salario_sin_puntos)
                id_paciente = data.form['id_paciente']

                if data.files['foto_paciente']:
                    file = data.files['foto_paciente']
                    fotoForm = procesar_imagen_perfil(file)

                    querySQL = """
                        UPDATE tbl_paciente
                        SET 
                            nombre_paciente = %s,
                            apellido_paciente = %s,
                            sexo_paciente = %s,
                            telefono_paciente = %s,
                            email_paciente = %s,
                            profesion_paciente = %s,
                            salario_paciente = %s,
                            foto_paciente = %s
                        WHERE id_paciente = %s
                    """
                    values = (nombre_paciente, apellido_paciente, sexo_paciente,
                              telefono_paciente, email_paciente, profesion_paciente,
                              salario_paciente, fotoForm, id_paciente)
                else:
                    querySQL = """
                        UPDATE tbl_paciente
                        SET 
                            nombre_paciente = %s,
                            apellido_paciente = %s,
                            sexo_paciente = %s,
                            telefono_paciente = %s,
                            email_paciente = %s,
                            profesion_paciente = %s,
                            salario_paciente = %s
                        WHERE id_paciente = %s
                    """
                    values = (nombre_paciente, apellido_paciente, sexo_paciente,
                              telefono_paciente, email_paciente, profesion_paciente,
                              salario_paciente, id_paciente)

                cursor.execute(querySQL, values)
                conexion_MySQLdb.commit()

        return cursor.rowcount or []
    except Exception as e:
        print(f"Ocurrió un error en procesar_actualizacion_form: {e}")
        return None


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, first_name, email, created_at FROM users where type_user='admin'"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar upaciente
def eliminarpaciente(id_paciente):
    print(id_paciente)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id_paciente,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        print(cursor.rowcount)
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarpaciente : {e}")
        return []



# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []