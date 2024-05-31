
from .subscriptions import *
from .channel import *


def update_Uploads():
    from music_feed.youtube.data import uploads
    return uploads.update_all_channels()
