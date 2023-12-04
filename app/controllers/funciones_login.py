# Importandopaquetes desde flask
from flask import session, flash
# Importando conexion a BD
from conexion.conexionBD import connectionBD
# Para  validar contraseña
from werkzeug.security import check_password_hash

import re
# Para encriptar contraseña generate_password_hash
from werkzeug.security import generate_password_hash
from datetime import datetime
import traceback

def register_login_log(user_id, accessed_url):
    connection = connectionBD()
    
    if connection:
        try:
            cursor = connection.cursor()
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            query = f"INSERT INTO login_logs (user_id, timestamp, accessed_url) VALUES ({user_id}, '{timestamp}', '{accessed_url}')"
            cursor.execute(query)
            connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al registrar el inicio de sesión: {e}")
            traceback.print_exc()  # Imprime el rastreo de la pila para obtener más detalles sobre el error.
        finally:
            connection.close()

def recibeInsertPaciente(nombre_paciente, apellido_paciente, email_paciente, password_paciente, id_clinico=None):
    respuestaValidar = validarDataRegisterLogin(nombre_paciente, email_paciente, password_paciente)
    if respuestaValidar:
        password_encriptada = generate_password_hash(password_paciente, method='scrypt')
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    # Modificamos la consulta SQL para incluir id_clinico solo si se proporciona
                    if id_clinico is not None:
                        sql = "INSERT INTO users(first_name, last_name, email, password, type_user, id_clinicak) VALUES (%s, %s, %s, %s, 'regular', %s)"
                        valores = (nombre_paciente, apellido_paciente, email_paciente, password_encriptada, id_clinico)
                    else:
                        sql = "INSERT INTO users(first_name, last_name, email, password, type_user) VALUES (%s, %s, %s, %s, 'regular')"
                        valores = (nombre_paciente, apellido_paciente, email_paciente, password_encriptada)

                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert
        except Exception as e:
            print(f"Error en el Insert users: {e}")
            return []
    else:
        return False


# Validando la data del Registros para el login
def validarDataRegisterLogin(name_surname, email_user, pass_user):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM users WHERE email = %s"
                cursor.execute(querySQL, (email_user,))
                userBD = cursor.fetchone()  # Obtener la primera fila de resultados

                if userBD is not None:
                    flash('el registro no fue procesado ya existe la cuenta', 'error')
                    return False
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email_user):
                    flash('el Correo es invalido', 'error')
                    return False
                elif not name_surname or not email_user or not pass_user:
                    flash('por favor llene los campos del formulario.', 'error')
                    return False
                else:
                    # La cuenta no existe y los datos del formulario son válidos, puedo realizar el Insert
                    return True
    except Exception as e:
        print(f"Error en validarDataRegisterLogin : {e}")
        return []


def info_perfil_session():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT first_name, last_name, email FROM users WHERE id = %s"
                cursor.execute(querySQL, (session['id'],))
                info_perfil = cursor.fetchall()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []


def procesar_update_perfil(data_form):
    # Extract data from the data_form dictionary
    user_id = session['id']
    first_name = data_form['first_name']
    last_name = data_form['last_name']
    email = data_form['email']
    pass_actual = data_form['pass_actual']
    new_pass_user = data_form['new_pass_user']
    repetir_pass_user = data_form['repetir_pass_user']

    # Validate required fields
    if not pass_actual or not email:
        return 3

    # Connect to MySQL database
    with connectionBD() as conexion_MySQLdb:
        with conexion_MySQLdb.cursor(dictionary=True) as cursor:
            # Check if the email exists in the database
            querySQL = """SELECT * FROM users WHERE email = %s LIMIT 1"""
            cursor.execute(querySQL, (email,))
            account = cursor.fetchone()

            if account:
                # Verify the entered password matches the user's password
                if check_password_hash(account['password'], pass_actual):
                    # If new_pass_user and repetir_pass_user are empty, update without password change
                    if not new_pass_user or not repetir_pass_user:
                        return updatePefilSinPass(user_id, first_name)

                    # Check if new_pass_user and repetir_pass_user match
                    if new_pass_user != repetir_pass_user:
                        return 2

                    # Update the password and other user details
                    nueva_password = generate_password_hash(new_pass_user, method='scrypt')
                    with connectionBD() as conexion_MySQLdb_update:
                        with conexion_MySQLdb_update.cursor(dictionary=True) as cursor_update:
                            querySQL_update = """
                                UPDATE users
                                SET 
                                    first_name = %s,
                                    last_name = %s,
                                    password = %s
                                WHERE id = %s
                            """
                            params_update = (first_name, last_name, nueva_password, user_id)
                            cursor_update.execute(querySQL_update, params_update)
                            conexion_MySQLdb_update.commit()
                            return cursor_update.rowcount or []
                else:
                    return 1
            else:
                return 0



def updatePefilSinPass(id_user, name_surname):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    UPDATE users
                    SET 
                        name_surname = %s
                    WHERE id = %s
                """
                params = (name_surname, id_user)
                cursor.execute(querySQL, params)
                conexion_MySQLdb.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Ocurrió un error en la funcion updatePefilSinPass: {e}")
        return []


def dataLoginSesion():
    inforLogin = {
        "id": session['id'],
        "name_surname": session['name_surname'],
        "email_user": session['email_user']
    }
    return inforLogin