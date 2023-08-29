import os
from pathlib import Path


basedir = Path(__file__).parent.parent.parent.absolute()
db_path = str(basedir.joinpath("data/database.db").absolute())


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = 'REPLACE ME - this value is here as a placeholder.'

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FEED_UPLOADS_PER_PAGE = 4*20
