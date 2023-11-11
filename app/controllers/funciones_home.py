
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

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

                sql = "INSERT INTO tbl_paciente (nombre_paciente, apellido_paciente, sexo_paciente, telefono_paciente, email_paciente, profesion_paciente, foto_paciente, salario_paciente) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                # Creando una tupla con los valores del INSERT
                valores = (dataForm['nombre_paciente'], dataForm['apellido_paciente'], dataForm['sexo_paciente'],
                           dataForm['telefono_paciente'], dataForm['email_paciente'], dataForm['profesion_paciente'], result_foto_perfil, salario_entero)
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
                        e.id_paciente,
                        e.nombre_paciente, 
                        e.apellido_paciente,
                        e.salario_paciente,
                        CASE
                            WHEN e.sexo_paciente = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_paciente,
                        e.telefono_paciente, 
                        e.email_paciente,
                        e.profesion_paciente,
                        e.foto_paciente,
                        DATE_FORMAT(e.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro
                    FROM tbl_paciente AS e
                    WHERE id_paciente =%s
                    ORDER BY e.id_paciente DESC
                    """)
                cursor.execute(querySQL, (idpaciente,))
                pacienteBD = cursor.fetchone()
        return pacienteBD
    except Exception as e:
        print(
            f"Errro en la función sql_detalles_pacienteBD: {e}")
        return None


# Funcion paciente Informe (Reporte)
def pacienteReporte():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        e.id_paciente,
                        e.nombre_paciente, 
                        e.apellido_paciente,
                        e.salario_paciente,
                        e.email_paciente,
                        e.telefono_paciente,
                        e.profesion_paciente,
                        DATE_FORMAT(e.fecha_registro, '%d de %b %Y %h:%i %p') AS fecha_registro,
                        CASE
                            WHEN e.sexo_paciente = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_paciente
                    FROM tbl_paciente AS e
                    ORDER BY e.id_paciente DESC
                    """)
                cursor.execute(querySQL,)
                pacienteBD = cursor.fetchall()
        return pacienteBD
    except Exception as e:
        print(
            f"Errro en la función pacienteReporte: {e}")
        return None


def generarReporteExcel():
    datapaciente = pacienteReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("Nombre", "Apellido", "Sexo",
                     "Telefono", "Email", "Profesión", "Salario", "Fecha de Ingreso")

    hoja.append(cabeceraExcel)

    # Formato para números en moneda colombiana y sin decimales
    formato_moneda_colombiana = '#,##0'

    # Agregar los registros a la hoja
    for registro in datapaciente:
        nombre_paciente = registro['nombre_paciente']
        apellido_paciente = registro['apellido_paciente']
        sexo_paciente = registro['sexo_paciente']
        telefono_paciente = registro['telefono_paciente']
        email_paciente = registro['email_paciente']
        profesion_paciente = registro['profesion_paciente']
        salario_paciente = registro['salario_paciente']
        fecha_registro = registro['fecha_registro']

        # Agregar los valores a la hoja
        hoja.append((nombre_paciente, apellido_paciente, sexo_paciente, telefono_paciente, email_paciente, profesion_paciente,
                     salario_paciente, fecha_registro))

        # Itera a través de las filas y aplica el formato a la columna G
        for fila_num in range(2, hoja.max_row + 1):
            columna = 7  # Columna G
            celda = hoja.cell(row=fila_num, column=columna)
            celda.number_format = formato_moneda_colombiana

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_paciente_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
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
                            e.id_paciente,
                            e.nombre_paciente, 
                            e.apellido_paciente,
                            e.sexo_paciente,
                            e.telefono_paciente,
                            e.email_paciente,
                            e.profesion_paciente,
                            e.salario_paciente,
                            e.foto_paciente
                        FROM tbl_paciente AS e
                        WHERE e.id_paciente =%s LIMIT 1
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
                querySQL = "SELECT id, name_surname, email_user, created_user FROM users"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar upaciente
def eliminarpaciente(id_paciente, foto_paciente):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_paciente WHERE id_paciente=%s"
                cursor.execute(querySQL, (id_paciente,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

                if resultado_eliminar:
                    # Eliminadon foto_paciente desde el directorio
                    basepath = path.dirname(__file__)
                    url_File = path.join(
                        basepath, '../static/fotos_paciente', foto_paciente)

                    if path.exists(url_File):
                        remove(url_File)  # Borrar foto desde la carpeta

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