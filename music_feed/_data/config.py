import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')


class Config:
    SECRET_KEY = 'REPLACE ME - this value is here as a placeholder.'  # os.environ.get('SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    FEED_UPLOADS_PER_PAGE = 4*20

