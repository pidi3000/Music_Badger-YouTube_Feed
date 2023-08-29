
from google.oauth2.credentials import Credentials
from ..db_models import YT_Credentials

def save_credentials(credentials: Credentials):
    YT_Credentials.create(None, None, credentials)


def get_credentials():
    return YT_Credentials.get_first()


def delete_credentials(credentials: Credentials):
    YT_Credentials.delete(True)

