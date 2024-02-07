from time import sleep

from mpd import MPDClient

from bulbs import Bulbs


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False


blink_interval = 1.1  # seconds, cycle duration will be 2x this value
bulb = Bulbs(12)  # GPIO 12

while True:
    if get_mpd_status() is True:
        print("alive")
        bulb.on()
        break
    else:
        print("dead")
        bulb.blink(blink_interval, intensity=2, repeat=2)
