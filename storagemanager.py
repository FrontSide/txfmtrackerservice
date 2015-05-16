#!./bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

import redis
from time import gmtime, strftime, strptime
import hashlib

class StorageManager:

    TIMES_KEY = "times"

    def __init__(self, host="localhost", port="6379", db="0"):
        self.storage = redis.StrictRedis(host=host, port=port, db=db)

    def get_song(self, time=None):
        """
        Returns the song that was played at a certain time
        or the one that is currently plyed if no time given
        """
        if time is None:
            return self._get_stored()

        for t in self._get_all_times():
            # Return the song with the first time that is equal to or smaller than the given
            if strptime(t, "%Y.%m.%d %H:%M:%S") <= strptime(time, "%Y.%m.%d %H:%M:%S"):
                return {t: self._get_stored(hashname=t)}

    def add_song(self, song):
        
        c_time = strftime("%Y.%m.%d %H:%M:%S", gmtime())

        to_store = {
            "title": song["title"],
            "artist": song["artist"]
        }

        # Check if the song that is stored as "currently playing" 
        # is the same as the one just fetched
        songhash = StorageManager.song_to_hash(song["title"], song["artist"])
    
        try:
            playing_song = self._get_stored()
        except IndexError:
            playing_song = False        

        # If registered song is not the song just fetched store it 
        if (not playing_song) or (songhash != StorageManager.song_to_hash(playing_song["title"], playing_song["artist"])):
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
            hashname = self._get_all_times()[0] # Index 0 is the time for the last song stored
        return {k.decode("UTF-8"): v.decode("UTF-8") for (k,v) in self.storage.hgetall(hashname).items()}

    def get_all_stored(self):
        """
        Returns all stored songs
        """
        _all_songs = dict()
        for t in self._get_all_times():
            _all_songs[t] = self._get_stored(t)
        return _all_songs

    def song_to_hash(title, artist):
        return hashlib.md5("{}{}".format(title, artist).encode()).hexdigest()
