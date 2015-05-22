#!/usr/bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""
import bottle
from bottle import route, run, response
from storagemanager import StorageManager

sm = StorageManager()


@route('/api/get/all')
def get_all_songs():
    response.headers['Access-Control-Allow-Origin'] = '*'
    return sm.get_songs()


@route('/api/get/time/<time>')
def get_song(time):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return sm.get_songs(time=time)


@route('/api/get/text/<text>')
def get_song(text):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return sm.get_songs(text=text)

app = bottle.default_app()

if __name__ == '__main__':
    run(host="localhost", port=8080)
