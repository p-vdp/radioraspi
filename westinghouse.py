import asyncio
import os
import select
from subprocess import run
from time import sleep

import gpiod  # noqa
from mpd import CommandError, MPDClient

CHIP = gpiod.Chip("gpiochip4", gpiod.Chip.OPEN_BY_NAME)  # Raspberry Pi 5 spec
POLLING_RATE = 0.05


class Output:
    def __init__(
        self,
        gpio_pin_num: int,
        normally_closed: bool = False,
        relay_delay: float = 0.3,
        chip: gpiod.Chip = CHIP,
    ):
        self._pin = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed
        self._relay_delay = relay_delay

        self._line: gpiod.Line = chip.get_line(self._pin)
        self._line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

    def __del__(self):
        self._line.set_value(0)
        self._line.release()

    @property
    def value(self) -> int:
        return self._line.get_value()

    def toggle_on_off(self):
        if self._line.get_value() == 0:
            sleep(self._relay_delay)
            self._line.set_value(1)
            sleep(self._relay_delay / 2)
            return 1
        else:
            sleep(self._relay_delay)
            self._line.set_value(0)
            sleep(self._relay_delay / 2)
            return 0

    def on(self) -> bool:
        """Return True if turns on, return False if no change"""
        value = self._line.get_value()
        if self._normally_closed is False and value == 0:
            self.toggle_on_off()
            return True
        elif self._normally_closed is True and value == 1:
            self.toggle_on_off()
            return True
        else:
            return False

    def off(self) -> bool:
        """Return True if turns off, return False if no change"""
        value = self._line.get_value()
        if self._normally_closed is False and value == 1:
            self.toggle_on_off()
            return True
        elif self._normally_closed is True and value == 0:
            self.toggle_on_off()
            return True
        else:
            return False

    def reset(self):
        self._line.set_value(0)

    def blink(self, seconds: [int, float]):
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()


class Input:
    def __init__(self, gpio_pin_num: int, chip: gpiod.Chip = CHIP):
        self._pin: int = gpio_pin_num
        self._line: gpiod.Line = chip.get_line(gpio_pin_num)
        self._line.request(
            consumer="GPOUT",
            type=gpiod.LINE_REQ_EV_FALLING_EDGE,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
        )

    def __del__(self):
        self._line.release()

    @property
    def value(self) -> int:
        return self._line.get_value()

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

        print("Updating library....")
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


def mpd_previous_track(host="localhost", port=6600):
    client = MPDClient()
    cmd = None
    try:
        client.connect(host, port)
        client.previous()
        cmd = True
    except CommandError:
        sleep(1)
        cmd = False
    finally:
        client.disconnect()
        del client
        return cmd


def mpd_next_track(host="localhost", port=6600):
    client = MPDClient()
    cmd = None
    try:
        client.connect(host, port)
        client.next()
        cmd = True
    except CommandError:
        sleep(1)
        cmd = False
    finally:
        client.disconnect()
        del client
        return cmd


def mpd_shuffle(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.shuffle()
    finally:
        client.disconnect()
        del client


async def mpd_play_indicator(play_bulb: int):
    play_bulb = Output(play_bulb)
    while True:
        if mpd_get_status()["state"] == "play":
            play_bulb.on()
        else:
            play_bulb.off()
        await asyncio.sleep(POLLING_RATE)


async def mpd_volume_knob(vol_down_gpio, vol_up_gpio):
    clk = Input(vol_down_gpio)
    dt = Input(vol_up_gpio)
    last_state = dt.value

    while True:
        clk_state = clk.value
        dt_state = dt.value
        if clk_state != last_state:
            if dt_state != clk_state:
                run("/var/www/vol.sh -up 1".split(" "))
            else:
                run("/var/www/vol.sh -dn 1".split(" "))
            print("volume =", mpd_get_status()["volume"])
        last_state = clk.value
        await asyncio.sleep(0.01)


async def mpd_play_pause_button(play_pause_gpio):
    button = Input(play_pause_gpio)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            print("play/pause")
            mpd_toggle_pause()
        await asyncio.sleep(POLLING_RATE)


async def mpd_track_knob(track_previous_gpio, track_next_gpio, feedback_gpio):
    clk = Input(track_previous_gpio)
    dt = Input(track_next_gpio)
    last_state = dt.value
    while True:
        clk_state = clk.value
        dt_state = dt.value

        if clk_state != last_state:
            if dt_state != clk_state:
                action = mpd_previous_track()
            else:
                action = mpd_next_track()

            if action is True:
                feedback = Output(feedback_gpio)
                feedback.on()
                del feedback

            sleep(POLLING_RATE)

        last_state = clk.value
        await asyncio.sleep(POLLING_RATE)


async def mpd_shuffle_button(track_shuffle_button, feedback_gpio):
    button = Input(track_shuffle_button)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            feedback = Output(feedback_gpio)
            feedback.on()

            mpd_shuffle()
            print("shuffle")

            del feedback

            sleep(POLLING_RATE)
        await asyncio.sleep(POLLING_RATE)


async def processes(
    play_bulb,
    feedback_bulb,
    vol_down_gpio,
    vol_up_gpio,
    track_previous_gpio,
    track_next_gpio,
    play_pause_button,
    track_shuffle_button,
):
    async with asyncio.TaskGroup() as tg:
        tg.create_task(mpd_play_indicator(play_bulb))
        tg.create_task(mpd_volume_knob(vol_down_gpio, vol_up_gpio))
        tg.create_task(mpd_play_pause_button(play_pause_button))
        tg.create_task(
            mpd_track_knob(track_previous_gpio, track_next_gpio, feedback_bulb)
        )
        tg.create_task(mpd_shuffle_button(track_shuffle_button, feedback_bulb))


if __name__ == "__main__":
    print("Starting westinghouse.py....")
    nc = Output(13, normally_closed=True)
    nc.off()
    print("Started")

    print("Waiting for MPD....")
    mpd_boot_status_bulb = Output(12)
    mpd_boot_status_bulb.on()
    while mpd_is_alive() is False:
        mpd_boot_status_bulb.blink(2)
    sleep(2)

    print("Starting processes....")
    asyncio.run(
        processes(
            play_bulb=27,
            feedback_bulb=16,
            vol_down_gpio=23,
            vol_up_gpio=24,
            track_previous_gpio=5,
            track_next_gpio=6,
            play_pause_button=4,
            track_shuffle_button=17,
        )
    )
    sleep(5)

    print("Setting up MPD....")
    mpd_startup()

    print("Done")
