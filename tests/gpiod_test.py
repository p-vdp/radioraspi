from time import sleep

import gpiod
from gpiod.line import Direction, Value

# from gpiod.line import Direction, Value


CHIP = "/dev/gpiochip4"

chip = gpiod.Chip(CHIP)

with gpiod.request_lines(
    CHIP,
    consumer="LED",
    config={
        12: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE, active_low=False
        ),
        13: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE, active_low=True
        ),
        16: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE, active_low=False
        ),
        27: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.INACTIVE, active_low=False
        ),
    },
) as request:
    print(request.get_value(12))
    request.set_value(12, Value.INACTIVE)
    print(request.get_value(12))
    sleep(5)
