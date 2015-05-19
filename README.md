#TXFM Trackservice

A tiny app with which the Songs played on the Irish Independent Radio TXFM Dublin (105.2) can be tracked.

# Live on [www.txfmtrack.com](www.txfmtrack.com)

######Built with Python, Redis, bottle.py and BeautifulSoup.

---

## Recommended/Tested Setup

- Start a redis server on localhost with default port **6379**

- Run the main file as cronjob (best every 1-3 minutes since the average song is around 4 minutes)


    ./txfmtracker.py

- Start the HTTP ReST interface with a WSGI server like **gunicorn**


     gunicorn -w 4 -b 127.0.0.1:8384 web:app &

- Link your webserver to the web interface on port **8384**

######Optionally:

- Let your webserver listen on location **"/api"** and on port **80** and link it to the above set-up ReST service

- Download the txfmtrackservice-client and link your webserver there as well (location: **"/"**, port: **80**)


## Backend API

For simply fetching the currently played song, call

    now_playing()
from the *txfmtracker.py* module

---

For storing things to the Redis-DB first create a StorageManager object

     from storagemanager import StorageManager
     sm = StorageManager()

For adding the currently played song to the DB call

     sm.add_song(now_playing())

For retrieving the songs played around a certain time call (watch the formatting)

     sm.get_song(time="%d.%m.%Y %H:%M:%S")

For retrieving a dictionary of all stored songs call

     sm.get_all_songs()

## ReST API

For retrieving all the songs stored call

    /api/get/all

For a couple of songs around a certain time call (watch formatting)

    /api/get/%d.%m.%Y %H:%M:%S
