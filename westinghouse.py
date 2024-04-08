import asyncio
import os
import select
from subprocess import run
from time import sleep

import gpiod
from mpd import MPDClient

CHIP = gpiod.Chip("gpiochip4", gpiod.Chip.OPEN_BY_NAME)  # Raspberry Pi 5 spec


class Output:
    def __init__(
        self,
        gpio_pin_num,
        normally_closed: bool = False,
        toggle_delay: float = 1.0,
        chip: gpiod.Chip = CHIP,
    ):
        self._value_initialized = False
        pinctrl_get = str(run(["pinctrl", "get", "12"], capture_output=True))
        if "| lo " in pinctrl_get:
            self._initial_value = 0
        else:
            self._initial_value = 1

        self._pin: int = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed

        self.toggle_delay = toggle_delay

        self._line: gpiod.Line = chip.get_line(gpio_pin_num)
        self._line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

    def __del__(self):
        self._line.release()

    @property
    def value(self):
        if not self._value_initialized:
            return self._initial_value
        else:
            return self._line.get_value()

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
            sleep(self.toggle_delay)
            return 1
        else:
            self._line.set_value(0)
            sleep(self.toggle_delay)
            return 0

    def on(self):
        if self.is_off:
            return True, self.toggle_on_off()
        else:
            return False, None

    def off(self):
        if self.is_on:
            self.toggle_on_off()
        else:
            return False

    def blink(self, seconds: [int, float]):
        blink_delay = seconds - self.toggle_delay
        self.toggle_on_off()
        sleep(blink_delay)
        self.toggle_on_off()
        sleep(blink_delay)
        self.toggle_on_off()
        return True


class Input:
    def __init__(
        self, gpio_pin_num: int, normally_closed: bool = False, chip: gpiod.Chip = CHIP
    ):
        self._pin: int = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed

        self._line: gpiod.Line = chip.get_line(gpio_pin_num)
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

        print("Updating....")
        client.update()

        print("Adding library to queue....")
        client.clear()
        for root, dirs, files in os.walk(music_path):
            for filename in files:
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
                        p = p.strip("/mnt/")
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


# async def bulb1():
#     print(1)
#     await asyncio.sleep(1)
#     print(2)
#
#
# async def bulb2():
#     print(3)
#     await asyncio.sleep(1.5)
#     print(4)
#
#
# async def main():
#     async with asyncio.TaskGroup() as tg:
#         t1 = tg.create_task(bulb1())
#         t2 = tg.create_task(bulb2())


if __name__ == "__main__":
    print("Starting westinghouse.py....")

    print("Normally closed LEDs on GPIO 13, bulbs off")
    led_yellow_nc = Output(13, normally_closed=True)
    led_yellow_nc.off()

    print("Normally open LEDs on GPIO 12, bulbs on")
    led_yellow_no1 = Output(12)
    print(led_yellow_no1._initial_value)
    # print(run(["pinctrl", "get", "12"]))
    print(led_yellow_no1.on())
    print(led_yellow_no1.off())
    print(led_yellow_no1.toggle_on_off())

    #
    # print("LEDs on GPIO 16")
    # led_yellow_no2 = Output(16)
    # led_yellow_no2.off()
    # print("OK", end="\r", sep="")
    # sleep(0.5)
    #
    # print("LEDs on GPIO 27")
    # led_white_no = Output(27)
    # led_white_no.off()
    # print("OK", end="\r", sep="")
    # sleep(0.5)
    # for k, v in mpd_get_status().items():
    #     print(k, v, sep="\t\t")
    #
    # print("Starting processes....")
    # asyncio.run(main())
