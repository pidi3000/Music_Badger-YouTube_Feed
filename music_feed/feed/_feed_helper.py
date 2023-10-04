
from ..db_models import Tag, Channel, Upload
from music_feed.config import app_config



######################################################################################################


def _get_Channels_Tagged_v1(filter_tag_id: int) -> list[Channel]:
    filter_tag: Tag = Tag.get_by_ID(filter_tag_id)

    tagged_channels = []

    if filter_tag:
        tagged_channels = filter_tag.channels

    return tagged_channels


def _get_uploads_before(last_upload_idx: int | None = None) -> list[Upload]:
    if last_upload_idx:
        last_upload = Upload.query.filter_by(id=last_upload_idx).first()

        if last_upload:
            return Upload.query.order_by(Upload.dateTime.desc()).filter(
                Upload.dateTime < last_upload.dateTime).limit(app_config.yt_feed.uploads_per_page).all()

    return Upload.query.order_by(Upload.dateTime.desc()).limit(app_config.yt_feed.uploads_per_page).all()


def _get_Tagged_Uploads_v1(last_upload_idx: int | None = None, filter_tag_id: int | None = None):
    tagged_uploads: list[Upload] = []

    print("filter_tag_id: ", filter_tag_id)

    ################################################################
    # get tagged uploads
    ################################################################
    if filter_tag_id and filter_tag_id > 0:
        print("Get tagged uploads")

        tagged_channels = _get_Channels_Tagged_v1(filter_tag_id)

        # print()
        # print("Num Channels tagged: ", len(tagged_channels))

        for channel in tagged_channels:
            channel_uploads = channel.uploads
            tagged_uploads.extend(channel_uploads)

            # print(channel.name, ": ", len(channel_uploads))

        tagged_uploads.sort(key=lambda x: x.dateTime, reverse=True)

        # print()
        # print("list length: ", len(tagged_uploads))

        ################################################################
        # limit by last_upload_idx
        ################################################################
        if last_upload_idx:
            last_upload: Upload = Upload.query.filter_by(
                id=last_upload_idx).first()

            if last_upload:

                cut_off_idx = 0
                for idx, upload in enumerate(tagged_uploads):
                    if upload.dateTime >= last_upload.dateTime:  # is newer then last upload set
                        cut_off_idx = idx

                cut_off_idx = cut_off_idx + 1
                # print("cut_off_idx: ", cut_off_idx)
                # print("list length: ", len(tagged_uploads))
                if len(tagged_uploads) > cut_off_idx:
                    tagged_uploads = tagged_uploads[cut_off_idx:]
                # print("list length: ", len(tagged_uploads))

        if len(tagged_uploads) > app_config.yt_feed.uploads_per_page:
            tagged_uploads = tagged_uploads[:app_config.yt_feed.uploads_per_page]

        # print("list length: ", len(tagged_uploads))
        # print()
        # print(tagged_uploads[0].dateTime)
        # print(tagged_uploads[1].dateTime)
        # print(tagged_uploads[2].dateTime)
        # print()

        return tagged_uploads

    ################################################################
    # Untagged uploads
    ################################################################
    elif filter_tag_id and filter_tag_id == -2:
        print("Get untagged uploads")

        untagged_uploads = []
        all_uploads = Upload.get_all()

        last_upload = None
        if last_upload_idx:
            last_upload: Upload = Upload.query.filter_by(
                id=last_upload_idx).first()

        for upload in all_uploads:
            if len(upload.tags) == 0:
                if last_upload:
                    if upload.dateTime < last_upload.dateTime:  # is older then last upload set
                        untagged_uploads.append(upload)

                else:
                    untagged_uploads.append(upload)

            if len(untagged_uploads) >= app_config.yt_feed.uploads_per_page:
                break

        return untagged_uploads

    ################################################################
    # No Tag set
    ################################################################
    return _get_uploads_before(last_upload_idx)


def get_Uploads_dict(last_upload_idx: int | None = None, filter_tag_id: int | None = None) -> list[Upload]:
    uploads = _get_Tagged_Uploads_v1(last_upload_idx, filter_tag_id)

    uploads_list = []
    for upload in uploads:
        upload: Upload
        uploads_list.append(upload.toDict())

    return uploads_list


def get_Channels_Tagged_dict(filter_tag_id: int | None = None) -> list[Upload]:

    channels = _get_Channels_Tagged_v1(filter_tag_id)

    channel_list = []
    for channel in channels:
        channel: Channel
        channel_list.append(channel.toDict(include_tags=True))

    return channel_list

