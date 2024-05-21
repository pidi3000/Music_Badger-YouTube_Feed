

import xmltodict
import json

import time
from datetime import datetime

from pyyoutube import Client
from pyyoutube.models import (
    PlaylistItemListResponse,
    PlaylistItem,
    PlaylistItemSnippet,
    PlaylistItemContentDetails
)

from music_feed.config import app_config
from music_feed.db_models import Upload, Channel
from music_feed.youtube.uploads._base import YT_Uploads_Handler_Base


class YT_Uploads_Handler_API(YT_Uploads_Handler_Base):

    @classmethod
    def get_channel_uploads(cls, channel: Channel) -> tuple[list[Upload], dict | None]:
        print(f"Start channel: {channel.name}")

        YT_API_KEY = app_config.yt_feed.YT_API_KEY
        if YT_API_KEY is None or len(YT_API_KEY.strip()) < 10:
            raise KeyError(f"YT_API_KEY mus be set to use API")

        cli = Client(api_key=YT_API_KEY)

        # cli.session = session

        channel_Uploads = []

        raw_data = cli.playlistItems.list(
            playlist_id=channel.upload_pl_ID,
            parts="snippet, contentDetails",
            max_results=50,
        )

        channel_Uploads = cls._handle_uploads(
            raw_Data=raw_data,
            channel=channel
        )

        errors = None

        print(f"Done channel: {channel.name} - {len(channel_Uploads)}")

        return (
            channel_Uploads,
            errors
        )

    @classmethod
    def _handle_uploads(cls, raw_Data: PlaylistItemListResponse, channel: Channel) -> list[Upload]:

        # if channel_upload_data.items is None:
        #     return []

        channel_Uploads: list[Upload] = []

        try:
            for item in raw_Data.items:

                #####################################################################################################
                upload = Upload.create(
                    yt_id=item.contentDetails.videoId,
                    channel_id=channel.id,
                    title=item.snippet.title,
                    thumbnail_url=item.snippet.thumbnails.default.url,
                    dateTime=item.contentDetails.string_to_datetime(
                        item.contentDetails.videoPublishedAt),
                    add_to_session=False
                )

                # `Upload.create` can return string on duplicate
                if isinstance(upload, Upload):
                    channel_Uploads.append(upload)

        except Exception as e:
            from pathlib import Path
            file_path = Path(f"data_dev/uploads/{channel.name}.json")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

            with open(file_path, "a") as f:
                f.write("\n\n")
                json.dump(
                    raw_Data.to_dict(True),
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print(f"Channel update failed: {channel.name}")
            print(e)

        # channel_Uploads.sort(key=lambda x: x.dateTime)

        return channel_Uploads
