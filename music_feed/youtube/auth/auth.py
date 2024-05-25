

import flask
import datetime

from pathlib import Path
from music_feed.config import app_config
from pyyoutube import Client, AccessToken, PyYouTubeException


__all__ = [
    'get_api_client',
    'get_oauth_client',
    'get_client_secret_path',

    'check_client_secret_exists',
    'check_oauth_token_saved',
    'check_oauth_client_works',

    'get_authorization_url',
    'handle_authorization_response',
    'revoke_access_token',

    'save_oauth_token',
    'load_oauth_token',
    'delete_oauth_token'
]


SESSION_NAME_YT_OAUTH_TOKEN = "yt_oauth_token"
SESSION_NAME_YT_OAUTH_STATE = "yt_oauth_state"
YT_OAUTH_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


def get_client_secret_path() -> Path:
    return app_config.yt_config.YT_CLIENT_SECRET_PATH

    # * no data caching needed
    global CLIENT_SECRETS_FILE_CACHE
    if CLIENT_SECRETS_FILE_CACHE is None:
        CLIENT_SECRETS_FILE_CACHE = app_config.yt_config.YT_CLIENT_SECRET_PATH

    return CLIENT_SECRETS_FILE_CACHE


def check_client_secret_exists() -> bool:
    return get_client_secret_path().exists()


####################################################################################################
# New Client
####################################################################################################
def get_api_client() -> Client:
    YT_API_KEY = app_config.yt_config.YT_API_KEY
    if YT_API_KEY is None or len(YT_API_KEY.strip()) < 10:
        raise KeyError(f"YT_API_KEY mus be set to use API")

    cli = Client(api_key=YT_API_KEY)

    return cli


####################################################################################################
# OAUTH client
####################################################################################################
def _get_default_oauth_client() -> Client:
    cli = Client(
        client_secret_path=get_client_secret_path(),
    )

    cli.DEFAULT_SCOPE = YT_OAUTH_SCOPES
    # cli.DEFAULT_STATE

    return cli


def get_oauth_client() -> Client | None:
    cli = _get_default_oauth_client()

    print("DEBUG get oauth client")

    if check_oauth_token_saved():
        token: AccessToken = load_oauth_token()
        
        print("get client")
        print(f"\n\n\n{token.access_token=}\n{cli.refresh_token=}\n\n")
        cli.access_token = token.access_token
        cli.refresh_token = token.refresh_token
        print(f"\n\n\n{cli.access_token=}\n{cli.refresh_token=}\n\n")
        
        print("DONE")

        return cli

    # TODO maybe raise error
    return None


##################################################
# Authroization Flow
##################################################
# auth flow:
# get auth url -> redirect user to url
# user autherizes service -> google redirects to service callback URL
# on callback URL get source url (has info stuff) -> generate acces tokens
# store access and refresh token (in SESSION or DB or FILE)

def get_authorization_url(redirect_uri: str = None) -> str:
    """
    Returns
        url: Authorize url for user.
    """

    client = _get_default_oauth_client()

    authorize_url, state = client.get_authorize_url(
        # access_type=`online` or `offline`
        access_type="offline"
    )

    flask.session[SESSION_NAME_YT_OAUTH_STATE] = state

    print()
    print("DEBUG oauth STATE: ", state)
    print()

    return authorize_url


def handle_authorization_response(response_uri: str):
    """
    saves the oauth token to the session

    Parameters
    ----------
    authorization_response
        str: url of where google redirected to after user authorized service

    """

    client = _get_default_oauth_client()

    state = flask.session[SESSION_NAME_YT_OAUTH_STATE]

    access_token: AccessToken = client.generate_access_token(
        authorization_response=response_uri,
        state=state
    )
    

    print()
    print("DEBUG oauth STATE: ", state)
    print()
    
    print(f"DEBUG new token \n{access_token.to_json(indent=4)}")

    save_oauth_token(access_token)


def revoke_access_token() -> bool:
    if check_oauth_token_saved():
        client = _get_default_oauth_client()
        token = load_oauth_token()

        print()
        print("DEBUG OAuth token: ", token, type(token))
        print("DEBUG OAuth token: ", token.access_token,
              type(token.access_token))
        print()
        print()

        try:
            status = client.revoke_access_token(token=token.access_token)
        except PyYouTubeException as e:
            print(e)
            status = False

        delete_oauth_token()
        return status

    return True


####################################################################################################
# Credential sutff NEW
####################################################################################################
def check_oauth_token_saved() -> bool:
    print("DEBUG check token saved")

    token = load_oauth_token()
    return isinstance(token, AccessToken)


def _check_oauth_token_valid() -> bool:
    #! not sure the `token.expires_at` parameter is set,
    #! needs testing
    token = load_oauth_token()
    return datetime.datetime.fromtimestamp(token.expires_at) > datetime.datetime.now()
    # return YT_OAUTH_TOKEN_SESSION_NAME in flask.session


def check_oauth_client_works(cli: Client = None) -> bool:
    """Auto creates client of none given
    """

    if cli is None:
        cli = get_oauth_client()

    if cli is None:
        print("DEBUG oauth client error")
        return False

    print(f"\n\n\n{cli.access_token=}\n{cli.refresh_token=}\n\n")
    try:
        test_data = cli.subscriptions.list(
            mine=True
        )
    except PyYouTubeException as e:
        print(f"\n\n\n{cli.access_token=}\n{cli.refresh_token=}\n\n")
        raise
        print(e)
        return False

    return True


##################################################
def save_oauth_token(yt_oauth_token: AccessToken) -> bool:
    flask.session[SESSION_NAME_YT_OAUTH_TOKEN] = yt_oauth_token.to_json()

    print(f"DEBUG: save token: \n{yt_oauth_token.to_json(indent=4)}")


def load_oauth_token() -> AccessToken | None:
    token_string = flask.session.get(SESSION_NAME_YT_OAUTH_TOKEN, None)

    # print(f"DEBUG: load token: \n{token_string}")

    if token_string is None:
        return None

    yt_oauth_token = AccessToken.from_json(token_string)

    print(f"\nDEBUG: load token: \n{yt_oauth_token.to_json(indent=4)}\n\n")
    return yt_oauth_token


def delete_oauth_token():
    flask.session.pop(SESSION_NAME_YT_OAUTH_TOKEN)
