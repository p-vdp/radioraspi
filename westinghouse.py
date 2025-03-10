import asyncio
from subprocess import run

import gpiozero
from mpd import CommandError, MPDClient  # noqa


HOST = "localhost"
POLLING_RATE = 0.05
PORT = 6600

# GPIO pins
NC = 16  # LED normally closed
NO = 12  # LED normally open
PP = 4  # play/pause button
SB = 17  # shuffle button
TN = 5  # track next on rotary encoder
TP = 6  # track previous on rotary encoder
VD = 23  # volume down on rotary encoder
VU = 24  # volume up on rotary encoder


def mpd_get_status(host=HOST, port=PORT) -> str:
    client = MPDClient()
    status = None

    try:
        client.connect(host, port)
        status = client.status()  # noqa
    finally:
        client.disconnect()
        del client
        return status


def mpd_is_alive(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
    except ConnectionRefusedError:
        return False
    finally:
        client.disconnect()
        del client
        return True


def mpd_shuffle(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.shuffle()  # noqa
    finally:
        client.disconnect()
        del client


def mpd_toggle_pause(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.pause()  # noqa
    finally:
        client.disconnect()
        del client
        return True


def mpd_previous_track(host=HOST, port=PORT):
    client = MPDClient()
    cmd = None
    try:
        client.connect(host, port)
        client.previous()  # noqa
        cmd = True
    except CommandError:
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
        client.next()  # noqa
        cmd = True
    except CommandError:
        cmd = False
    finally:
        client.disconnect()
        del client
        return cmd


def mpd_volume_down(increment: int = 1):
    run(f"/var/www/util/vol.sh -dn {increment}", shell=True)


def mpd_volume_up(increment: int = 1):
    run(f"/var/www/util/vol.sh -up {increment}", shell=True)


def mpd_volume_get():
    out = run(f"/var/www/util/vol.sh", shell=True, capture_output=True)
    return int(out.stdout.decode().strip())


def mpd_volume_set(volume: int):
    run(f"/var/www/util/vol.sh {volume}", shell=True)


async def gpio_play_pause_button(play_pause_gpio: int = PP):
    button = gpiozero.Button(play_pause_gpio)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            print("play/pause")
            await asyncio.sleep(0.2)
            mpd_toggle_pause()
            await asyncio.sleep(1)

        await asyncio.sleep(POLLING_RATE)


async def gpio_play_indicator():
    last_state = None
    while True:
        play_state = mpd_get_status()["state"]
        if last_state != play_state:
            if play_state == "play":
                print("Playing, turning on bulb")
                led_no.on()
            elif play_state != "play":
                print("Not playing, turning off bulb")
                led_no.off()
            last_state = play_state
            await asyncio.sleep(1)

        await asyncio.sleep(POLLING_RATE)


async def gpio_shuffle_button(track_shuffle_button: int = SB):
    button = gpiozero.Button(track_shuffle_button)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            print("shuffle")
            mpd_shuffle()

            await asyncio.sleep(0.2)
            led_no.off()
            await asyncio.sleep(0.1)
            led_no.on()

            await asyncio.sleep(1)
        await asyncio.sleep(POLLING_RATE)


async def gpio_track_knob(track_previous_gpio: int = TP, track_next_gpio: int = TN):
    rotor = gpiozero.RotaryEncoder(
        track_previous_gpio, track_next_gpio, bounce_time=0.01
    )

    last_value = rotor.value
    while True:
        current_value = rotor.value

        if current_value < last_value:
            print("previous track")
            mpd_previous_track()

            led_no.off()
            await asyncio.sleep(0.1)
            led_no.on()
            await asyncio.sleep(3)

        if current_value > last_value:
            print("next track")
            mpd_next_track()

            led_no.off()
            await asyncio.sleep(0.1)
            led_no.on()
            await asyncio.sleep(3)

        last_value = rotor.value
        await asyncio.sleep(POLLING_RATE)


async def gpio_volume_knob(
    volume_down_gpio: int = VD,
    volume_up_gpio: int = VU,
    min_vol: int = 0,
    max_vol: int = 50,
):
    rotor = gpiozero.RotaryEncoder(
        volume_down_gpio,
        volume_up_gpio,
        bounce_time=0.01,
        max_steps=max_vol,
        threshold_steps=(min_vol, max_vol),
        wrap=False,
    )

    rotor.steps = mpd_volume_get()

    last_value = rotor.steps
    while True:
        if rotor.steps <= min_vol:
            rotor.steps = min_vol

        if rotor.steps >= max_vol:
            rotor.steps = max_vol

        current_steps = rotor.steps

        if current_steps != last_value:
            mpd_volume_set(current_steps)
            last_value = current_steps
            print(f"volume set to {current_steps}")

        await asyncio.sleep(POLLING_RATE)


async def processes():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(gpio_play_indicator())
        tg.create_task(gpio_play_pause_button())
        tg.create_task(gpio_shuffle_button())
        tg.create_task(gpio_track_knob())
        tg.create_task(gpio_volume_knob())


print("Starting westinghouse.py....")
led_nc = gpiozero.LED(NC)
led_no = gpiozero.LED(NO)

if __name__ == "__main__":
    print("Blinking once....")
    led_nc.blink(1, 1, 1, background=False)
    led_no.blink(1, 1, 1, background=False)

    print("Waiting for MPD....")
    while mpd_is_alive() is False:
        print("MPD is down, blinking....")
        led_nc.blink(2, 2, 1, background=False)

    print("MPD is alive! Status:")
    print(mpd_get_status())

    print("Starting processes....")
    asyncio.run(processes())

    print("Exiting....")
