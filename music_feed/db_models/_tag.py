from . import db
from . import Channel
from._channel_tag import _channel_tag

from sqlalchemy.ext.hybrid import hybrid_property


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(100), nullable=False)

    # channels = db.relationship('Channel', secondary=channel_tag, backref='Tag')
    channels = db.relationship(
        'Channel', secondary=_channel_tag, back_populates='tags')
    # channels:list[Channel]

    def __repr__(self):
        return f'<Tag {self.name}>'

    ################################################################
    # Class functions
    ################################################################

    @classmethod
    def get_all(cls) -> list:
        return Tag.query.all()

    @classmethod
    def get_by_ID(cls, tag_id):
        return Tag.query.filter_by(id=tag_id).first()

    ################################################################
    # Instance functions
    ################################################################

    @hybrid_property
    def num_channels(self) -> int:
        return len(self.channels)

    def toDict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
        }

