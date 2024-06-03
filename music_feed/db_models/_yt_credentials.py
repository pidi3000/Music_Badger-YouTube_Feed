from . import db
from . import _Base_Mixin

from sqlalchemy import Column, Integer, String

import pyyoutube


class YT_Credentials(_Base_Mixin, db.Model):
    __tablename__ = "yt_credentials"
    yt_id = db.Column(db.String(100), primary_key=True)
    yt_name = db.Column(db.String(100), unique=False, nullable=False)

    # this is a `pyyoutube.AccessToken` as a json string
    _oauth_token = db.Column(db.String(10000), unique=True, nullable=False)

    # access_token: Optional[str] = field(default=None)
    # expires_in: Optional[int] = field(default=None)
    # refresh_token: Optional[str] = field(default=None, repr=False)
    # scope: Optional[List[str]] = field(default=None, repr=False)
    # token_type: Optional[str] = field(default=None)
    # expires_at: Optional[float] = field(default=None, repr=False)

    def __repr__(self):
        return f'<yt_credentials {self.yt_name}>'

    ################################################################
    # Class functions
    ################################################################

    @classmethod
    def create(cls, yt_id, yt_name, oauth_token: pyyoutube.AccessToken):
        obj = super().create(
            yt_id=yt_id,
            yt_name=yt_name,
            _oauth_token=oauth_token.to_json()
        )

        return obj

    @classmethod
    def get(cls, yt_id):
        return cls.query.filter_by(yt_id=yt_id).first()

    @classmethod
    def delete(cls, yt_id: str):
        obj = cls.get(yt_id=yt_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False

    ################################################################
    # Properties
    ################################################################

    @property
    def oauth_token(self) -> pyyoutube.AccessToken:
        return pyyoutube.AccessToken.from_json(self._oauth_token)

    @oauth_token.setter
    def oauth_token(self, token: pyyoutube.AccessToken):
        self._oauth_token = token.to_json()
