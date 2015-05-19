#!/usr/bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

import redis
from time import gmtime, strftime, strptime
from collections import OrderedDict
import hashlib
from datetime import datetime, timedelta


class StorageManager:

    TIMES_KEY = "times"

    def __init__(self, host="localhost", port="6379", db="0"):
        self.storage = redis.StrictRedis(host=host, port=port, db=db)

    def get_song(self, time=None):
        """
        Returns the songs that were played arount the given time sorted by time
        or the one that is currently plyed if no time given
        """
        if time is None:
            return self._get_stored()

        for t in self._get_all_times():
            SCOPE = 5
            # Return the songs that was played is closest but before or exactly to/at the given time
            # and the numer of SCOPE songs before and after this one
            if strptime(t, "%d.%m.%Y %H:%M:%S") <= strptime(time, "%d.%m.%Y %H:%M:%S"):

                # index of this time in the list
                _idx = self._get_all_times().index(t)

                _songs = OrderedDict()
                for _timekey in self._get_all_times()[_idx-SCOPE:_idx+SCOPE]:
                    try:
                        _songs[_timekey] = self._get_stored(hashname=_timekey)
                    except IndexError:
                        pass

                return _songs

    def add_song(self, song):

        c_time = (datetime.utcnow() + timedelta(hours=1)).strftime("%d.%m.%Y %H:%M:%S")

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
            self.storage.lpush(self.TIMES_KEY, c_time)
            self.storage.hmset(c_time, to_store)

    def _get_all_times(self):
        """
        Returns the list of all times for which a song is stored
        """
        return [ti.decode("UTF-8") for ti in self.storage.lrange(self.TIMES_KEY, start=0, end=-1)]

    def _get_stored(self, hashname=None):
        """
        Returns the song that is stored with >hashname
        by default i.e if no hashname given, the last song stored is returned (which is the song currently playing)
        """
        if hashname is None:
            hashname = self._get_all_times()[0]  # Index 0 is the time for the last song stored
        return {k.decode("UTF-8"): v.decode("UTF-8") for (k, v) in self.storage.hgetall(hashname).items()}

    def get_all_stored(self):
        """
        Returns all stored songs sorted by time
        """
        _all_songs = OrderedDict()
        for t in self._get_all_times():
            _all_songs[t] = self._get_stored(t)
        return _all_songs

    def song_to_hash(title, artist):
        return hashlib.md5("{}{}".format(title, artist).encode()).hexdigest()
