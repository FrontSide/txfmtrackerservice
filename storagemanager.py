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
        self.persistence = Persistence()
        self.MAX_NUM_IN_CACHE = 50

    def get_songs(self, time=None, text=None, scope=50):
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
        except KeyError:
            playing_song = False

        if (not playing_song) or (songhash != playing_song_hash):

            # Save new song to cache
            self.cache.add_song(song=to_store, time=c_time)

            # Save songs that is now on 2nd place (should be equal to playing_song) to the persistent DB
            # playing_song might not be the song now on 2nd place if the cache adapter has decided to delete it
            # e.g. in case that it was not a real song but merely a TXFM show
            _persist_key = self.cache.get_times(amount=2)[1]
            self.persistence.add_song(song=self.cache.get_song_for_key(_persist_key), time=_persist_key)
            print("persist:: {}".format(_persist_key))

            # If the number of songs stored in the cache is bigger than 50 remove the oldest ones
            # but only if the songs already exists in the persistence layer - otherwise add them there
            if self.cache.get_amount_songs() <= self.MAX_NUM_IN_CACHE:
                return

            _keys_to_remove = self.cache.get_times()[self.MAX_NUM_IN_CACHE-1:]

            for t in _keys_to_remove:
                if not self.persistence.is_stored(t):
                    self.persistence.add_song(song=self.cache.get_song_for_key(t), time=t)
                self.cache.remove_song(time=t)

    def song_to_hash(title, artist):
        return hashlib.md5("{}{}".format(title, artist).encode()).hexdigest()
