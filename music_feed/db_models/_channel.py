from sqlalchemy.ext.hybrid import hybrid_property
from . import db
from ._channel_tag import _channel_tag


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    yt_id = db.Column(db.String(100),  unique=True, nullable=False)

    profile_img_url = db.Column(db.String(250))

    # yt_link = db.Column(db.String(200), nullable=False)

    # tags = db.relationship('Tag', secondary=channel_tag, backref='Channel')
    tags = db.relationship('Tag', secondary=_channel_tag,
                           back_populates='channels')

    uploads = db.relationship('Upload', back_populates='channel')
    # uploads = db.relationship('Upload', backref='channel')

    def toDict(self, include_tags: bool = False) -> dict:

        channel_dict = {
            "id": self.id,
            "name": self.name,

            "yt_id": self.yt_id,
            "yt_link": self.yt_link,
            "profile_img_url": self.profile_img_url,

            "color": self.color,
        }

        if include_tags:
            # upload_tags = []
            # for tag in self.tags:
            #     upload_tags.append(tag.toDict())

            # channel_dict["tags"] = upload_tags

            channel_dict["tags"] = []
            for tag in self.tags:
                channel_dict["tags"].append(tag.toDict())

        return channel_dict

    def __repr__(self):
        return f'<Channel {self.name} {self.yt_id}>'

    ################################################################
    # Class functions
    ################################################################

    @classmethod
    def get_all(cls):
        return Channel.query.all()

    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls, yt_id, name, profile_img_url):
        if Channel.query.filter_by(yt_id=yt_id).first():
            return "Channel \"{}\" already in DB".format(name)

        new_channel = Channel(yt_id=yt_id, name=name,
                              profile_img_url=profile_img_url)
        db.session.add(new_channel)

        return new_channel

    ################################################################
    # Instance functions
    ################################################################

    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html

    @hybrid_property
    def color(self) -> str:
        return self.tags[0].color if len(self.tags) > 0 else "#ffffff"

    @hybrid_property
    def feed_url(self) -> str:
        return "https://www.youtube.com/feeds/videos.xml?channel_id={}".format(self.yt_id)

    @hybrid_property
    def yt_link(self) -> str:
        return "https://www.youtube.com/channel/" + self.yt_id
