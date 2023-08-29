
from ..extension import db
from ..db_models import Tag, Channel, Upload
from .._data.config import Config


from datetime import datetime
import xmltodict


import asyncio
import aiohttp
import time


"%Y-%m-%dT%H:%M:%S"
YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
OUT_DATE_FORMAT = "%H:%M %d-%m-%Y"


def getUploadList(channel_Data_Raw, channel: Channel):
    channel_Data = xmltodict.parse(channel_Data_Raw)

    channel_Data_Feed = channel_Data["feed"]
    channel_ID = channel_Data_Feed["yt:channelId"]
    channel_Title = channel_Data_Feed["title"]

    uploads = []
    if "entry" in channel_Data_Feed:
        uploads = channel_Data_Feed["entry"]

        if type(uploads) != list:
            uploads = [uploads]

    channel_Uploads = []

    # print()
    # print(type(uploads))
    # print(uploads)

    for upload in uploads:
        videoID = upload["yt:videoId"]
        videoTitle = upload["title"]
        videoUploadTime = upload["published"]
        videoURL = upload["link"]["@href"]

        thumbnailData = upload["media:group"]["media:thumbnail"]
        thumbnailURL = thumbnailData["@url"]
        thumbnail_width = thumbnailData["@width"]
        thumbnail_height = thumbnailData["@height"]
        # rating = upload["media:group"]["media:community"]["media:starRating"]["@average"]

        upload_date = str(videoUploadTime).split("+", 1)[0]
        upload_dateTime = datetime.strptime(upload_date, YT_DATE_FORMAT)

        #####################################################################################################
        upload = Upload.create(yt_id=videoID, channel_id=channel.id,
                               title=videoTitle, thumbnail_url=thumbnailURL, dateTime=upload_dateTime)

        if isinstance(upload, str):
            # print("1", upload)
            pass

        else:
            # print("2", upload)
            channel_Uploads.append(upload)

    return channel_Uploads


async def get(channel: Channel, session):

    url = channel.feed_url

    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            # print("Successfully got url {} with resp of length {}.".format(url, len(resp)))

            # <--- Do filtering here,

            # channel_Data = xmltodict.parse(resp.content)
            uploads = getUploadList(resp, channel)

            # print(uploads)
            return uploads
    except Exception as e:
        print("Unable to get channel {} due to {}.".format(
            channel.name, e.__class__))


async def main(event_loop, channels: list[Channel]):
    async with aiohttp.ClientSession(loop=event_loop) as session:
        ret = await asyncio.gather(*[get(channel, session) for channel in channels])
    # print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))
    # print()
    # print(ret)

    return ret


def loadSubFeed():
    channels = Channel.query.order_by(Channel.id.asc()).all()
    # channels = Channel.query.order_by(Channel.id.asc()).limit(200).all()
    # channels = Channel.get_all()

    start = time.time()

#    event_loop = asyncio.get_event_loop()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    channel_uploads = event_loop.run_until_complete(
        main(event_loop, channels))
    end = time.time()

    # event_loop.stop()

    # with open("subFeed.json", "w", encoding="utf-8") as file:
    #     json.dump(channelUploadList, file, ensure_ascii=False, indent=4)

    db.session.commit()

    end = time.time()

    print()
    print("Took {} seconds to Handle {} channels.".format(
        end - start, len(channels)))

    return channel_uploads


def update_Uploads():
    all_channel_uploads = []
    all_channel_uploads = loadSubFeed()

    # print(temp)
    # with open("upload_feed.json", "w", encoding="utf-8") as f:
    #     json.dump(all_channel_uploads, f,
    #               ensure_ascii=False, indent=4, default=str)

    num_uploads = 0
    for channel_uploads in all_channel_uploads:
        num_uploads += len(channel_uploads)

    # uploads = sorted(uploads, key=lambda d: d['time'], reverse=True)
    # uploads = Upload.query.order_by(Upload.dateTime.desc()).limit(200).all()

    print("Loaded {} uploads".format(num_uploads))
    print()

    return num_uploads

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
                Upload.dateTime < last_upload.dateTime).limit(Config.FEED_UPLOADS_PER_PAGE).all()

    return Upload.query.order_by(Upload.dateTime.desc()).limit(Config.FEED_UPLOADS_PER_PAGE).all()


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

        if len(tagged_uploads) > Config.FEED_UPLOADS_PER_PAGE:
            tagged_uploads = tagged_uploads[:Config.FEED_UPLOADS_PER_PAGE]

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

            if len(untagged_uploads) >= Config.FEED_UPLOADS_PER_PAGE:
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


if __name__ == '__main__':
    loadSubFeed()
