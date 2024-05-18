import asyncio
import os
import select
from datetime import timedelta
from time import sleep

import gpiod
from gpiod.line import Bias, Direction, Edge, Value
from mpd import CommandError, MPDClient

CHIP = "/dev/gpiochip4"  # Raspberry Pi 5 spec
HOST = "localhost"
POLLING_RATE = 0.05
PORT = 6600


def mpd_get_status(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        status = client.status()
    finally:
        client.disconnect()
        del client
    return status


def mpd_is_alive(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False
    finally:
        del client


def mpd_startup(host=HOST, port=PORT, music_path="/mnt/SDCARD"):
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


def mpd_toggle_pause(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.pause()
    finally:
        client.disconnect()
        del client


def mpd_previous_track(host=HOST, port=PORT):
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


def mpd_next_track(host=HOST, port=PORT):
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


def mpd_shuffle(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.shuffle()
    finally:
        client.disconnect()
        del client


def mpd_volume_up(v: int = 1,host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.volume("+" + str(v))
    finally:
        client.disconnect()
        del client


def mpd_volume_down(v: int = 1,host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.volume("-" + str(v))
    finally:
        client.disconnect()
        del client


async def gpio_shuffle_button(track_shuffle_button, feedback_gpio):
    button = Input(track_shuffle_button)
    initial_value = button.value

    # feedback = Output(feedback_gpio)  # TODO make global
    while True:
        if button.value != initial_value:
            print("shuffle")
            mpd_shuffle()
            # feedback.on()
            sleep(2)
            # feedback.off()
            initial_value = button.value
        await asyncio.sleep(POLLING_RATE)


async def gpio_play_indicator(play_bulb_gpio: int):
    play_bulb = Output(play_bulb_gpio)
    while True:
        play_state = mpd_get_status()["state"]
        if play_state == "play" and not play_bulb.is_on:
            print('Playing, turning on bulb', play_bulb_gpio)
            play_bulb.on()
            sleep(1)
        elif play_state != "play" and play_bulb.is_on:
            print('Not playing, turning off bulb', play_bulb_gpio)
            play_bulb.off()
            sleep(1)
        await asyncio.sleep(POLLING_RATE)


async def gpio_play_pause_button(play_pause_gpio):
    button = Input(play_pause_gpio)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            print("play/pause")
            mpd_toggle_pause()
            sleep(1)
        await asyncio.sleep(POLLING_RATE)


async def gpio_track_knob(track_previous_gpio, track_next_gpio, feedback_gpio):
    clk = Input(track_previous_gpio)
    dt = Input(track_next_gpio)
    last_state = dt.value
    while True:
        clk_state = clk.value
        dt_state = dt.value

        if clk_state != last_state:
            if dt_state != clk_state:
                print("previous track")
                sleep(1)
                action = mpd_previous_track()

            else:
                print("next track")
                sleep(1)
                action = mpd_next_track()

            # if action is True:  # TODO feedback
            #     feedback = Output(feedback_gpio)
            #     feedback.on()
            #     del feedback

            sleep(POLLING_RATE)

        last_state = clk.value
        await asyncio.sleep(POLLING_RATE)


async def gpio_volume_knob(vol_down_gpio, vol_up_gpio):
    clk = Input(vol_down_gpio)
    dt = Input(vol_up_gpio)
    last_state = dt.value

    while True:
        clk_state = clk.value
        dt_state = dt.value
        if clk_state != last_state:
            if dt_state != clk_state:
                print("volume up")
                mpd_volume_up()
            else:
                print("volume down")
                mpd_volume_down()
        last_state = clk.value
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
        tg.create_task(gpio_play_indicator(play_bulb))
        tg.create_task(gpio_volume_knob(vol_down_gpio, vol_up_gpio))
        tg.create_task(gpio_play_pause_button(play_pause_button))
        tg.create_task(
            gpio_track_knob(track_previous_gpio, track_next_gpio, feedback_bulb)
        )
        tg.create_task(gpio_shuffle_button(track_shuffle_button, feedback_bulb))


class Output:
    def __init__(
        self,
        gpio_pin_num: int,
        normally_closed: bool = False,
        relay_delay: float = 0.3,
        chip: str = CHIP,
    ):
        self._pin: int = gpio_pin_num
        self._normally_closed: bool = normally_closed
        self._normally_open: bool = not normally_closed
        self._relay_delay = relay_delay

        self._line = gpiod.request_lines(
            chip,
            consumer="LED",
            config={
                self._pin: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.INACTIVE,
                    active_low=self._normally_closed,
                ),
            },
        )

    def __del__(self):
        self._line.release()
    
    @property
    def value(self) -> int:
        v = self._line.get_value(self._pin)
        return v.value

    @property
    def is_on(self) -> bool:
        if self._line.get_value(self._pin) == Value.ACTIVE:
            return True
        else:
            return False

    def toggle_on_off(self):
        if self._line.get_value(self._pin) == Value.INACTIVE:
            sleep(self._relay_delay)
            self._line.set_value(self._pin, Value.ACTIVE)
            sleep(self._relay_delay / 2)
            return 1
        else:
            sleep(self._relay_delay)
            self._line.set_value(self._pin, Value.INACTIVE)
            sleep(self._relay_delay / 2)
            return 0

    def on(self) -> bool:
        """Return True if turns on, return False if no change"""
        if self._line.get_value(self._pin) == Value.INACTIVE:
            self._line.set_value(self._pin, Value.ACTIVE)
            return True
        else:
            return False

    def off(self) -> bool:
        """Return True if turns off, return False if no change"""
        if self._line.get_value(self._pin) == Value.ACTIVE:
            self._line.set_value(self._pin, Value.INACTIVE)
            return True
        else:
            return False

    def blink(self, seconds: [int, float]):
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()
        sleep(seconds)
        self.toggle_on_off()


class Input:
    def __init__(self, gpio_pin_num: int, chip_path: str = CHIP):
        self._pin: int = gpio_pin_num
        self._line = gpiod.request_lines(
            chip_path,
            consumer="BUTTON",
            config={
                self._pin: gpiod.LineSettings(
                    edge_detection=Edge.BOTH,
                    bias=Bias.PULL_UP,
                    debounce_period=timedelta(milliseconds=10),
                ),
            },
        )

    def __del__(self):
        self._line.release()

    @property
    def value(self):
        return self._line.get_value(self._pin)

    def wait(self):
        """https://stackoverflow.com/questions/76676779/problem-with-event-wait-in-python3-libgpiod"""
        fd = self._line.wait_edge_events()
        poll = select.poll()
        poll.register(fd)
        poll.poll(None)  # wait here
        event = self._line.read_edge_events()
        return event


if __name__ == "__main__":
    print("Starting westinghouse.py....")
    nc = Output(13, normally_closed=True)
    nc.on()
    nc.off()
    print("Started")

    print("Waiting for MPD....")
    mpd_status_bulb = Output(12, normally_closed=True)
    mpd_status_bulb.on()
    while mpd_is_alive() is False:
        mpd_status_bulb.blink(2)
    mpd_status_bulb.off()
    sleep(2)

    print("Setting up MPD....")
    mpd_startup()

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

    print("Done")
