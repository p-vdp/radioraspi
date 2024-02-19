import os
from time import sleep

from mpd import MPDClient


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False


# status = client.status()
path = "/mnt/SDCARD/Default Playlist/"

songs = os.listdir(path)
print(songs)

try:
    while get_mpd_status() is False:
        sleep(1)

    sleep(10)
    client = MPDClient()
    client.connect("localhost", 6600)

    client.clear()

    client.load("Default Playlist")
    client.playlistclear("Default Playlist")

    for s in songs:
        client.add(os.path.join("SDCARD/Default Playlist/", s))

    client.shuffle()
    # client.random(1)
    client.repeat(1)
    client.play(0)
finally:
    client.disconnect()  # noqa
