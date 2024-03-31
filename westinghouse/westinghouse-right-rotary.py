from time import sleep

import gpiod
from mpd import MPDClient

from utils import chip

sleep(5)

debounce = 0.01  # seconds
clk = chip.get_line(6)
dt = chip.get_line(5)

clk.request(
    consumer="Button",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)
dt.request(
    consumer="Button",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)

counter = 0
rotation_direction = None
clk_last_state = dt.get_value()

while True:
    clk_state = clk.get_value()
    dt_state = dt.get_value()

    if clk_state != clk_last_state:
        if dt_state != clk_state:
            counter += 1
            rotation_direction = "R"
        else:
            counter -= 1
            rotation_direction = "L"
    else:
        rotation_direction = "0"

    print(
        clk_state,
        dt_state,
        rotation_direction,
        str(counter).zfill(3),
        sep=" ",
        end="\r",
    )

    client = MPDClient()
    client.connect("localhost", port=6600)
    if rotation_direction == "R":
        client.next()
        sleep(0.5)
    elif rotation_direction == "L":
        client.previous()
        sleep(0.5)
    else:
        pass  # TODO

    # reinitialize
    client.disconnect()
    rotation_direction = None
    clk_last_state = clk_state
    sleep(debounce)
