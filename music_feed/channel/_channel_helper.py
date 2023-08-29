
from ..extension import db
from ..db_models import Tag, Channel

from ..youtube import youtube_data as yt_data


###########################################################################################
# Form Handler
###########################################################################################


# TODO remove tags_old use channel.tags instead
def handle_form(channel, form, tags_old):
    name = form['name']
    yt_id = form["yt_id"]

    if len(yt_id) < 1:
        error_msg = "ERROR: no youtube channel ID"
        print(error_msg)
        return error_msg

    # Create new channel entry
    if channel == None:

        # Check yt_id already in DB
        temp = Channel.query.filter_by(yt_id=yt_id).first()

        if temp:
            error_msg = "ERROR: Channel already in DB"
            print(error_msg)
            return error_msg

        channel = Channel()

    channel_data = yt_data.get_channel_data(yt_id)
    # check channel data found / channel ID is valid
    if "error" in channel_data:
        # print(channel_data["error"])
        return channel_data["error"]

    if len(name) < 1:
        name = channel_data["name"]

    # yt_id = channel_data["id"]

    channel.name = name
    # channel.yt_link = yt_link
    channel.yt_id = yt_id
    channel.profile_img_url = channel_data["profile_img_url"]

    db.session.add(channel)
    db.session.commit()

    tags_name = form.getlist("tags")
    tags_new = []

    print(tags_name)

    # turn tag name list to Tag object list
    for tag_name in tags_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        tags_new.append(tag)

    tags_old = set(tags_old)
    tags_new = set(tags_new)

    tags_delete = tags_old - tags_new
    tags_add = tags_new - tags_old

    # print()
    # print()
    # print(form)
    # print()
    # print(tags_name)
    # print(channel.id)
    # print(tags_old)
    # print(tags_new)
    # print()
    # print("Delete")
    # print(tags_delete)
    # print()

    for tag in tags_delete:
        channel.tags.remove(tag)
    #     print(tag)
    #     print(channel_tag)
    #     print()

    # print()
    # print()

    # print("Add")
    # print(tags_add)
    # print()
    for tag in tags_add:
        channel.tags.append(tag)

    #     print(tag)
    #     print(channel_tag)
    #     print()

    # print()
    # print()
    # print()

    db.session.commit()


def handle_form_tags(channel, tags_name: list[str]):

    tags_new = []

    print(tags_name)

    # turn tag name list to Tag object list
    for tag_name in tags_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        tags_new.append(tag)

    tags_old = set(channel.tags)
    tags_new = set(tags_new)

    tags_delete = tags_old - tags_new
    tags_add = tags_new - tags_old

    for tag in tags_delete:
        channel.tags.remove(tag)

    for tag in tags_add:
        channel.tags.append(tag)

    db.session.commit()


###########################################################################################
# Helper Functions
###########################################################################################

def handle_import_channel(request):  # TODO add error handling

    import_source = request.args.get("source")
    print(import_source)

    if import_source == "youtube":
        all_subs = yt_data.get_all_subscriptions()

        print()
        print(len(all_subs))
        print()

        for sub in all_subs:
            new_channel = Channel.create(
                sub["id"], sub["name"], sub["profile_img_url"])

            if isinstance(new_channel, str):
                # print(new_channel)
                pass

        db.session.commit()
        # db.session.rollback()
