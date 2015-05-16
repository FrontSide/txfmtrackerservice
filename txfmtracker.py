#!./bin/python3

"""
TXFMTrackService
(C) 2015
David Rieger
"""

import urllib.request
import json
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from storagemanager import StorageManager

def now_playing():    
   
    # I need to use that URL which was buried somewhere in their JS
    URL = "http://www.txfm.ie/player/assets/includes/ajax/hp_grid_gen.php"
 
    # It returns a JSON which has a key called "data" which contains - get this - HTML
    jsonstr = urllib.request.urlopen(URL).readall().decode("UTF-8")
    htmlpure = json.loads(jsonstr)["data"]
    htmlsoup = BeautifulSoup(htmlpure)

    # The tag where the songname is in doesn't have an id so
    # let's keep our fingers crossed that this will work for a while...
    nowplaying = htmlsoup.find_all("h2", class_="tName white")[0].text
    
    try:
        artist = nowplaying.split("-")[0].strip()
        title = nowplaying.split("-")[1].strip()
    except IndexError:
        artist = ""
        title = nowplaying

    return {"title": title, "artist": artist}

sm = StorageManager()

# Update
sm.add_song(now_playing())

