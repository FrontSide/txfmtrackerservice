#TXFM Trackservice

A tiny app with which the Songs played on the Irish Independent Radio TXFM Dublin (105.2) can be tracked.

# Live on [www.txfmtrack.com](http://www.txfmtrack.com)

## Now running with docker

######Built with Python, Redis, MongoDB, bottle.py and BeautifulSoup.

---

## Setup with Docker (recommended)

Install docker and docker compose and run 

    docker-compose up -d

This will start 3 docker containers (the txfmtrack app, redis and mongo) which are linked with each other.
You can now access the service from the host machine (where the docker containers are running) on port 8585 (use the docker host IP address instead of "localhost" if you can't connect).
Link your webserver on the host machine to this port to publish the service.

## Setup without Docker

Start a redis server on localhost with default port **6379**

Start a mongodb server on localhost with port **6380**

Run the main file as cronjob (best every 1-3 minutes since the average song is around 4 minutes)

    ./txfmtracker.py

Start the HTTP ReST interface with a WSGI server like **gunicorn**<br>

     gunicorn -w 4 -b 127.0.0.1:8384 web:app &

Link your webserver to the web interface on port **8384**

######Optionally:

- Let your webserver listen on location **"/api"** and on port **80** and link it to the above set-up ReST service

- Download the txfmtrackservice-client and link your webserver there as well (location: **"/"**, port: **80**)


## Backend API

For simply fetching the currently played song, call

    now_playing()
from the *txfmtracker.py* module

---

### Storing in-Memory and on the FS

The storage system utilises - per default - a Redis im-MemoryDB and a MongoDB  instance fot persisting things on the file system. This way Most recent Songs can be accessed quickly but the memory can be releieved from older ones.

If you want to swap either of the technologies check out **sorageadapter.py**

If you want to change the storagemechanism completely (e.g. redefine when songs are moved from cache to persisten, or removing the cache comletely) check out **storagemanager.py**

---

For storing things, first create a StorageManager object

     from storagemanager import StorageManager
     sm = StorageManager()

For adding the currently played song to the DB call

     sm.add_songs(now_playing())

For retrieving [n] songs played around a certain time call (watch the formatting) (n=10 by default)

     sm.get_songs(time="%d.%m.%Y %H:%M:%S", scope=n)

For retrieving all songs that match [string] call

     sm.get_songs(text=string)

For retrieving a dictionary of the latest [n] stored songs call

     sm.get_songs(scope=n)

## ReST API

For retrieving all the songs stored (cache only)

    /api/get/all

For a couple of songs around a certain time call (watch formatting!) (cache only) (quick)

    /api/get/time/[%d.%m.%Y %H:%M:%S]


As above but with persistent storage included (slower)

    /api/full/time/[%d.%m.%Y %H:%M:%S]

For all songs that match [text] call (cache only) (quick)

    /api/get/text/[text]


As above but with persistent storage included (slower)

    /api/full/text/[text]
