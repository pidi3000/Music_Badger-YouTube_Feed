import aiohttp
import asyncio

import flask
import requests

import xmltodict
import json

import time
from datetime import datetime

from music_feed.db_models import Upload, Channel
from music_feed.extension import db
from music_feed.youtube import YouTube_auth
from music_feed.config import app_config

YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

##################################################
# Ideas Speeding up data loading:
# * seems faster so far
# TODO needs to be tested with YT api
# 1: create upload, but don't run db.session.add. Return the uploads and add all uploads to DB at the same time

# ! not really good, cause I need them RIGHT after this is done
# 2: only extract the data and set upload creation and stuff to celery
# 2.1: all in one celery task
# 2.2: each upload runs in it's own task
# 2.3: group uploads, like 10 or something. (reduces the db.commit calls)
##################################################

cookies = {
    "SOCS": "XXXXXXXXXXX"
}

##################################################
# YT API method
##################################################


async def _update_channel_api_old(session, channel: Channel, youtube):
    # print("DEBUG update wiht API")

    playlist_id = ("UU" + channel.yt_id.removeprefix("UC"))

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=playlist_id
    )
    response = request.execute()

    # print(f"DEBUG playlist ids: {playlist_id}")
    num_uploads = _handle_upload_raw_api(
        response, channel.id, channel.name)
    # db.session.commit()

    erros = None
    return {"num_uploads": num_uploads, "errors": erros}


async def _update_channel_api(session, channel: Channel):
    YT_API_KEY = app_config.yt_feed.YT_API_KEY
    if YT_API_KEY is None or len(YT_API_KEY.strip()) < 10:
        raise KeyError(f"YT_API_KEY mus be set to use API")

    playlist_id = ("UU" + channel.yt_id.removeprefix("UC"))
    num_uploads = 0
    channel_Uploads = []

    # Make an asynchronous request to the YouTube API
    async with session.get(
        "https://www.googleapis.com/youtube/v3/playlistItems",
        params={
            "part": "snippet,contentDetails",
            "maxResults": 50,
            "playlistId": playlist_id,
            "key": YT_API_KEY  # Replace with your API key app_config
        },
    ) as response:
        if response.status == 200:
            data = await response.json()
            num_uploads, channel_Uploads = _handle_upload_raw_api(
                data, channel.id, channel.name)
            errors = None
        else:
            # errors = f"Error: {response.status} - {await response.text()}"
            errors = await response.json()
            errors["status"] = response.status

            errors["channel.name"] = channel.name
            errors["playlist_id"] = playlist_id

        return {
            "num_uploads": num_uploads,
            "uploads": channel_Uploads,
            "rss_errors": None,
            "api_errors": errors,
        }


def _handle_upload_raw_api(channel_Data_Raw, channel_id: int, channel_name: str):
    with open(f"data_dev/uploads/{channel_name}.json", "w") as f:
        json.dump(channel_Data_Raw, f, indent=4, ensure_ascii=False)

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

        is_short = _check_video_is_short(video_ID=videoID)

        #####################################################################################################
        upload = Upload.create(
            yt_id=videoID,
            channel_id=channel_id,
            title=videoTitle,
            thumbnail_url=thumbnailURL,
            dateTime=upload_dateTime,
            is_short=is_short,
            add_to_session=False
        )

        if isinstance(upload, Upload):
            channel_Uploads.append(upload)

    return len(channel_Uploads), channel_Uploads


##################################################
# RSS method
##################################################
async def _update_channel_rss(session: aiohttp.ClientSession, channel: Channel):
    url = channel.feed_url
    num_uploads = 0
    channel_Uploads = []

    async with session.get(url) as response:
        # response.raise_for_status()
        if response.status == 200:
            data = await response.text()
            num_uploads, channel_Uploads = await _handle_upload_raw_rss(
                data, channel_id=channel.id, session=session)
            errors = None
        else:
            # errors = f"Error: {response.status} - {await response.text()}"
            errors = {}
            errors["text"] = await response.text()
            errors["status"] = response.status

            errors["channel.name"] = channel.name

        return {
            "num_uploads": num_uploads,
            "uploads": channel_Uploads,
            "rss_errors": errors,
            "api_errors": None

        }


async def _handle_upload_raw_rss(channel_Data_Raw, channel_id: int, session: aiohttp.ClientSession):
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

        # print(f"checking is short: {channel_Title} - {videoID}")
        is_short = await _check_video_is_short_rss(video_ID=videoID, session=session)

        #####################################################################################################
        upload = Upload.create(
            yt_id=videoID,
            channel_id=channel_id,
            title=videoTitle,
            thumbnail_url=thumbnailURL,
            dateTime=upload_dateTime,
            is_short=is_short,
            add_to_session=False
        )

        if isinstance(upload, Upload):
            channel_Uploads.append(upload)

    return len(channel_Uploads), channel_Uploads


##################################################
# Async stuff
##################################################
async def _check_video_is_short_rss(video_ID: str, session: aiohttp.ClientSession) -> bool:
    url = 'https://www.youtube.com/shorts/' + video_ID
    async with session.head(url) as response:
        # response.raise_for_status()
        return response.status == 200


def _check_video_is_short(video_ID: str):
    url = 'https://www.youtube.com/shorts/' + video_ID
    ret = requests.head(url)
    # whether 303 or other values, it's not short
    return ret.status_code == 200


async def _update_channel(session, channel: Channel):
    print(f"starting channel: {channel.name}")
    data = {}
    api_errors = None

    if app_config.yt_feed.use_api:

        try:
            pass
            data = await _update_channel_api(session, channel)

            # no errors
            if not (data["api_errors"] is not None and len(data["api_errors"]) > 0):
                print(f"finnished channel: {channel.name}")
                return data

            api_errors = data["api_errors"]
        except Exception as e:
            api_errors = str(e)
        # print("DEBUG API had error, using RSS")

    # config use_api is false or api had error
    data = await _update_channel_rss(session, channel)
    data["api_errors"] = api_errors

    print(f"finnished channel: {channel.name}")

    return data


async def _main(channels):
    async with aiohttp.ClientSession(cookies=cookies) as session:
        tasks = [_update_channel(session, channel)
                 for channel in channels]
        responses = await asyncio.gather(*tasks)
        return responses


def update_all_async():
    print()
    print("DEBUG updating uploads...")

    channels: list[Channel] = Channel.query.order_by(Channel.id.asc()).all()

    start_all = time.time()

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    all_channel_updates = asyncio.run(_main(channels))

    # channel_uploads = [video for channel in all_channel_updates for video in channel["uploads"]]
    channel_uploads = []
    for channel in all_channel_updates:
        channel_uploads.extend(channel["uploads"])

    db.session.add_all(channel_uploads)
    # db.session.rollback()
    db.session.commit()

    end_all = time.time()

    time_taken = end_all - start_all
    errors = {"count": 0}
    num_uploads = 0

    def handle_error(channel, list_name):
        if channel[list_name] is not None:
            if list_name not in errors:
                errors[list_name] = []
            errors[list_name].append(channel[list_name])
            errors["count"] = errors["count"] + 1

    for channel in all_channel_updates:
        num_uploads += channel["num_uploads"]

        handle_error(channel, "rss_errors")
        handle_error(channel, "api_errors")

    if len(errors) > 1:
        print(f"ERROR: {errors['count']}, check error logs")

    print(
        "Took {} seconds to Handle {} channels. Average per channel: {}".format(
            time_taken,
            len(channels),
            time_taken/len(channels)
        )
    )

    print("Loaded {} new uploads".format(len(channel_uploads)))
    print()
    print()

    from pathlib import Path
    data_dev_dir = Path("data_dev")
    if not data_dev_dir.is_dir():
        data_dev_dir.mkdir(exist_ok=True)

    with open(data_dev_dir.joinpath("errors.json"), "w") as f:
        json.dump(errors, f, indent=4)

    return num_uploads
