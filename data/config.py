import os
from pathlib import Path


data_dir = Path(__file__).parent.absolute()
# basedir = Path(__file__).parent.parent.parent.absolute()
# db_path = str(basedir.joinpath("data/database.db").absolute())


class Config:
    db_path = str(data_dir.joinpath("database.db").absolute())

    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = 'REPLACE ME - this value is here as a placeholder.'

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ssl_path = data_dir.joinpath("ssl").absolute()
    MUSIC_FEED = {
        "FEED_UPLOADS_PER_PAGE": 4*20,

        "SSL_ENABLE": True,
        "SSL_ENFORCE": True,  # if FALSE and ssl cert files not found, run without ssl
        "SSL_CERT_PATH": str(ssl_path.joinpath("cert.pem").absolute()),
        "SSL_KEY_PATH": str(ssl_path.joinpath("key.pem").absolute()),
    }
