from time import sleep

from mpd import MPDClient
from RPi import GPIO


debounce = 0.01  # seconds
clk = 27
dt = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 0
rotation_direction = None
clk_last_state = GPIO.input(clk)

try:
    while True:
        GPIO.wait_for_edge(clk, GPIO.BOTH)
        # get state
        clk_state = GPIO.input(clk)
        dt_state = GPIO.input(dt)

        if clk_state != clk_last_state:
            if dt_state != clk_state:
                counter += 1
                rotation_direction = "clockwise"
            else:
                counter -= 1
                rotation_direction = "counterclockwise"

        # do mpd command
        if rotation_direction:
            try:
                # print(counter, rotation_direction)
                client = MPDClient()
                client.connect("localhost", 6600)
                status = client.status()
                # print(status['playlistlength'], status['song'])
                if rotation_direction == "clockwise" and int(status['song']) < int(status['playlistlength']) - 1:
                    client.next()
                if rotation_direction == "counterclockwise":
                    client.previous()
            finally:
                # print(status['playlistlength'], status['song'])
                client.disconnect()

        # reinitialize
        rotation_direction = None
        clk_last_state = clk_state
        sleep(debounce)
finally:
    GPIO.cleanup()

