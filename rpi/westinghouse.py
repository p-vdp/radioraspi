from time import sleep

import gpiod
from mpd import MPDClient


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False


NC_PIN = 12
NO_PIN = 17

chip = gpiod.Chip('gpiochip4')
led_line = chip.get_line(NO_PIN)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

while True:
    if get_mpd_status() is True:
        # print("alive")
        led_line.set_value(1)
        sleep(1)
    else:
        print("dead")
        led_line.set_value(0)
        sleep(0.75)
        led_line.set_value(1)
        sleep(0.75)
