from flask import Flask

app = Flask(__name__)
application = app
app.secret_key = 'CambiarEstoPorUnSecreto'