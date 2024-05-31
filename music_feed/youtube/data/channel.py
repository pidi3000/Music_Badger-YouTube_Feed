
from music_feed.youtube import auth as YT_Auth

from pyyoutube import (
    ChannelListResponse,
    VideoListResponse
)


__all__ = [
    "get_channel_data",
    "get_channel_pfp_url",
    "get_channel_ID_from_video",
    "get_channel_ID_from_handle",
    "get_channel_ID_from_username",
]


##################################################
##################################################
def get_channel_data(channel_id):
    channel_data = {
        "id": "00000",
        "name": "temp",
        "profile_img_url": "",
    }

    cli = YT_Auth.get_api_client()

    ch_data_list: ChannelListResponse = cli.channels.list(
        parts="snippet,contentDetails",
        channel_id=channel_id
    )

    # print(response)

    try:
        ch_data = ch_data_list.items[0]

        channel_data["id"] = ch_data.id
        channel_data["name"] = ch_data.snippet.title
        channel_data["profile_img_url"] = ch_data.snippet.thumbnails.high.url

    except KeyError as e:
        print(e)
        error_msg = "ERROR: no youtube data found"
        print(error_msg)
        channel_data["error"] = error_msg

    # print(response["items"][0])
    # print(channel_data)

    return channel_data


def get_channel_pfp_url(yt_channel_id) -> str:
    profile_img_url = None

    cli = YT_Auth.get_api_client()

    channel_data: ChannelListResponse = cli.channels.list(
        parts="snippet,contentDetails",
        channel_id=yt_channel_id
    )

    # print(response)

    try:
        profile_img_url = channel_data.items[0].snippet.thumbnails.high.url
        # profile_img_url = response["items"][0]["snippet"]["thumbnails"]["default"]["url"]

    except KeyError as e:
        print(e)
        error_msg = "ERROR: no youtube data found"
        print(error_msg)

    # TODO tuple return, legacy support
    return profile_img_url, None


##################################################
# get channel ID
##################################################
def get_channel_ID_from_video(video_id: str):
    cli = YT_Auth.get_api_client()

    video_response: VideoListResponse = cli.videos.list(
        parts='snippet',
        video_id=video_id
    )

    video_response.items

    if video_response.items is None or len(video_response.items) < 1:
        raise LookupError(f"no youtube video found with {video_id=}")

    channel_id = video_response.items[0].snippet.channelId
    return channel_id


##################################################
def _get_channel_ID(handle: str = None, username: str = None):
    cli = YT_Auth.get_api_client()

    channel_data: ChannelListResponse = cli.channels.list(
        parts="snippet,contentDetails",
        for_handle=handle,
        for_username=username
    )

    yt_id = None

    try:
        yt_id = channel_data.items[0].id

    except KeyError as e:
        print(e)
        error_msg = f"ERROR: no youtube data found for: '{handle=}' OR '{username=}'"
        print(error_msg)

    return yt_id


def get_channel_ID_from_handle(handle: str):
    return _get_channel_ID(handle=handle)


def get_channel_ID_from_username(username: str):
    username = username.removeprefix("@").strip()
    channel_id = _get_channel_ID(username=username)

    if channel_id is None:
        raise LookupError(f"no youtube channel found with {username=}")

    return channel_id
