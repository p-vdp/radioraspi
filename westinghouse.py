import os
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


def mpd_get_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        status = client.status()
    finally:
        client.disconnect()
        del client
    return status


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


def mpd_startup(host="localhost", port=6600, music_path="/mnt/SDCARD"):
    client = MPDClient()
    try:
        client.connect(host, port)

        client.clear()

        for root, dirs, files in os.walk(music_path):
            for filename in files:
                print(filename)
                if filename.split(".")[-1].lower() in [
                    "mp3",
                    "flac",
                    "mp4",
                    "m4a",
                    "aiff",
                    "aac",
                ]:
                    p = os.path.join(root, filename)
                    if p.startswith("/mnt/"):
                        p.strip("/mnt/")
                    client.add(p)

        client.shuffle()
        client.play()
    finally:
        client.disconnect()
        del client


def mpd_toggle_pause(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.pause()
    finally:
        client.disconnect()
        del client


if __name__ == "__main__":
    print(mpd_get_status())
    print("Startup....")
    mpd_startup()
    print(mpd_get_status())
