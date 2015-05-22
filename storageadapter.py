"""
TXFMTrackService
(C) 2015
David Rieger
"""

import redis
import re
from pymongo import MongoClient
from collections import OrderedDict
from time import strptime


class Cache:

    def __init__(self, host="localhost", port="6379", db="0"):
        self.storage = redis.StrictRedis(host=host, port=port, db=db)
        self.TIMES_KEY = "times"

    def add_song(self, song, time):
        """
        Adds [song] to the DB as hash with key [time]
        """

        # First remove the song that has been the "playing_song"
        # from the storage if it was a TXFM Show rather than an actual song
        last_song = self.get_latest_songs(1)
        ignore_pattern = re.compile("((nialler9[\s]?.*)|(txfm[\s]?.*))")

        if ignore_pattern.match(last_song["title"].strip().lower()) and not last_song["artist"].strip():
            self.storage.delete(self.storage.lpop(self.TIMES_KEY))

        self.storage.lpush(self.TIMES_KEY, time)
        self.storage.hmset(time, song)

    def get_times(self, amount=None):
        """
        Returns the latest [amount] stored times
        All if [amount] is ::None::
        """
        if amount is None:
            end_idx = -1
        else:
            end_idx = min(amount-1, self.get_amount_songs()-1)
        return [t.decode("UTF-8") for t in self.storage.lrange(self.TIMES_KEY, start=0, end=end_idx)]

    def get_amount_songs(self):
        """
        Returns the number of songs stored in the cache
        """
        return self.storage.llen(self.TIMES_KEY)

    def get_latest_songs(self, amount=50):
        """
        Returns the latest [amount] songs
        All if [amount] is ::None::
        if [amount] is ::1:: only the value of the hash
        for the latest song is returned i.e. no time
        """
        if amount is 1:
            return self.get_song_for_key(self.get_times(amount=1)[0])

        _times = self.get_times(amount)
        _all_songs = OrderedDict()
        for t in self.get_times(amount):
            _all_songs[t] = self.get_song_for_key(t)

        return _all_songs

    def get_song_for_key(self, time):
        """
        Returns a song for the given [time]
        whereas time has to be an actual existing hash key
        """
        return {k.decode("UTF-8"): v.decode("UTF-8") for (k, v) in self.storage.hgetall(time).items()}

    def get_songs_by_time(self, req_time, scope=30):
        """
        Returns [scope] songs stored around the given [req_time]
        [req_time] must be in the correct format _times %d.%m.%Y %H:%M:%S
        but does not have to be an existing key
        """
        for t in self.get_times():
            # Go through the list from HEAD to TAIL and get the [scope] times arounc the
            # time that closestly matches [req_time] but is definitly smaller than [req_time]
            if strptime(t, "%d.%m.%Y %H:%M:%S") > strptime(str(req_time), "%d.%m.%Y %H:%M:%S"):
                continue

            # index of this time in the list
            _idx = self.get_times().index(t)

            _start_idx = max(_idx-int((scope/2)), 0)
            _end_idx = min(_idx+int((scope/2)), self.get_amount_songs()-1)

            # Get the songs for all scope times and add to dict
            _songs = OrderedDict()
            for _timekey in self.get_times()[_start_idx:_end_idx]:
                _songs[_timekey] = self.get_song_for_key(_timekey)

            return _songs

    def get_songs_by_text(self, text, scope=None):
        """
        returns all songs that match [text] within the latest [scope] songs
        """
        _result = OrderedDict()
        for k, v in self.get_latest_songs(amount=self.get_amount_songs()).items():
            if (v["title"] + v["artist"]).replace(" ", "").lower().find(text.replace(" ", "").lower()) != -1:
                _result[k] = v
        return _result

    def remove_song(self, time):
        """
        removes [time] from the list of times and the accoring song from the cache
        """
        self.storage.lrem(self.TIMES_KEY, count=1, value=time)
        self.storage.delete(time)


class Persistence:

    def __init__(self, host="localhost", port=6380, dbname="txfmstore"):
        self.db = MongoClient(host, port)[dbname]
        self.col_songs = self.db.songs

    def add_song(self, song, time):
        song["_id"] = time
        self.col_songs.insert_one(song)

    def is_stored(self, time):
        _res = self.col_songs.find_one({"_id": time})
        if _res is None:
            return False
        return True

    def get_songs_by_time(self, req_time, scope=30):

        for t in self.get_all_times():
            if t > req_time:
                continue

            # index of this time in the list
            _idx = self.get_all_times().index(t)

            _start_idx = max(_idx-int((scope/2)), 0)
            _end_idx = min(_idx+int((scope/2)), len(self.get_all_times())-1)

            _songs = OrderedDict()
            for _timekey in self.get_all_times()[_start_idx:_end_idx]:
                _songs[_timekey] = self.col_songs.find_one({"_id": t}, {"_id": False})

            return _songs

    def get_all_times(self):
        return sorted([t["_id"] for t in self.col_songs.find({}, {"_id": True})])
