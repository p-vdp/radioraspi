from time import sleep

import utils

# LED control
led_closed = utils.Gpio(12, "op")
led_open = utils.Gpio(17, "op")

try:
    while True:
        led_closed.on()
        led_open.on()

        if utils.get_mpd_status() is False:
            led_open.blink(1)
finally:
    led_closed.off()
    led_open.off()
    utils.chip.close()
