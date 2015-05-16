#!./bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""
from bottle import route, run, template
import txfmtracker
from storagemanager import StorageManager

sm = StorageManager()

@route('/get/all')
def get_all_songs():
    return sm.get_all_stored()

@route('/get/<time>')
def get_song(time):
    return sm.get_song(time)

run(host='localhost', port=8384)


