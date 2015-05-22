#!/usr/bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

import redis
from time import strptime
from collections import OrderedDict
import hashlib
from datetime import datetime
from pytz import timezone
from persistence import Persistence


class StorageManager:

    TIMES_KEY = "times"

    def __init__(self, host="localhost", port="6379", db="0"):
        self.storage = redis.StrictRedis(host=host, port=port, db=db)

    def get_instance():
        return StorageManager()

    def get_song(self, time=None, text=None, scope=10):
        """
        Returns the [scope] songs that were played arount the given time sorted by time
        or the songs that match [text] for either "title" or "artist"
        or the [scope ]songs that were played most recently
        """
        if text is not None and text.strip() is not False:
            return self._get_stored_by_text(text)

        if time is None:
            return self._get_stored()

        for t in self.get_all_times():
            # Return the songs that was played is closest but before or exactly to/at the given time
            # and the numer of SCOPE songs before and after this one
            if strptime(t, "%d.%m.%Y %H:%M:%S") <= strptime(time, "%d.%m.%Y %H:%M:%S"):

                # index of this time in the list
                _idx = self.get_all_times().index(t)

                _songs = OrderedDict()

                _start_idx = max(_idx-int((scope/2)), 0)
                _end_idx = min(_idx+int((scope/2)), len(self.get_all_times())-1)

                for _timekey in self.get_all_times()[_start_idx:_end_idx]:
                    try:
                        _songs[_timekey] = self._get_stored(hashname=_timekey)
                    except IndexError:
                        continue

                return _songs

    def add_song(self, song):

        c_time = datetime.now(timezone("Europe/Dublin")).strftime("%d.%m.%Y %H:%M:%S")

        to_store = {
            "title": song["title"],
            "artist": song["artist"]
            }

        # Check if the song that is stored as "currently playing"
        # is the same as the one just fetched
        songhash = StorageManager.song_to_hash(song["title"], song["artist"])

        try:
            playing_song = self._get_stored()
            playing_song_hash = StorageManager.song_to_hash(playing_song["title"], playing_song["artist"])
        except IndexError:
            playing_song = False

        # If registered song is not the song just fetched store it
        if (not playing_song) or (songhash != playing_song_hash):

            # Also first remove the song that has been the "playing_song"
            # from the storage if it was a TXFM Show rather than an actual song
            if playing_song["title"].strip().lower().startswith("txfm ") and not playing_song["artist"].strip():
                self.storage.delete(self.storage.lpop(self.TIMES_KEY))

            self.storage.lpush(self.TIMES_KEY, c_time)
            self.storage.hmset(c_time, to_store)

    def get_all_times(self):
        """
        Returns the list of all times for which a song is stored
        """
        return [ti.decode("UTF-8") for ti in self.storage.lrange(self.TIMES_KEY, start=0, end=-1)]

    def _get_stored(self, hashname=None):
        """
        Returns the song that is stored with [hashname]
        by default i.e if no hashname given, the last song stored is returned (which is the song currently playing)
        """
        if hashname is None:
            hashname = self.get_all_times()[0]  # Index 0 is the time for the last song stored
        return {k.decode("UTF-8"): v.decode("UTF-8") for (k, v) in self.storage.hgetall(hashname).items()}

    def get_all_stored(self, amount=10):
        """
        Returns the latest [amount] stored songs, sorted by time
        """
        _all_songs = OrderedDict()

        _end_idx = min(amount, len(self.get_all_times())-1)
        for t in self.get_all_times()[0:_end_idx]:
            _all_songs[t] = self._get_stored(t)

        return _all_songs

    def _get_stored_by_text(self, text):
        "Returns all songs that match [text] for either title or artist"
        _all_songs = self.get_all_stored(amount=len(self.get_all_times()))
        _result = OrderedDict()
        for k, v in _all_songs.items():
            if (v["title"] + v["artist"]).replace(" ", "").lower().find(text.replace(" ", "").lower()) != -1:
                _result[k] = v
        return _result

    def song_to_hash(title, artist):
        return hashlib.md5("{}{}".format(title, artist).encode()).hexdigest()
