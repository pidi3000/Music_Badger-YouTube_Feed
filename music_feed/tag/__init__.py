
from flask import Flask, Blueprint

tag_pages = Blueprint(
    'tag',
    __name__,
    url_prefix="/tags",
    template_folder='templates_tag'
)

from . import routes


def init(app: Flask):
    print("init Tag")
    app.register_blueprint(tag_pages)
