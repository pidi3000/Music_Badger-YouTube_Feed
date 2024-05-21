
import time

import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor

from music_feed.extension import db
from music_feed.db_models import Upload, Channel
from music_feed.youtube.uploads._base import YT_Uploads_Handler_Base
from music_feed.youtube.uploads.web import YT_Uploads_Handler_WEB
from music_feed.youtube.uploads.api import YT_Uploads_Handler_API

####################################################################################################
####################################################################################################


def update_channel(channel: Channel):
    uploads_handler: YT_Uploads_Handler_Base = YT_Uploads_Handler_WEB

    channel_Uploads, errors = uploads_handler.get_channel_uploads(
        channel=channel)

    # TODO
    # if errors
    #     fail-over to different handler

    return channel_Uploads


####################################################################################################
####################################################################################################
async def _update_channel(channel: Channel, executor):
    loop = asyncio.get_event_loop()
    channel_uploads = await loop.run_in_executor(executor, update_channel, channel)

    return channel_uploads


async def _load_channel_uploads():
    channels = Channel.get_all()

    with ThreadPoolExecutor() as executor:
        tasks = [
            _update_channel(channel, executor) for channel in channels
        ]

        new_uploads: list[list[Upload]] = await asyncio.gather(*tasks)

    all_uploads = []

    for channel_uploads in new_uploads:
        all_uploads.extend(channel_uploads)

    return all_uploads, len(channels)


def update_all_channels():

    start_all = time.time()

    new_uploads, num_channels = asyncio.run(_load_channel_uploads())

    end_uploads = time.time()

    # if check is short / livestream
    #     new_uploads = asyncio.run(_check_video_type(new_uploads))

    end_all = time.time()

    db.session.add_all(new_uploads)
    # db.session.rollback()
    db.session.commit()

    time_taken = end_all - start_all

    print()
    print()
    print(
        f"Took {time_taken} seconds to Handle {num_channels} channels. Average per channel: {time_taken/num_channels}"
    )
    print(f"Loaded {len(new_uploads)} new uploads")

    return len(new_uploads)
