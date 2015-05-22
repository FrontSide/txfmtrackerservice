#!/usr/bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

import hashlib
from datetime import datetime
from pytz import timezone
from storageadapter import Cache, Persistence


class StorageManager:

    def __init__(self):
        self.cache = Cache()
        self.perst = Persistence()

    def get_songs(self, time=None, text=None, scope=30):
        """
        Returns the songs that were played arount the given [time] sorted by time
        or the songs that match [text]
        or the [scope] songs that were played most recently is time is ::None::
        """

        if time:
            return self.cache.get_songs_by_time(req_time=time, scope=scope)

        if text is None or not text.strip():
            return self.cache.get_latest_songs(amount=scope)

        return self.cache.get_songs_by_text(text=text)

    def add_song(self, song):
        """
        Adds a song to the the storage if it is not the same song as the one that was added last
        """
        c_time = datetime.now(timezone("Europe/Dublin")).strftime("%d.%m.%Y %H:%M:%S")

        to_store = {
            "title": song["title"],
            "artist": song["artist"]
            }

        # Check if the song that is stored as "currently playing"
        # is the same as the one just fetched
        songhash = StorageManager.song_to_hash(song["title"], song["artist"])

        try:
            playing_song = self.cache.get_latest_songs(amount=1)
            playing_song_hash = StorageManager.song_to_hash(playing_song["title"], playing_song["artist"])
        except IndexError:
            playing_song = False

        # If registered song is not the song just fetched store it
        if (not playing_song) or (songhash != playing_song_hash):
            self.cache.add_song(song=to_store, time=c_time)

    def song_to_hash(title, artist):
        return hashlib.md5("{}{}".format(title, artist).encode()).hexdigest()
