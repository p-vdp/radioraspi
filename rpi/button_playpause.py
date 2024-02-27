from time import sleep

import gpiod
from mpd import MPDClient


BUTTON_PIN = 4
DEBOUNCE = 1.0  # seconds
POLLING_WAIT = 0.01  # seconds

chip = gpiod.Chip("gpiochip4")
button_line = chip.get_line(BUTTON_PIN)
button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

try:
    while True:
        button_state = button_line.get_value()
        client = MPDClient()
        if button_state == 0:
            client.connect("localhost", 6600)
            status = client.status()
            if status["state"] == "stop":
                client.play()
            else:
                client.pause()
            print(status)
            sleep(DEBOUNCE)
        sleep(POLLING_WAIT)
finally:
    button_line.release()
