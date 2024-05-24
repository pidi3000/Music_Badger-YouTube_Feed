
import flask

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests

from . import blueprint as youtube_auth_pages
from music_feed.config import app_config

import os
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from pathlib import Path


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE_CACHE: Path = None


# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_client_secret_path() -> Path:
    global CLIENT_SECRETS_FILE_CACHE
    if CLIENT_SECRETS_FILE_CACHE is None:
        CLIENT_SECRETS_FILE_CACHE = app_config.yt_config.YT_CLIENT_SECRET_PATH

    return CLIENT_SECRETS_FILE_CACHE

##################################################
# Credential sutff
##################################################


def check_user_yt_autherized():
    return 'credentials_MAIN' in flask.session


def check_yt_credentials():
    if 'credentials_MAIN' not in flask.session:
        return flask.redirect(flask.url_for('authorize'))


def get_yt_credentials():
    return flask.session.get('credentials_MAIN', None)


def del_yt_credentials():
    del flask.session['credentials_MAIN']

##################################################
# other sutff
##################################################


def get_authorized_yt_obj():
    if 'credentials_MAIN' not in flask.session:
        return None, flask.redirect("/authorize")

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials_MAIN'])

    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials_MAIN'] = _credentials_to_dict(credentials)

    return youtube, None


@youtube_auth_pages.route('/authorize')
def authorize():

    if not os.path.isfile(get_client_secret_path()):
        return redirect(url_for('.set_client_secret'))

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        get_client_secret_path(), scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@youtube_auth_pages.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        get_client_secret_path(), scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials_MAIN'] = _credentials_to_dict(credentials)

#   return flask.redirect(flask.url_for('test_api_request'))
    return flask.redirect("/")


def _credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@youtube_auth_pages.route('/revoke')
def revoke():
    if 'credentials_MAIN' not in flask.session:
        return ('You need to <a href="{}">authorize</a> before ' +
                'testing the code to revoke credentials.'.format(flask.url_for(".authorize")))

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials_MAIN'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return ('Credentials successfully revoked.')
    else:
        return ('An error occurred.')


@youtube_auth_pages.route('/clear')
def clear_credentials():
    if 'credentials_MAIN' in flask.session:
        del flask.session['credentials_MAIN']
    return ('Credentials have been cleared.<br><br>')


@youtube_auth_pages.route('/client_secret', methods=['GET', 'POST'])
def set_client_secret():
    # https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/

    UPLOAD_FOLDER = os.path.dirname(__file__)
    ALLOWED_EXTENSIONS = {'txt', 'json'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(UPLOAD_FOLDER, filename))
            file.save(get_client_secret_path())

            return redirect(url_for('.authorize'))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
