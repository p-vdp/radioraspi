from time import sleep

from mpd import MPDClient

import utils

left_knob = utils.Gpio(25, "wait")

client = MPDClient()

while True:
    print("waiting")
    left_knob.wait()
    print("continuing")
    try:
        client.connect("localhost", 6600)
        client.shuffle()
        client.disconnect()
    except ConnectionRefusedError:
        print("Not connected")
    print("sleeping")
    sleep(3)
