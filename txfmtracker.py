#!/usr/bin/env python3

"""
TXFMTrackService
(C) 2015
David Rieger
v1.1
"""

import urllib.request
import json
from storagemanager import StorageManager


def now_playing():

    # New TXFM website has a nicer API that makes things much easier
    URL = "http://www.txfm.ie/assets/includes/ajax/player_info.php?type=On+Air&currentstationID=11"

    req = urllib.request.Request(url=URL, headers={'User-Agent': 'Mozilla/5.0'})

    # It returns a JSON which has a key called "data" which contains - get this - HTML
    jsonstr = urllib.request.urlopen(req).readall().decode("UTF-8")
    onairinfo = json.loads(jsonstr)

    # Try to obtain current song info from JSON response
    try:
        title = onairinfo["currentTitle"]
        artist = onairinfo["currentArtist"]
    except IndexError:
        print("API Error")
        pass

    # If either song or title info not available - set show title as title
    if not (artist and title):
        artist = ""
        try:
            title = onairinfo["title"]
        except IndexError:
            title = "ERROR RETRIEVING SONG INFO"

    return {"title": title, "artist": artist}

if __name__ == "__main__":
    print(now_playing())
    StorageManager().add_song(now_playing())
