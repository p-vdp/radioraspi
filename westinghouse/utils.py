import select
from time import sleep

import gpiod
from mpd import MPDClient


chip = gpiod.Chip("gpiochip4")


class Gpio:
    def __init__(self, pin_num, type: str, gpiod_chip=chip):
        self.line = gpiod_chip.get_line(pin_num)
        self.type = type

        if self.type == "ip":
            raise NotImplementedError
            # self.line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        elif self.type == "op":
            self.line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
        elif self.type == "wait":
            self.line.request(
                consumer="GPOUT",
                type=gpiod.LINE_REQ_EV_FALLING_EDGE,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
        else:
            raise ValueError

    def on(self):
        if self.type != "op":
            raise TypeError('Expected type output "op"')
        else:
            self.line.set_value(1)

    def off(self):
        if self.type != "op":
            raise TypeError('Expected type output "op"')
        else:
            self.line.set_value(0)

    def toggle(self):
        if self.type != "op":
            raise TypeError('Expected type output "op"')
        else:
            if self.line.get_value() == 0:
                self.line.set_value(1)
            else:
                self.line.set_value(0)

    def blink(self, seconds: [int, float]):
        if self.type != "op":
            raise TypeError('Expected type output "op"')
        else:
            self.toggle()
            sleep(seconds)
            self.toggle()
            sleep(seconds)
            self.toggle()

    def wait(self):
        if self.type != "wait":
            raise TypeError("Expected type wait")
        else:  # https://stackoverflow.com/questions/76676779/problem-with-event-wait-in-python3-libgpiod
            fd = self.line.event_get_fd()
            poll = select.poll()
            poll.register(fd)
            poll.poll(None)  # wait here
            event = self.line.event_read()
            return event

    def get_value(self):
        return self.line.get_value()


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False
