
from .YouTube_auth import get_authorized_yt_obj, del_yt_credentials
from ._uploads import update_all_async
from music_feed.youtube import uploads

# TODO rework youtube stuff

from google.auth.exceptions import RefreshError


##################################################
# Channels
##################################################

def get_channel_ID_from_video(video_id):
    # Create a YouTube Data API service
    youtube, redirect = get_authorized_yt_obj()

    if redirect is not None:
        return None

    # Retrieve video details using videos().list() method
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    # Extract channel ID from video details
    if 'items' not in video_response or len(video_response['items']) < 1:
        raise LookupError(f"no youtube video found with {video_id=}")

    channel_id = video_response['items'][0]['snippet']['channelId']
    return channel_id


def get_channel_ID_from_handle(handle):

    youtube, redirect = get_authorized_yt_obj()

    if redirect is not None:
        return None

    request = youtube.channels().list(
        part="snippet",
        forHandle=handle
    )
    response = request.execute()

    # print(response)
    yt_id = None

    try:
        yt_id = response["items"][0]["id"]

    except KeyError as e:
        print(e)
        error_msg = "ERROR: no youtube data found"
        print(error_msg)

    return yt_id


def get_channel_ID_from_username(username: str):

    username = username.removeprefix("@").strip()

    youtube, redirect = get_authorized_yt_obj()

    if redirect is not None:
        return None

    request = youtube.channels().list(
        part='id',
        forUsername=username
    )

    response = request.execute()

    if 'items' not in response or len(response['items']) < 0:
        raise LookupError(f"no youtube channel found with {username=}")

    return response['items'][0]['id']
    # else:
    #     return None


def get_channel_data(channel_id):
    channel_data = {
        "id": "00000",
        "name": "temp",
        "profile_img_url": "",
    }

    youtube, redirect = get_authorized_yt_obj()

    if redirect is not None:
        return None

    request = youtube.channels().list(
        part="snippet,contentDetails",
        id=channel_id
    )
    response = request.execute()

    # print(response)

    try:
        channel_data["id"] = response["items"][0]["id"]
        channel_data["name"] = response["items"][0]["snippet"]["title"]
        channel_data["profile_img_url"] = response["items"][0]["snippet"]["thumbnails"]["default"]["url"]

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

    youtube, redirect = get_authorized_yt_obj()

    if redirect is not None:
        return None, redirect

    request = youtube.channels().list(
        part="snippet,contentDetails",
        id=yt_channel_id
    )
    response = request.execute()

    # print(response)

    try:
        profile_img_url = response["items"][0]["snippet"]["thumbnails"]["default"]["url"]

    except KeyError as e:
        print(e)
        error_msg = "ERROR: no youtube data found"
        print(error_msg)

    # print(response["items"][0])
    # print(channel_data)

    return profile_img_url, None


def _get_page_subscriptions(youtube, pageToken=""):

    request = youtube.subscriptions().list(
        part="snippet",
        maxResults=50,
        mine=True,

        pageToken=pageToken,
    )
    response = request.execute()

    return response


def _get_formated_subscriptions(raw_data):

    subscriptions = []

    count = 0
    for channel in raw_data["items"]:
        channel_data = {
            "id": channel["snippet"]["resourceId"]["channelId"],
            "name": channel["snippet"]["title"],
            "profile_img_url": channel["snippet"]["thumbnails"]["default"]["url"]
        }

        subscriptions.append(channel_data)

        if count < 1:
            # print()
            # print(channel_data)
            count += 1

    return subscriptions


def get_all_subscriptions():
    try:
        youtube, redirect = get_authorized_yt_obj()

        if redirect is not None:
            return None

        all_subscriptions = []

        # print(response["nextPageToken"])
        response = _get_page_subscriptions(youtube)
        all_subscriptions.extend(_get_formated_subscriptions(response))

        while "nextPageToken" in response:
            response = _get_page_subscriptions(
                youtube, response["nextPageToken"])
            all_subscriptions.extend(_get_formated_subscriptions(response))

        return all_subscriptions

    except RefreshError as e:
        print("ERROR: Credentials need to be Refreshed")
        del_yt_credentials()
        return []


##################################################
# Uploads
##################################################

def update_Uploads():
    # return update_all_async()
    
    return uploads.update_all_channels()
