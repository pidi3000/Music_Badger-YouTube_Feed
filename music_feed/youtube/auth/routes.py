
from . import youtube_auth_pages

from music_feed.youtube import auth as YT_Auth

import flask
from flask import flash, request, redirect, url_for

# YT_Auth.check_client_secret_exists
# YT_Auth.


@youtube_auth_pages.route('/authorize')
def authorize():

    if not YT_Auth.check_client_secret_exists():
        return redirect(url_for('.set_client_secret'))

    needs_consent = request.args.get('needs_consent', 'false', str)
    needs_consent = needs_consent.lower() in ['true', '1', 't', 'y', 'yes']

    authorization_url = YT_Auth.get_authorization_url(
        needs_consent=needs_consent
    )

    return flask.redirect(authorization_url)


@youtube_auth_pages.route('/oauth2callback')
def oauth2callback():
    authorization_response = flask.request.url

    print("DEBUG oauth callback")

    redirect = YT_Auth.handle_authorization_response(authorization_response)
    if redirect is not None:
        return redirect

    # TODO redirect back to original site, before being redirected to auth flow
    return flask.redirect("/")


@youtube_auth_pages.route('/revoke')
def revoke():
    if not YT_Auth.check_oauth_token_saved():
        return ('You need to <a href="{}">authorize</a> before ' +
                'testing the code to revoke credentials.'.format(flask.url_for(".authorize")))

    status = YT_Auth.revoke_access_token()

    if status:
        return ('Credentials successfully revoked.')
    else:
        return ('An error occurred.')


@youtube_auth_pages.route('/refresh')
def refresh():
    if not YT_Auth.check_oauth_token_saved():
        return ('You need to <a href="{}">authorize</a> before ' +
                'testing the code to revoke credentials.'.format(flask.url_for(".authorize")))

    status = YT_Auth.refresh_oauth_token()

    if status:
        return ('Credentials successfully refreshed.')
    else:
        return ('An error occurred.')


@youtube_auth_pages.route('/client_secret', methods=['GET', 'POST'])
def set_client_secret():
    # https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/

    if request.method == 'POST':
        return _handle_upload_client_secret_file()

    # reqeust type is "GET", return file upload form
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


def _handle_upload_client_secret_file():
    ALLOWED_EXTENSIONS = {'txt', 'json'}

    def check_is_allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    if not check_is_allowed_file(file.filename):
        print(
            f"File type has to be",
            ' or '.join(f"'{f_type}'" for f_type in ALLOWED_EXTENSIONS)
        )
        return redirect(request.url)

    if file:
        file.save(YT_Auth.get_client_secret_path())

        return redirect(url_for('.authorize'))
