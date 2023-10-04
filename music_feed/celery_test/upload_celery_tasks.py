"""testing functions for celery workers
"""

from celery import shared_task
from celery.result import AsyncResult

from google.auth.exceptions import RefreshError

import xmltodict
import json
import pickle as pk


import time
from datetime import datetime

import requests
import flask

from ..db_models import Tag, Channel, Upload
from ..extension import db
from music_feed.youtube import YouTube_auth

# from .run_async import update_all_async

YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_all_channels():
    print("DEBUG START")
    channels: list[Channel] = Channel.query.order_by(Channel.id.asc()).all()
    # channels = Channel.get_all()
    # channels = channels[:100]
    # channels = channels[:1]

    num_new_uploads = None

    try:
        # num_new_uploads = update_uploads_api(channels)
        # num_new_uploads = update_uploads_api_v2(channels)
        # num_new_uploads = update_all_async(channels)
        pass

    except RefreshError as e:
        del flask.session['credentials_MAIN']
        print(e)

    except Exception as e:
        print(e)
        raise

    if num_new_uploads is None:
        print("use RSS")
        num_new_uploads = 0
        pass
        # num_new_uploads = update_uploads_rss(channels)

    return num_new_uploads


##################################################
# YT API method
##################################################
def update_uploads_api(channels: list[Channel]):
    print("DEBUG update wiht API")
    youtube = YouTube_auth.get_authorized_yt_obj()

    if isinstance(youtube, flask.Response):
        raise TypeError("YT not authorized")

    start = time.time()

    num_new_uploads = 0

    for channel in channels:
        playlist_id = ("UU" + channel.yt_id.removeprefix("UC"))

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            playlistId=playlist_id
        )
        response = request.execute()

        # print(f"DEBUG playlist ids: {playlist_id}")
        num_new_uploads += handle_upload_raw_api(
            response, channel.id, channel.name)
        db.session.commit()

    end = time.time()

    print()
    print(
        "Took {} seconds to Handle {} channels. Average per channel: {}".format(
            end - start,
            len(channels),
            (end - start)/len(channels)
        )
    )
    print("Loaded {} uploads".format(num_new_uploads))
    print()

    return num_new_uploads


def update_uploads_api_v2(channels: list[Channel]):
    print("DEBUG update wiht API V2")
    youtube = YouTube_auth.get_authorized_yt_obj()

    if isinstance(youtube, flask.Response):
        raise TypeError("YT not authorized")

    result_ids = []

    num_new_uploads = 0
    start = time.time()

    # start task
    for channel in channels:
        playlist_id = ("UU" + channel.yt_id.removeprefix("UC"))

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            playlistId=playlist_id
        )
        request = pk.dumps(request)
        res = api_request_task.delay(
            request=request,
            channel_id=channel.id,
            channel_name=channel.name
        )
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
    print(
        "Took {} seconds to Handle {} channels. Average per channel: {}".format(
            end - start,
            len(channels),
            (end - start)/len(channels)
        )
    )
    print("Loaded {} uploads".format(num_new_uploads))
    print()

    return num_new_uploads


@shared_task(ignore_result=False)
def api_request_task(request, channel_id, channel_name):
    request = pk.loads(request)

    response = request.execute()

    # print(f"DEBUG playlist ids: {playlist_id}")
    num_new_uploads = handle_upload_raw_api(
        response, channel_id, channel_name)
    db.session.commit()

    return num_new_uploads


def handle_upload_raw_api(channel_Data_Raw, channel_id: int, channel_name: str):
    # with open(f"uploads/{channel_name}.json", "w") as f:
    #     json.dump(channel_Data_Raw, f, indent=4, ensure_ascii=False)

    channel_Uploads = []

    for upload in channel_Data_Raw["items"]:
        videoID = upload["snippet"]["resourceId"]["videoId"]
        videoTitle = upload["snippet"]["title"]
        videoUploadTime: str = upload["snippet"]["publishedAt"]

        thumbnailData: dict = upload["snippet"]["thumbnails"]

        # print(f"{videoID}, {thumbnailData.keys()}")
        thumbnailURL = thumbnailData["high"]["url"]

        videoUploadTime = videoUploadTime.split("Z")[0] + "+00:00"
        upload_dateTime = datetime.fromisoformat(videoUploadTime)

        #####################################################################################################
        upload = Upload.create(yt_id=videoID, channel_id=channel_id,
                               title=videoTitle, thumbnail_url=thumbnailURL, dateTime=upload_dateTime)

        if isinstance(upload, str):
            # print("1", upload)
            pass

        else:
            # print("2", upload)
            channel_Uploads.append(upload)

    return len(channel_Uploads)


##################################################
# RSS feed method
##################################################
def update_uploads_rss(channels: list[Channel]):
    print("DEBUG update wiht RSS")
    result_ids = []

    num_new_uploads = 0
    start = time.time()

    # start task
    for channel in channels:
        res = update_channel_singel.delay(
            channel_id=channel.id
        )
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
def update_channel_singel(channel_id: int):  # yt_credentials: dict):
    # return update_channel_uploads(channel_id=channel_id)

    # YouTube_auth.check_user_yt_autherized()
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

    new_uploads = handle_upload_raw_rss(resp.text, channel_id=channel.id)

    db.session.commit()
    # print(f"channel: {channel_id}, num: {len(new_uploads)}")

    return len(new_uploads)


def handle_upload_raw_rss(channel_Data_Raw, channel_id: int):
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
