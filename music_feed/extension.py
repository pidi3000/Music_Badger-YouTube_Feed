from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from music_feed.youtube.YouTube_auth import get_authorized_yt_obj

db = SQLAlchemy()
migrate = Migrate()

# youtube = get_authorized_yt_obj()