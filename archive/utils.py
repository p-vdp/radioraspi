import select
from time import sleep

import python_gpiod
from mpd import MPDClient


CHIP = gpiod.Chip("gpiochip4")  # Raspberry Pi 5 spec


class Line(gpiod.Line):
    pass


class Input:
    def __init__(self, pin_num: int, io_type: str, circuit_type: str = "open"):
        try:
            assert pin_num.is_integer()
            assert io_type in ["ip", "op", "wait"]
            assert circuit_type in ["open", "closed"]
        except AssertionError:
            raise TypeError

        self.line = CHIP.get_line(pin_num)
        self.io_type = io_type

        if self.io_type == "ip":
            raise NotImplementedError
            # self.line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        elif self.io_type == "op":
            self.line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
        elif self.io_type == "wait":
            self.line.request(
                consumer="GPOUT",
                type=gpiod.LINE_REQ_EV_FALLING_EDGE,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
        else:
            raise ValueError

    def on(self):
        self.line.set_value(1)

    def off(self):
        self.line.set_value(0)

    def toggle(self):
        if self.line.get_value() == 0:
            self.line.set_value(1)
        else:
            self.line.set_value(0)

    def blink(self, seconds: [int, float]):
        self.toggle()
        sleep(seconds)
        self.toggle()
        sleep(seconds)
        self.toggle()

    def wait(self):
        """https://stackoverflow.com/questions/76676779/problem-with-event-wait-in-python3-libgpiod"""
        fd = self.line.event_get_fd()
        poll = select.poll()
        poll.register(fd)
        poll.poll(None)  # wait here
        event = self.line.event_read()
        return event

    def get_value(self):
        return self.line.get_value()


class Output:
    def __init__(self):
        pass


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False
