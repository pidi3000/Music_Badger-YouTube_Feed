
from music_feed.db_models import Upload, Channel


class YT_Uploads_Handler_Base():

    @classmethod
    def update_channel(cls, channel: Channel) -> tuple[list[Upload], dict | None]:
        """Upadete single channels uplaods

        Parameters
        ----------
        channel : Channel
            the channel to update

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
    def _check_video_is_short(cls, upload_Data_Raw: dict, upload_id: int) -> bool:
        raise NotImplementedError("Derived class must implement this function")

    @classmethod
    def _check_video_is_livestream(cls, upload_Data_Raw: dict, upload_id: int) -> bool:
        raise NotImplementedError("Derived class must implement this function")
