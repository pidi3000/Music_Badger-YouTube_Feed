
import requests
from requests import Response

import xmltodict
import json

import time
from datetime import datetime

from music_feed.db_models import Upload, Channel
from music_feed.youtube.uploads._base import YT_Uploads_Handler_Base


YT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class YT_Uploads_Handler_WEB(YT_Uploads_Handler_Base):

    @classmethod
    def get_channel_uploads(cls, channel: Channel) -> tuple[list[Upload], dict]:
        channel_Uploads = []

        session = requests.Session()

        response = session.get(channel.feed_url)
        # response.raise_for_status()
        raw_data = response.text

        if response.status_code == 200:

            channel_Uploads = cls._handle_uploads(
                raw_Data=raw_data,
                channel=channel
            )

            errors = None

        else:
            # errors = f"Error: {response.status} - {await response.text()}"
            errors = {}
            errors["text"] = raw_data
            errors["status"] = response.status_code

            errors["channel.name"] = channel.name

        return (
            channel_Uploads,
            errors
        )

    @classmethod
    def _handle_uploads(cls, raw_Data, channel: Channel) -> list[Upload]:
        channel_Data = xmltodict.parse(raw_Data)

        channel_Uploads = []

        channel_Data_Feed = channel_Data["feed"]
        channel_ID = channel_Data_Feed["yt:channelId"]
        channel_Title = channel_Data_Feed["title"]

        raw_uploads = []
        if "entry" in channel_Data_Feed:
            raw_uploads = channel_Data_Feed["entry"]

            # if channel has only 1 video entry is a dict of the single upload, otherwise it's a list of videos
            if isinstance(raw_uploads, dict):
                temp = list()
                temp.append(raw_uploads)
                raw_uploads = temp

            if not isinstance(raw_uploads, list):
                raw_uploads = list(raw_uploads)

        try:
            for raw_upload_data in raw_uploads:

                videoID = raw_upload_data["yt:videoId"]
                videoTitle = raw_upload_data["title"]
                videoUploadTime = raw_upload_data["published"]
                videoURL = raw_upload_data["link"]["@href"]

                thumbnailData = raw_upload_data["media:group"]["media:thumbnail"]
                thumbnailURL = thumbnailData["@url"]
                thumbnail_width = thumbnailData["@width"]
                thumbnail_height = thumbnailData["@height"]
                # rating = upload["media:group"]["media:community"]["media:starRating"]["@average"]

                upload_date = str(videoUploadTime).split("+", 1)[0]
                upload_dateTime = datetime.strptime(
                    upload_date, YT_DATE_FORMAT)

                #####################################################################################################
                upload = Upload.create(
                    yt_id=videoID,
                    channel_id=channel.id,
                    title=videoTitle,
                    thumbnail_url=thumbnailURL,
                    dateTime=upload_dateTime,
                    add_to_session=False,
                    check_exists=False
                )

                # `Upload.create` can return string on duplicate
                if isinstance(upload, Upload):
                    channel_Uploads.append(upload)

        except Exception as e:
            from pathlib import Path
            file_path = Path(f"data_dev/uploads/{channel.name}.json")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            # file_path.touch()

            with open(file_path, "a") as f:
                f.write("\n\n")
                json.dump({
                    channel_Data
                }, f, indent=4, ensure_ascii=False)

            print(f"Channel update failed: {channel.name}")
            print(e)

        return channel_Uploads

    @classmethod
    def check_videos_type(cls, uploads: list[Upload]) -> list[Upload]:

        for upload in uploads:
            is_short = cls._check_is_short(upload.yt_id)
            upload.is_short = is_short

        return uploads

    @classmethod
    def _check_is_short(cls, video_ID: str) -> bool:
        url = 'https://www.youtube.com/shorts/' + video_ID

        session = requests.Session()
        # session.max_redirects = 0
        response = session.head(url)

        response.raise_for_status()

        return not response.is_redirect
        # return response.status_code.real == 200
