from . import db


_channel_tag = db.Table(
    'channel_tag',
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)
