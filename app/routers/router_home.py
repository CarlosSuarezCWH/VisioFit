from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from controllers.funciones_login import *
# Importando cenexión a BD
from controllers.funciones_home import *

PATH_URL = "public/pacientes"


@app.route('/registrar-paciente', methods=['GET'])
def viewFormpaciente():
    url = "/registrar-paciente"
    if 'conectado' in session:
        # Obtener el ID de la cuenta desde la sesión
        user_id = session.get('id')

        # Registrar la visualización de la página en la base de datos
        register_login_log(user_id, url)

        return render_template(f'{PATH_URL}/form_paciente.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-paciente', methods=['POST'])
def formpacientes():
    if 'conectado' in session:
        if 'foto_paciente' in request.files:
            foto_perfil = request.files['foto_paciente']
            resultado = procesar_form_paciente(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_pacientes'))
            else:
                flash('El paciente NO fue registrado.', 'error')
                return render_template(f'{PATH_URL}/form_paciente.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/lista-de-paciente', methods=['GET'])
def lista_pacientes():
    url = "/lista-de-paciente"
    if 'conectado' in session:
        # Obtener el ID de la cuenta desde la sesión
        user_id = session.get('id')

        # Registrar la visualización de la página en la base de datos
        register_login_log(user_id, url)

        return render_template(f'{PATH_URL}/lista_paciente.html', pacientes=sql_lista_pacienteBD())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))



@app.route("/detalles-paciente/", methods=['GET'])
@app.route("/detalles-paciente/<int:idpaciente>", methods=['GET'])
def detallepaciente(idpaciente=None):
    url = f"/detalles-paciente/{idpaciente}"
    if 'conectado' in session:
        # Obtener el ID de la cuenta desde la sesión
        user_id = session.get('id')

        # Registrar la visualización de la página en la base de datos
        register_login_log(user_id, url)

        # Verificamos si el parámetro idpaciente es None o no está presente en la URL
        if idpaciente is None:
            return redirect(url_for('inicio'))
        else:
            detalle_paciente = sql_detalles_pacienteBD(idpaciente) or []
            print(detalle_paciente)
            return render_template(f'{PATH_URL}/detalles_paciente.html', detalle_paciente=detalle_paciente)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))



# Buscadon de pacientes
@app.route("/buscando-paciente", methods=['POST'])
def viewBuscarpacienteBD():
    resultadoBusqueda = buscarpacienteBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_paciente.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-paciente/<int:id>", methods=['GET'])
def viewEditarpaciente(id):
    url = f"/editar-paciente/{id}"
    if 'conectado' in session:
        # Obtener el ID de la cuenta desde la sesión
        user_id = session.get('id')

        # Registrar la visualización de la página en la base de datos
        register_login_log(user_id, url)

        respuestapaciente = buscarpacienteUnico(id)
        if respuestapaciente:
            return render_template(f'{PATH_URL}/form_paciente_update.html', respuestapaciente=respuestapaciente)
        else:
            flash('El paciente no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Recibir formulario para actulizar informacion del paciente
@app.route('/actualizar-paciente', methods=['POST'])
def actualizarpaciente():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_paciente'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


@app.route('/borrar-paciente/<int:id_paciente>', methods=['GET'])
def borrarpaciente(id_paciente ):
    print(id_paciente)
    resp = eliminarpaciente(id_paciente)
    if resp:
        flash('El paciente fue eliminado correctamente', 'success')
        return redirect(url_for('lista_pacientes'))


@app.route("/descargar-informe-pacientes/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/examen-uno")
def examen_uno():
    url = "/examen-uno"
    
    # Aquí puedes definir user_id según tu lógica de sesión
    user_id = session.get('id') if 'conectado' in session else None

    # Registrar la visualización de la página en la base de datos
    register_login_log(user_id, url)

    return render_template('public/examenes/examen_uno.html')

@app.route("/examen-dos")
def examen_dos():
    url = "/examen-dos"
    
    # Aquí puedes definir user_id según tu lógica de sesión
    user_id = session.get('id') if 'conectado' in session else None

    # Registrar la visualización de la página en la base de datos
    register_login_log(user_id, url)

    return render_template('public/examenes/examen_dos.html')   

@app.route("/examen-tres")
def examen_tres():
    url = "/examen-tres"
    
    # Aquí puedes definir user_id según tu lógica de sesión
    user_id = session.get('id') if 'conectado' in session else None

    # Registrar la visualización de la página en la base de datos
    register_login_log(user_id, url)

    return render_template('public/examenes/examen_tres.html')
