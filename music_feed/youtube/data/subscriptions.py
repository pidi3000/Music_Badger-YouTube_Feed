
from music_feed.youtube import auth as YT_Auth

from pyyoutube import (
    Client,
    SubscriptionListResponse
)


__all__ = [
    "get_all_subscriptions",
]


##################################################
##################################################
def _get_page_subscriptions(cli: Client, pageToken="") -> SubscriptionListResponse:

    data = cli.subscriptions.list(
        part="snippet",
        maxResults=50,
        mine=True,

        pageToken=pageToken,
    )

    return data


def _get_formated_subscriptions(raw_data: SubscriptionListResponse):
    subscriptions = []

    for channel in raw_data.items:
        channel_data = {
            "id": channel.snippet.resourceId.channelId,
            "name": channel.snippet.title,
            "profile_img_url": channel.snippet.thumbnails.high.url
        }

        subscriptions.append(channel_data)

    return subscriptions


def get_all_subscriptions():
    cli = YT_Auth.get_oauth_client()

    if cli is None:
        return None

    all_subscriptions = []

    # print(response["nextPageToken"])
    raw_data = None

    while True:
        raw_data = _get_page_subscriptions(
            cli,
            raw_data.nextPageToken if raw_data else ""
        )

        all_subscriptions.extend(_get_formated_subscriptions(raw_data))

        if raw_data.nextPageToken is None or len(raw_data.nextPageToken) < 2:
            break

    return all_subscriptions
