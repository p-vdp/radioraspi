from time import sleep

from mpd import MPDClient

import utils


left_knob = utils.Gpio(4, "wait")
print("waiting")
left_knob.wait()
print("continuing")

client = MPDClient()
try:
    client.connect("localhost", 6600)
    print("play/pause")
    client.pause()  # noqa
except ConnectionRefusedError:
    print("Not connected")
finally:
    client.disconnect()
    left_knob.line.release()
    print("sleeping")
    sleep(3)
