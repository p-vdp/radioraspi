from time import sleep

from mpd import MPDClient

import utils


right_knob = utils.Gpio(25, "wait")

client = MPDClient()

while True:
    right_knob.wait()
    try:
        client.connect("localhost", 6600)
        # cmd here
        client.disconnect()
    except ConnectionRefusedError:
        print("Not connected")
    sleep(1)
