import utils

led_nc_yellow = utils.Gpio(13, "op")
led_no_yellow1 = utils.Gpio(12, "op")
led_no_yellow2 = utils.Gpio(16, "op")
led_no_white = utils.Gpio(27, "op")

try:
    while True:
        led_nc_yellow.on()
        led_no_yellow1.off()
        led_no_yellow2.off()
        led_no_white.off()

        # if utils.get_mpd_status() is False:
        #   led_open.blink(1)
        # else:
        #   sleep(1)
finally:
    led_y1.off()
    led_y2.off()
    # led_y3.off()
    led_w1.off()
