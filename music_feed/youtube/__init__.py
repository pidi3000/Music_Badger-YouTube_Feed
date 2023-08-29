import os
from flask import Flask, Blueprint

blueprint = Blueprint(
    'youtube_auth',
    __name__,
    template_folder='templates_channel'
)


# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
#     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# from . import routes


def init(app: Flask):
    print("init youtube")
    app.register_blueprint(blueprint)
