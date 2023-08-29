from . import db
from . import _Base_Mixin


class YT_Credentials(_Base_Mixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    account_name = db.Column(db.String(100), unique=False, nullable=False)
    credentials = db.Column(db.String(1000), unique=True, nullable=False)

    def __repr__(self):
        return f'<yt_credentials {self.account_name}>'

    ################################################################
    # Class functions
    ################################################################

    @classmethod
    def create(cls, user_id, account_name, credentials):
        obj = super().create( user_id, account_name, credentials)
        db.session.commit()

    @classmethod
    def set(cls, user_id, account_name, credentials):
        obj: YT_Credentials
        if cls.get_num() > 0:
            obj = cls.get_first() #TODO get correct one

            obj.user_id = user_id
            obj.account_name = account_name
            obj.credentials = credentials
            db.session.commit()
        else:
            obj = cls.create(user_id, account_name, credentials)

