#!/usr/bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

from pymongo import MongoClient


class Persistence:

    def __init__(self, host="localhost", port="6380"):
        self.db = MongoClient(host, port)['txfmstore']
        self.col_times = self.db.times
        self.col_songs = self.db.songs

    def add(sm):
        if len(sm.get_all_times) > 20:
            overlap_times = sm.get_all_times[20:-1]
            db().col_times.insert_many(overlap_times)

        def wrapper(self, song):
            add_func(song)
