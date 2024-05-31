import flask
from flask import jsonify, render_template, request, redirect, url_for

from . import blueprint as sub_feed_pages
from ._feed_helper import get_Uploads_dict, get_Channels_Tagged_dict
from ..db_models import Tag
from ..help_functions import get_int_or_none

from music_feed.youtube import auth as YT_auth
from music_feed.youtube import data as YT_data


def _get_url_filter_parameters(request) -> tuple[int | None, int | None]:
    last_upload_idx = get_int_or_none(request.args.get("last_upload_idx"))
    filter_tag_id = get_int_or_none(request.args.get("filter_tag"))

    print("last_upload_idx: ", last_upload_idx)
    print("filter_tag_id: ", filter_tag_id)

    return last_upload_idx, filter_tag_id


@sub_feed_pages.route('/subFeed')
def index():
    last_upload_idx, filter_tag_id = _get_url_filter_parameters(request)

    uploads = (get_Uploads_dict(filter_tag_id=filter_tag_id))
    tags = Tag.query.all()

    return render_template('sub_feed.html', tags=tags, uploads=uploads, yt_autherized=YT_auth.check_oauth_token_saved())


@sub_feed_pages.route('/uploads', methods=('GET', ))
def uploads():
    last_upload_idx, filter_tag_id = _get_url_filter_parameters(request)

    return jsonify(get_Uploads_dict(last_upload_idx, filter_tag_id))


@sub_feed_pages.route('/update', methods=('GET', ))
def update():
    num_uploads = YT_data.update_Uploads()

    response = {
        "response": "True" if num_uploads > 0 else "False"
    }
    return jsonify(response)


@sub_feed_pages.route('/channels_tagged', methods=('GET', ))
def channels_tagged():
    last_upload_idx, filter_tag_id = _get_url_filter_parameters(request)

    return jsonify(get_Channels_Tagged_dict(filter_tag_id))
