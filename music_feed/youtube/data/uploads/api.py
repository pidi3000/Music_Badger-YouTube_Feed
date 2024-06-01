
import json

import pyyoutube
from pyyoutube.models import (
    Video,
    VideoListResponse,
    PlaylistItemListResponse,
)

from music_feed.config import app_config
from music_feed.db_models import Upload, Channel
from music_feed.youtube.data.uploads._base import YT_Uploads_Handler_Base
from music_feed.youtube import auth as YT_auth


class YT_Uploads_Handler_API(YT_Uploads_Handler_Base):

    @classmethod
    def get_channel_uploads(cls, channel: Channel, yt_client: pyyoutube.Client = None) -> tuple[list[Upload], dict | None]:

        if yt_client is None:
            yt_client = YT_auth.get_api_client()

        channel_Uploads = []

        raw_data = yt_client.playlistItems.list(
            playlist_id=channel.upload_pl_ID,
            parts="snippet, contentDetails",
            max_results=50,
        )

        channel_Uploads = cls._handle_uploads(
            raw_Data=raw_data,
            channel=channel
        )

        errors = None

        return (
            channel_Uploads,
            errors
        )

    @classmethod
    def _handle_uploads(cls, raw_Data: PlaylistItemListResponse, channel: Channel) -> list[Upload]:
        channel_Uploads: list[Upload] = []

        try:
            for item in raw_Data.items:

                #####################################################################################################
                upload = Upload.create(
                    yt_id=item.contentDetails.videoId,
                    channel_id=channel.id,
                    title=item.snippet.title,
                    thumbnail_url=item.snippet.thumbnails.high.url,
                    dateTime=item.contentDetails.string_to_datetime(
                        item.contentDetails.videoPublishedAt),
                    add_to_session=False,
                    check_exists=False
                )

                # ? `Upload.create` can return string on duplicate
                if isinstance(upload, Upload):
                    channel_Uploads.append(upload)

        except Exception as e:
            from pathlib import Path
            file_path = Path(f"data_dev/uploads/{channel.name}.json")

            file_path.parent.mkdir(parents=True, exist_ok=True)

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

        return channel_Uploads

    @classmethod
    def check_videos_type(cls, uploads: list[Upload], yt_client: pyyoutube.Client = None) -> list[Upload]:

        if len(uploads) > 50:
            raise ValueError(
                f"The uploads list can not have more than 50 elements, got: {len(uploads)}")

        if yt_client is None:
            yt_client = YT_auth.get_api_client()

        video_data: VideoListResponse = yt_client.videos.list(
            parts=[
                "snippet",
                "contentDetails",
                "liveStreamingDetails"
            ],
            video_id=[upload.yt_id for upload in uploads]
        )

        # Create a lookup dictionary for uploads
        uploads_dict = {upload.yt_id: upload for upload in uploads}

        for video in video_data.items:
            # Shorts
            is_short = cls._check_is_short(video)
            if video.id in uploads_dict:
                uploads_dict[video.id].is_short = is_short

            # Livestream
            is_livestream = cls._check_is_livestream(video)
            if video.id in uploads_dict:
                uploads_dict[video.id].is_livestream = is_livestream

                # Active livestreams have a duration of 0 seconds
                # meaning they would also get marked as a short
                if is_livestream:
                    uploads_dict[video.id].is_short = False

        return uploads

    @classmethod
    def _check_is_short(cls, video: Video) -> bool:
        video_duration = video.contentDetails.get_video_seconds_duration()

        # shorts should be max 60s, but I've seen 61s (probably rounding error, idk.)
        return video_duration < 70

    @classmethod
    def _check_is_livestream(cls, video: Video) -> bool:
        # TODO try differentiating between livestream and "live video premier"
        return video.liveStreamingDetails is not None
