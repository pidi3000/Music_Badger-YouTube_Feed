from flask import Flask
from flask import Blueprint

blueprint = Blueprint('subfeed', __name__, template_folder='templates')

from . import routes

def init(app: Flask):
    print("init feed")
    app.register_blueprint(blueprint)