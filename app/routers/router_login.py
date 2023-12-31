
from app import app
from flask import render_template, request, flash, redirect, url_for, session
from routers.router_login import *
# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *

PATH_URL_LOGIN = "public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        _, graph_html = grafica()  # Ignoramos los datos_accesos ya que no se están utilizando
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion(), graph_html=graph_html)
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')



@app.route('/mi-perfil', methods=['GET'])
def perfil():
    url = "/mi-perfil"
    if 'conectado' in session:
        # Obtener el ID de la cuenta desde la sesión
        user_id = session.get('id')

        # Registrar la visualización del perfil en la base de datos 
        register_login_log(user_id, url)

        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session())
    else:
        return redirect(url_for('inicio'))



@app.route('/register-paciente', methods=['GET'])
def cpanelRegisterUser():
    url = "/register-paciente"
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        # No hay un usuario conectado, registrar la visualización de la página
        # Obtener el ID de la cuenta desde la sesión (puede ser None si no hay usuario conectado)
        user_id = session.get('id')

        # Registrar la visualización de la página en la base de datos
        register_login_log(user_id, url)

        return render_template(f'{PATH_URL_LOGIN}/auth_register.html')



# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelResgisterPacienteBD():
    if request.method == 'POST' and 'nombre_paciente' in request.form and 'email_paciente' in request.form:
        nombre_paciente = request.form['nombre_paciente']
        apellido_paciente = request.form['apellido_paciente']
        email_paciente = request.form['email_paciente']
        password_paciente = request.form['password_paciente']

        resultData = recibeInsertPaciente(
            nombre_paciente, apellido_paciente, email_paciente, password_paciente)
        if resultData:
            flash('El paciente ha sido registrado correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('No se pudo registrar al paciente.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Método HTTP incorrecto o datos faltantes en el formulario.', 'error')
        return redirect(url_for('inicio'))

# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil", methods=['POST'])
def actualizarPerfil():
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form)
            if respuesta == 1:
                # Los datos fueron actualizados correctamente
                flash('Los datos fueron actualizados correctamente.', 'success')

                # Obtener el ID de la cuenta desde la sesión
                user_id = session.get('id')

                # Registrar la actualización del perfil en la base de datos 
                url = "/actualizar-datos-perfil"
                register_login_log(user_id, url)

                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash('La contraseña actual es incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 2:
                flash('Ambas claves deben ser iguales, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 3:
                flash('La clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil'))
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'email_user' in request.form and 'pass_user' in request.form:
            email_user = str(request.form['email_user'])
            pass_user = str(request.form['pass_user'])
            
            # Comprobando si existe una cuenta
            conexion_MySQLdb = connectionBD()
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", [email_user])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['password'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['id'] = account['id']
                    session['name_surname'] = f"{account['first_name']} {account['last_name']}"
                    session['email_user'] = account['email']
                    session['type_user'] = account['type_user']  # Agregar el tipo de usuario a la sesión

                    # Registrar el inicio de sesión en la base de datos 
                    url = "/"
                    user_id = account['id']  # Obtener el ID de la cuenta
                    register_login_log(user_id, url)

                    flash('la sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('datos incorrectos por favor revise.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('el usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')



@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Obtener el ID de la cuenta desde la sesión
            user_id = session.get('id')

            # Registrar el cierre de sesión en la base de datos 
            url = "/closed-session"
            register_login_log(user_id, url)

            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email_user', None)

            flash('Tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
