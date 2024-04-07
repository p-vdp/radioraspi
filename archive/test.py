import os
from subprocess import run
from sys import argv
from time import sleep

from mpd import MPDClient

print("start")
client = MPDClient()
client.connect("localhost", 6600)
run(['rm', '/var/lib/mpd/music/ESPEAK/temp.wav'])
run(['espeak', '-w', '/var/lib/mpd/music/ESPEAK/temp.wav', '-s', '120', '\"' + argv[1] + '\"'])
client.clear()
client.update("ESPEAK/temp.wav")

client.add("ESPEAK/temp.wav")
client.play()
sleep(5)
client.clear()
for root, dirs, files in os.walk("/mnt/SDCARD"):
    for filename in files:
        if filename.split(".")[-1] in ["mp3", "flac", "mp4", "m4a", "aiff", "aac"]:
            p = os.path.join(root, filename).strip("/mnt/")
            print(p)
            client.add(p)

client.shuffle()
client.play()
client.disconnect()
print("done")
