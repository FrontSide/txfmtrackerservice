#!./bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""
from bottle import route, run, response
from storagemanager import StorageManager

sm = StorageManager()


@route('/get/all')
def get_all_songs():
    response.headers['Access-Control-Allow-Origin'] = '*'
    return sm.get_all_stored()


@route('/get/<time>')
def get_song(time):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return sm.get_song(time)

run(host='localhost', port=8384)
