
from ..extension import db
from ..db_models import Tag, Channel

from . import _channel_helper

import flask
from flask import render_template, request, url_for, redirect, jsonify


from . import blueprint as channel_pages


@channel_pages.route('/')
def index():
    # channels = Channel.get_all()
    channels = Channel.get_all_latest()

    return render_template('channel_index.html', channels=channels, tags=Tag.get_all())


# @channel_pages.route('/v2')
# def index_v2():
#     return render_template('channel_index_v3.html', channels=Channel.get_all(), tags=Tag.get_all())


@channel_pages.route('/<int:channel_id>/')
def channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    return render_template('channel.html', channel=channel)


@channel_pages.route('/create/', methods=('GET', 'POST'))
def create():
    if 'credentials_MAIN' not in flask.session:     # TODO
        return flask.redirect(flask.url_for('youtube_auth.authorize'))

    if request.method == 'POST':
        response = _channel_helper.handle_form(None, request.form, [])

        if response:    # TODO: add error response
            pass

        return redirect(url_for('.index'))

    tags = Tag.query.all()
    return render_template('channel_create.html', tags=tags)


# @channel_pages.route('/import/<string:source>', methods=('GET', 'POST', ))
@channel_pages.route('/import/', methods=('GET', 'POST', ))
def import_channel():
    if 'credentials_MAIN' not in flask.session:
        return flask.redirect(flask.url_for('youtube_auth.authorize'))

    if request.method == 'POST':
        _channel_helper.handle_import_channel(request)

        return redirect(url_for('.index'))

    return render_template('channel_import.html')


@channel_pages.route('/<int:channel_id>/edit/', methods=('GET', 'POST'))
def edit(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    channel_tags = channel.tags

    if request.method == 'POST':
        print(request.form)
        _channel_helper.handle_form(channel, request.form, channel_tags)

        return redirect(url_for('.index'))

    tags = Tag.query.all()
    return render_template('channel_edit.html', channel=channel, tags=tags)


@channel_pages.route('/<int:channel_id>/edit_tags/', methods=('POST',))
def edit_tags(channel_id):
    channel: Channel = Channel.query.get_or_404(channel_id)

    print(request.form)

    _channel_helper.handle_form_tags(channel, request.form.getlist("tags"))

    # http://localhost:5000/channels/v2?filter_tag=-1
    filter_tag = request.args.get("filter_tag")
    print(filter_tag)

    return jsonify(channel.toDict(True))
    # return redirect(url_for('.index', **request.args))


@channel_pages.post('/<int:channel_id>/delete/')
def delete(channel_id):
    channel = Channel.query.get_or_404(channel_id)

    # # first remove all Channel Tags using this channel
    # channel_tags = channel.tags

    # for tag in channel_tags:
    #     channel.tags.remove(tag)

    db.session.delete(channel)
    db.session.commit()

    return redirect(url_for('.index'))

######################################################################################################


@channel_pages.route('/page', methods=('GET', ))
def get_page():
    last_channel_id = request.args.get("last_channel_id", None, int)
    filter_tag_id = request.args.get("filter_tag", None, int)

    print("last_channel_id: ", last_channel_id)
    print("filter_tag_id: ", filter_tag_id)

    channels = _channel_helper.get_Channels_Tagged_dict(
        last_channel_id, filter_tag_id)

    tags = []

    for tag in Tag.get_all():
        tags.append(tag.toDict())

    return jsonify(
        {
            "channels": channels,
            "tags": tags
        }
    )
