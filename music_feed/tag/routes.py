from . import tag_pages

from ..extension import db
from ..db_models import Tag

from . import _tag_helper

from flask import render_template, request, url_for, redirect


@tag_pages.route('/')
def index():
    tags = Tag.query.all()
    return render_template('tag_index.html', tags=tags)


@tag_pages.route('/<int:tag_id>/')
def tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag.html', tag=tag)


@tag_pages.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']

        tag = Tag(name=name, color=color)

        db.session.add(tag)
        db.session.commit()

        return redirect(url_for('.index'))

    return render_template('tag_create.html')


@tag_pages.route('/<int:tag_id>/edit/', methods=('GET', 'POST'))
def edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']

        tag.name = name
        tag.color = color

        db.session.add(tag)
        db.session.commit()

        return redirect(url_for('.index'))

    return render_template('tag_edit.html', tag=tag)


@tag_pages.post('/<int:tag_id>/delete/')
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    # # first remove all Channel Tags using this tag
    # tagged_channels = tag.channels

    # for channel in tagged_channels:
    #     tag.channels.remove(channel)
    
    db.session.delete(tag)
    db.session.commit()

    return redirect(url_for('.index'))
