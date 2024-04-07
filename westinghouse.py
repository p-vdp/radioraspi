import select
from time import sleep

import gpiod
from mpd import MPDClient

CHIP = gpiod.Chip("gpiochip4", gpiod.Chip.OPEN_BY_NAME)  # Raspberry Pi 5 spec


class Line:
    def __init__(self, gpio_pin_num: int):
        self._line: gpiod.Line = CHIP.get_line(gpio_pin_num)

    def __del__(self):
        self._line.release()

    @property
    def value(self):
        return self._line.get_value()


class Output(Line):
    def __init__(self, gpio_pin_num, normally_closed: bool = False):
        super().__init__(gpio_pin_num=gpio_pin_num)
        self._pin: int = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed

        self._line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

    @property
    def is_off(self):
        if self._normally_open is True:
            if self.value == 0:
                return True
            else:
                return False
        else:  # normally closed
            if self.value == 0:
                return False
            else:
                return True

    @property
    def is_on(self):
        if self._normally_open is True:
            if self.value == 1:
                return True
            else:
                return False
        else:  # normally closed
            if self.value == 1:
                return False
            else:
                return True

    def toggle_on_off(self):
        if self.value == 0:
            self._line.set_value(1)
        else:
            self._line.set_value(0)

    def on(self):
        if self.is_off:
            self.toggle_on_off()

    def off(self):
        if self.is_on:
            self.toggle_on_off()

    def blink(self, seconds: [int, float]):
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()


class Input(Line):
    def __init__(self, gpio_pin_num: int, normally_closed: bool = False):
        super().__init__(gpio_pin_num)
        self._pin: int = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed

        self._line.request(
            consumer="GPOUT",
            type=gpiod.LINE_REQ_EV_FALLING_EDGE,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
        )

    def wait(self):
        """https://stackoverflow.com/questions/76676779/problem-with-event-wait-in-python3-libgpiod"""
        fd = self._line.event_get_fd()
        poll = select.poll()
        poll.register(fd)
        poll.poll(None)  # wait here
        event = self._line.event_read()
        return event


def mpd_is_alive(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False
    finally:
        del client


def mpd_toggle_pause(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.pause()
    finally:
        client.disconnect()
        del client


led_yellow_nc = Output(13, normally_closed=True)
led_yellow_no1 = Output(12)
led_yellow_no2 = Output(16)
led_white_no = Output(27)

# while True:
#     response = mpd_is_alive()
#     print(response)
#     if response is True:
#         subprocess.run(["sudo", "killall", "mpd"])
#     sleep(1)

print(mpd_is_alive())
mpd_toggle_pause()
