#TXFM Trackservice

A script that returns the name of the Song that is currently played (or was last played) on the Irish Independent Radio TXFM!

## API

For simply fetching the currently played song invoke

    now_playing()
from the *txfmtracker* module

For storing things to the Redis-DB first create a storage-manager object

     from storagemanager import StorageManager
     sm = StorageManager()

For adding the currently played song to the DB call

     sm.add_song(now_playing())

For retrieving the song played at a certain time call (watch the formatting)

     sm.get_song(date="%Y.%m.%d %H:%M:%S")

For retrieving a dictionary of all stored songs call

     sm.get_all_songs()
