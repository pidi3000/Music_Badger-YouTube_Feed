
from .YouTube_auth import get_authorized_yt_obj, del_yt_credentials
from ._uploads import update_all_async

# TODO rework youtube stuff

from google.auth.exceptions import RefreshError


##################################################
# Channels
##################################################
def get_channel_data(channel_id):
    channel_data = {
        "id": "00000",
        "name": "temp",
        "profile_img_url": "",
    }

    youtube = get_authorized_yt_obj()

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
        youtube = get_authorized_yt_obj()

        all_subscriptions = []

        # print(response["nextPageToken"])
        response = _get_page_subscriptions(youtube)
        all_subscriptions.extend(_get_formated_subscriptions(response))

        while "nextPageToken" in response:
            response = _get_page_subscriptions(youtube, response["nextPageToken"])
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
    return update_all_async()
