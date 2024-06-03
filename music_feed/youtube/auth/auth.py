

import flask
import logging
from datetime import datetime

from pathlib import Path
from pyyoutube import Client, AccessToken, PyYouTubeException

from music_feed.config import app_config
from music_feed.db_models import YT_Credentials
from music_feed.youtube.data.channel import get_channel_ID_mine


__all__ = [
    'get_api_client',
    'get_oauth_client',
    'get_client_secret_path',

    'check_client_secret_exists',
    'check_oauth_token_saved',
    'check_oauth_client_works',

    'get_authorization_url',
    'handle_authorization_response',
    "refresh_oauth_token",
    'revoke_access_token',

    'save_oauth_token',
    'load_oauth_token',
    'delete_oauth_token'
]


# ? this stores the users yt channel ID connected to the oauth token
SESSION_NAME_YT_CHANNEL_ID = "yt_channel_id"
# SESSION_NAME_YT_OAUTH_TOKEN = "yt_oauth_token"
SESSION_NAME_YT_OAUTH_STATE = "yt_oauth_state"
YT_OAUTH_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

logger = logging.getLogger(__name__)
# print(__name__)


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

        if app_config.yt_config.YT_ALLOW_CLIENT_FOR_API and check_oauth_token_saved():
            return get_oauth_client()
        else:
            error_msg = f"YT_API_KEY must be set to use API"
            logger.error(error_msg)
            raise KeyError(error_msg)

    cli = Client(api_key=YT_API_KEY)

    return cli


####################################################################################################
# OAUTH client
####################################################################################################
def _get_default_oauth_client(token: AccessToken = None) -> Client:
    cli = Client(
        client_secret_path=get_client_secret_path(),
    )

    cli.DEFAULT_SCOPE = YT_OAUTH_SCOPES
    # cli.DEFAULT_STATE

    if isinstance(token, AccessToken):
        cli.access_token = token.access_token
        cli.refresh_token = token.refresh_token

    return cli


def get_oauth_client() -> Client | None:
    cli = _get_default_oauth_client()

    temp_logger = logger.getChild("get_oauth_client")
    # temp_logger.debug("get oauth client")

    if check_oauth_token_saved():
        token: AccessToken = load_oauth_token()

        temp_logger.debug("get client")
        temp_logger.debug(
            f"\n\n\n{token.access_token=}",
            f"\n{cli.refresh_token=}\n\n"
        )

        cli.access_token = token.access_token
        cli.refresh_token = token.refresh_token

        temp_logger.debug(
            f"\n\n\n{token.access_token=}",
            f"\n{cli.refresh_token=}\n\n"
        )

        temp_logger.debug("DONE")

        return cli

    temp_logger.debug("No outh tokens")

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

def get_authorization_url(needs_consent: bool = False) -> str:
    """
    Returns
        url: Authorize url for user.
    """
    temp_logger = logger.getChild("oauth_flow")

    client = _get_default_oauth_client()

    authorize_url, state = client.get_authorize_url(
        # access_type=`online` or `offline`
        access_type="offline",
        prompt="consent" if needs_consent else None
    )

    flask.session[SESSION_NAME_YT_OAUTH_STATE] = state

    temp_logger.debug(f"STATE: {state}")

    return authorize_url


def handle_authorization_response(response_uri: str) -> flask.Response | None:
    """
    saves the oauth token to the session

    Parameters
    ----------
    response_uri
        str: url of where google redirected to after user authorized service

    Returns
    -------
    flask.Response | None
        target where the application should redirect the user
    """
    temp_logger = logger.getChild("oauth_flow")

    client = _get_default_oauth_client()

    state = flask.session[SESSION_NAME_YT_OAUTH_STATE]

    new_access_token: AccessToken = client.generate_access_token(
        authorization_response=response_uri,
        state=state
    )

    temp_logger.debug(f"STATE: {state}")
    temp_logger.debug(f"new token: \n{new_access_token.to_json(indent=4)}")

    # ?if new token has `refresh token`
    #   save new token, delete old
    # ?else
    #   get channel ID
    # ?  if token found for channel ID
    #       load old token
    #       refresh token
    # ?  else
    #       redirect to oauth flow start with `prompt="consent"`
    #
    #

    # ! get users channel ID and name
    client = _get_default_oauth_client(new_access_token)

    user_yt_id = get_channel_ID_mine(client)

    refresh_token = new_access_token.refresh_token
    if refresh_token is not None and len(refresh_token.strip()) > 10:
        save_oauth_token(new_access_token, user_yt_id)

    else:
        old_token = load_oauth_token(user_yt_id)

        if isinstance(old_token, AccessToken):
            # ! refresh old token, has to save cookie
            print("DEBUG: refresh old token")

            refresh_oauth_token(
                token=old_token
            )

        else:
            # ! redirect to oauth flow start with `prompt="consent"`
            print("DEBUG: redirect to oauth flow start with `prompt='consent'`")

            return flask.redirect(flask.url_for(".authorize", needs_consent=True))


####################################################################################################
# Token web stuff
####################################################################################################
def revoke_access_token() -> bool:
    if check_oauth_token_saved():
        client = _get_default_oauth_client()
        token = load_oauth_token()

        logger.debug(f"Revoke OAuth token: \n{token.to_json(indent=4)}")

        try:
            status = client.revoke_access_token(token=token.access_token)
        except PyYouTubeException as e:
            logger.exception("Token revoke error")
            status = False

        delete_oauth_token()
        return status

    return True


def refresh_oauth_token(token: AccessToken = None, yt_id: str = None):
    print("DEBUG refresh token")

    if token is None:
        token = load_oauth_token(yt_id=yt_id)

        if token is None:
            raise ValueError("no token found")

    if not isinstance(token, AccessToken):
        raise ValueError(f"no access token found,  {token=} - {yt_id=}")

    client = _get_default_oauth_client()

    try:
        print("DEBUG run refresh")
        new_token = client.refresh_access_token(
            refresh_token=token.refresh_token
        )

        token.access_token = new_token.access_token
        token.expires_at = datetime.now().timestamp() + new_token.expires_in

        save_oauth_token(
            yt_oauth_token=token,
            # yt_oauth_token=new_token,
            yt_id=yt_id
        )

    except PyYouTubeException as e:
        print(e)
        raise

    return True


####################################################################################################
# Credential sutff NEW
####################################################################################################
def check_oauth_token_saved() -> bool:
    token = load_oauth_token()
    return isinstance(token, AccessToken)


def _check_oauth_token_valid() -> bool | None:
    token = load_oauth_token()
    if token is None:
        return None
    return datetime.fromtimestamp(token.expires_at) > datetime.now()


def check_oauth_client_works(cli: Client = None) -> bool:
    """Auto creates client if none given
    """

    if cli is None:
        cli = get_oauth_client()

    if cli is None:
        logger.debug(f"oauth client error")
        return False

    logger.debug(f"\n{cli.access_token=}\n{cli.refresh_token=}")
    try:
        test_data = cli.subscriptions.list(
            mine=True
        )
    except PyYouTubeException as e:
        logger.debug(f"\n{cli.access_token=}\n{cli.refresh_token=}")
        logger.exception("OAUTH client doesn't work")
        raise

    return True


##################################################
def save_oauth_token(yt_oauth_token: AccessToken, yt_id: str = None) -> bool:
    if yt_id is None:
        client = _get_default_oauth_client(yt_oauth_token)
        yt_id = get_channel_ID_mine(client)

    YT_Credentials.delete(yt_id=yt_id)

    YT_Credentials.create(
        yt_id=yt_id,
        yt_name="",
        oauth_token=yt_oauth_token
    )

    flask.session[SESSION_NAME_YT_CHANNEL_ID] = yt_id

    logger.debug(f"save OAuth token: \n{yt_oauth_token.to_json(indent=4)}\n\tvalid until: {datetime.fromtimestamp(yt_oauth_token.expires_at)}")


def load_oauth_token(yt_id: str = None) -> AccessToken | None:
    if yt_id is None:
        yt_id = flask.session.get(SESSION_NAME_YT_CHANNEL_ID, None)

    if yt_id is None:
        return None

    yt_oauth_token: YT_Credentials = YT_Credentials.get(yt_id=yt_id)

    if yt_oauth_token is None:
        return None

    oauth_token = yt_oauth_token.oauth_token

    logger.debug(f"load OAuth token: \n{oauth_token.to_json(indent=4)}\n\tvalid until: {datetime.fromtimestamp(oauth_token.expires_at)}")

    return oauth_token


def delete_oauth_token():
    yt_id = flask.session.get(SESSION_NAME_YT_CHANNEL_ID, None)

    YT_Credentials.delete(yt_id=yt_id)

    flask.session.pop(SESSION_NAME_YT_CHANNEL_ID)
