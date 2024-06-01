
from music_feed.db_models import Upload, Channel

import pyyoutube


class YT_Uploads_Handler_Base():

    @classmethod
    def get_channel_uploads(cls, channel: Channel, yt_client: pyyoutube.Client = None) -> tuple[list[Upload], dict | None]:
        """Upadete single channels uplaods

        Parameters
        ----------
        channel : Channel
            the channel to update
        yt_client : pyyoutube.Client
            a youtube api client, only used by the `API` handler

        Returns
        -------
        tuple[list[Upload], dict | None]
            returns a `tuple` containing:\n
            1: list of all new `Upload` objects,\n
            2: `None` or dict of errors.


        Raises
        ------

        """
        raise NotImplementedError("Derived class must implement this function")

    @classmethod
    def _handle_uploads(cls, raw_Data, channel: Channel) -> list[Upload]:
        """Convert Raw data to `Upload` objects

        Parameters
        ----------
        channel_Data_Raw : any
            raw data
        channel: Channel
            `Channel` being update

        Returns
        -------
        list[Upload]
            `list` of new uploads

        Raises
        ------
        """
        raise NotImplementedError("Derived class must implement this function")

    @classmethod
    def check_videos_type(cls, uploads: list[Upload], yt_client: pyyoutube.Client = None) -> list[Upload]:
        """Check each upload for the type of video it is
        , either "normal" video, short or livestream

        Parameters
        ----------
        uploads : list[Upload]
            list of uploads to check
        yt_client : pyyoutube.Client
            a youtube api client, only used by the `API` handler

        Returns
        -------
        list[Upload]
            uploads list with video type set

        """
        raise NotImplementedError("Derived class must implement this function")
