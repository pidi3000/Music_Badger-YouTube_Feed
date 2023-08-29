
from flask import Flask, Blueprint

blueprint = Blueprint('channel', __name__, url_prefix="/channels",
                      template_folder='templates_channel')

from . import routes

def init(app: Flask):
    print("init channel")
    app.register_blueprint(blueprint)
