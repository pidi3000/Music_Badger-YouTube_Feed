from . import db
from . import _Base_Mixin
from ..help_functions import get_relative_time, get_time_group

from sqlalchemy import Column, Boolean, String, Integer, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import expression


class Upload(db.Model, _Base_Mixin):
    id = db.Column(db.Integer, primary_key=True)

    yt_id = db.Column(db.String(100),  unique=True, nullable=False)

    channel_id = db.Column(db.Integer, db.ForeignKey(
        'channel.id'), nullable=False)
    channel = db.relationship('Channel', back_populates="uploads")
    # channel = None

    title = db.Column(db.String(200), nullable=False)
    thumbnail_url = db.Column(db.String(200), nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False)

    is_short = db.Column(db.Boolean, nullable=True)
    is_livestream = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<Upload {self.title} {self.yt_id}>'

    ################################################################
    # Class functions
    ################################################################

    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls,
               yt_id: str,
               channel_id: int,
               title: str,
               thumbnail_url: str,
               dateTime: DateTime,
               is_short: bool = None,
               is_livestream: bool = None,
               add_to_session: bool = None,
               check_exists: bool = True):

        if check_exists and cls.is_duplicate(yt_id):
            return "Warning: Upload already in DB: {}".format(title)

        new_upload = Upload(
            yt_id=yt_id,
            channel_id=channel_id,
            title=title,
            thumbnail_url=thumbnail_url,
            dateTime=dateTime,
            is_short=is_short,
            is_livestream=is_livestream
        )

        if add_to_session:
            db.session.add(new_upload)

        return new_upload

    @classmethod
    def is_duplicate(cls, yt_id):
        if Upload.query.filter_by(yt_id=yt_id).first():
            return True

        return False

    ################################################################
    # Instance functions
    ################################################################

    def exists(self) -> bool:
        return self.is_duplicate(self.yt_id)

    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html

    @hybrid_property
    def url(self) -> str:
        return "https://www.youtube.com/watch?v={}".format(self.yt_id)

    @hybrid_property
    def time_relativ(self) -> str:
        return get_relative_time(self.dateTime)

    @hybrid_property
    def time_group(self) -> str:
        return get_time_group(self.dateTime)

    @hybrid_property
    def tags(self) -> str:
        return self.channel.tags

    @hybrid_property
    def color(self) -> str:
        return self.channel.color

    # @hybrid_property
    def has_tag(self, tag_id: int) -> bool:
        for tag in self.tags:
            if tag.id == tag_id:
                return True

        return False

    def toDict(self) -> dict:

        upload_tags = []
        for tag in self.tags:
            upload_tags.append(tag.toDict())

        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,

            "color": self.color,
            "tags": upload_tags,
            "channel": self.channel.toDict(),
            "is_short": self.is_short,
            "is_livestream": self.is_livestream,

            "dateTime": self.dateTime,
            "time_relativ": self.time_relativ,
            "time_group": self.time_group,
        }
