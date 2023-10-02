
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
    print("DEBUG START")
    channels: list[Channel] = Channel.query.order_by(Channel.id.asc()).all()
    # channels = Channel.get_all()
    # channels = channels[:100]

    result_ids = []

    num_new_uploads = 0
    start = time.time()

    # start task
    for channel in channels:
        res = update_channel_singel.delay(channel_id=channel.id)
        result_ids.append(res.id)

    print("DEBUG LOOP")
    # wait for all task to finish
    while True:
        all_done = True
        for result_id in result_ids:
            result = AsyncResult(result_id)
            ready = result.ready()

            if not ready:
                all_done = False

            # print(
            #     # f"{result_id} -->"
            #     f"{result_ids.index(result_id)+1} -->"
            #     f"\tready: {ready}"
            #     f"\tsuccessful: {result.successful() if ready else None}"
            #     f"\tvalue: {result.result}"
            #     # f"\tvalue: {result.get() if ready else result.result}"
            #     f"\tstate: {result.state}"
            # )

        if all_done:
            break

        # print()
        time.sleep(0.2)

    for result_id in result_ids:
        result = AsyncResult(result_id)
        result_value = result.get()
        ready = result.ready()

        # print(
        #     f"DEBUG task done, id: {result_id}\tsuccess: {result.successful()}")
        if result.successful():
            num_new_uploads += result_value
        else:
            print(
                f"{result_id}: ready: {ready}"
                f"\tsuccessful: {result.successful() if ready else None}"
                f"\tvalue: {result.get() if ready else result.result}"
                f"\state: {result.state}"
            )

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


@shared_task(ignore_result=False)
def update_channel_singel(channel_id: int):
    # return update_channel_uploads(channel_id=channel_id)
    num_uploads = update_channel_uploads(channel_id=channel_id)
    # num_uploads += 2
    # print(f"channel: {channel_id}, num: {num_uploads}")
    return num_uploads


def update_channel_uploads(channel_id: int):
    channel = Channel.query.filter_by(id=channel_id).first()

    if channel is None:
        raise ValueError(f"Channel does not exist: channel_id: {channel_id}")

    channel: Channel
    resp = requests.get(url=channel.feed_url)

    resp.raise_for_status()

    new_uploads = handle_raw_upload(resp.text, channel_id=channel.id)

    db.session.commit()
    # print(f"channel: {channel_id}, num: {len(new_uploads)}")

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
