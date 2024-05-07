
from ..extension import db

class _Base_Mixin(object):

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

        return obj

    @classmethod
    def get_all(cls) -> list:
        return cls.query.all()
    
    @classmethod
    def get_first(cls):
        return cls.query.first()
    
    @classmethod
    def get_num(cls) -> int:
        return len(cls.get_all())
    
    @classmethod
    def delete(cls) -> None:
        """Removes object but does not commit to DB unless set"""
        db.session.delete(cls)
        db.session.commit()
    

from ._channel import Channel
from ._tag import Tag
from ._upload import Upload
# from ._yt_credentials import YT_Credentials



# Tutorials
# https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy#step-2-setting-up-database-models-for-a-many-to-many-relationship
# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
