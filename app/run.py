# Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
from flask import Flask
from flask_talisman import Talisman
from app import app

# Importando todos mis Routers (Rutas)
from routers.router_login import *
from routers.router_home import *
from routers.router_page_not_found import *

# Configurando Flask-Talisman con HSTS habilitado
#talisman = Talisman(app, strict_transport_security=True, force_https=True)

app.config['TEMPLATES_AUTO_RELOAD'] = True

# Ejecutando el objeto Flask
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=0)
