
from celery import shared_task
from celery.result import AsyncResult

import xmltodict
import time
from datetime import datetime

import requests

from ..db_models import Tag, Channel, Upload
from ..extension import db

YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_all_channels():
    channels: list[Channel] = Channel.query.order_by(Channel.id.asc()).all()
    # channels = Channel.get_all()

    channel_ids = []
    for channel in channels:
        channel_ids.append(channel.id)

    NUM_WORKERS = 4
    result_ids = []

    num_new_uploads = 0
    start = time.time()

    channel_groups = [channel_ids[i::NUM_WORKERS] for i in range(NUM_WORKERS)]

    # start task
    for group in channel_groups:
        print("DEBUG")
        result_id = update_channel_group.delay(channel_ids=group)
        result_ids.append(result_id)
        print(f"DEBUG Result id: {result_id}")

        # num_uploads = update_channel_group(channel_ids=group)
        # num_new_uploads += num_uploads

    # wait for task to finish
    while True:
        all_done = True
        for result_id in result_ids:
            result = AsyncResult(result_id)
            ready = result.ready()

            if not ready:
                all_done = False

            print(f"{result_id}: ready: {ready}"
                  f"\tsuccessful: {result.successful() if ready else None}"
                  f"\tvalue: {result.get() if ready else result.result}"
                  )

        if all_done:
            break

        time.sleep(1)

    for result_id in result_ids:
        result = AsyncResult(result_id)
        result_value = result.get()

        print(
            f"DEBUG task done, id: {result_id}\tsuccess: {result.successful()}")
        if result.successful():
            num_new_uploads += result_value

    end = time.time()

    print()
    print("Took {} seconds to Handle {} channels.".format(
        end - start, len(channels)))
    print("Loaded {} uploads".format(num_new_uploads))
    print()

    return num_new_uploads


@shared_task(ignore_result=False)
def update_channel_group(channel_ids: list[int]):
    num_new_uploads = 0

    for channel_id in channel_ids:
        num_uploads = update_channel_uploads(channel_id=channel_id)
        num_new_uploads += num_uploads

    return num_new_uploads


def update_channel_uploads(channel_id: int):
    channel = Channel.query.filter_by(id=channel_id).first()

    if channel is None:
        raise ValueError(f"Channel does not exist: channel_id: {channel_id}")

    channel: Channel
    resp = requests.get(url=channel.feed_url)

    resp.raise_for_status()

    new_uploads = handle_raw_upload(resp.text, channel_id=channel.id)

    db.session.commit()

    return len(new_uploads)


def handle_raw_upload(channel_Data_Raw, channel_id: int):
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
        upload = Upload.create(yt_id=videoID, channel_id=channel_id,
                               title=videoTitle, thumbnail_url=thumbnailURL, dateTime=upload_dateTime)

        if isinstance(upload, str):
            # print("1", upload)
            pass

        else:
            # print("2", upload)
            channel_Uploads.append(upload)

    return channel_Uploads
