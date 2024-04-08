import asyncio
import os
import select
from subprocess import run
from time import sleep

import gpiod
from mpd import MPDClient

CHIP = gpiod.Chip("gpiochip4", gpiod.Chip.OPEN_BY_NAME)  # Raspberry Pi 5 spec
POLLING_RATE = 0.1


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


async def mpd_status_indicator(status_bulb: int):
    status_bulb = Output(status_bulb)
    status_bulb.on()

    while True:
        if mpd_is_alive() is False:
            status_bulb.blink(0.3)
        await asyncio.sleep(POLLING_RATE)


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

    counter = 0
    last_state = dt.value
    while True:
        clk_state = clk.value
        dt_state = dt.value

        if clk_state != last_state:
            if dt_state != clk_state:
                counter += 1
                rotation_direction = "R"
            else:
                counter -= 1
                rotation_direction = "L"

            if rotation_direction == "R":
                # print(counter, rotation_direction)
                run("/var/www/vol.sh -up 1".split(" "))

            if rotation_direction == "L":
                # print(counter, rotation_direction)
                run("/var/www/vol.sh -dn 1".split(" "))

        last_state = clk.value
        await asyncio.sleep(0.01)


async def mpd_play_pause_button(play_pause_gpio):
    pass


async def mpd_track_knob(track_previous_gpio, track_next_gpio, feedback_gpio):
    pass


async def mpd_shuffle_button(track_shuffle_button, feedback_gpio):
    pass


async def processes(
    nc_bulb,
    indicator_bulb,
    play_bulb,
    feedback_bulb,
    vol_down_gpio,
    vol_up_gpio,
    track_previous_gpio,
    track_next_gpio,
    play_pause_button,
    track_shuffle_button,
):
    nc = Output(nc_bulb, normally_closed=True)
    nc.off()
    print("Started")

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mpd_status_indicator(indicator_bulb))
        tg.create_task(mpd_play_indicator(play_bulb))
        tg.create_task(mpd_volume_knob(vol_down_gpio, vol_up_gpio))
        tg.create_task(mpd_play_pause_button(play_pause_button))
        tg.create_task(
            mpd_track_knob(track_previous_gpio, track_next_gpio, feedback_bulb)
        )
        tg.create_task(mpd_shuffle_button(track_shuffle_button, feedback_bulb))


if __name__ == "__main__":
    print("Starting westinghouse.py....")

    # print("Normally closed LEDs on GPIO 13, bulbs off")

    # print("Normally open LEDs on GPIO 12, bulbs on")
    # led_yellow_no1 = Output(12, normally_closed=False)
    # led_yellow_no1.on()

    # print("Normally open LEDs on GPIO 16, bulbs off")
    # led_yellow_no2 = Output(16, normally_closed=False)
    # print("Normally open LEDs on GPIO 27, bulbs off")
    # led_white_no = Output(27, normally_closed=False)

    print("Setting up MPD....")
    mpd_startup()

    print("Starting processes....")
    asyncio.run(
        processes(
            nc_bulb=13,
            indicator_bulb=12,
            play_bulb=27,
            feedback_bulb=16,
            vol_down_gpio=23,
            vol_up_gpio=24,
            track_previous_gpio=4,
            track_next_gpio=5,
            play_pause_button=17,
            track_shuffle_button=6,
        )
    )

print("Exiting....")
