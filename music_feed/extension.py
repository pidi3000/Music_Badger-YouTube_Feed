from flask_sqlalchemy import SQLAlchemy

from music_feed.youtube.YouTube_auth import get_authorized_yt_obj

db = SQLAlchemy()

# youtube = get_authorized_yt_obj()