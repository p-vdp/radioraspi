import asyncio

import gpiozero
from mpd import CommandError, MPDClient  # noqa

HOST = "localhost"
POLLING_RATE = 0.05
PORT = 6600

# GPIO pins
NC = 16  # LED normally closed
NO = 12  # LED normally open
PP = 4  # play/pause button


def mpd_get_status(host=HOST, port=PORT):
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


def mpd_toggle_pause(host=HOST, port=PORT):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.pause()  # noqa
    finally:
        client.disconnect()
        del client
        return True


async def gpio_play_pause_button(play_pause_gpio: int = PP):
    button = gpiozero.Button(play_pause_gpio)
    initial_value = button.value
    while True:
        if button.value != initial_value:
            print("play/pause")
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


async def processes():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(gpio_play_indicator())
        tg.create_task(gpio_play_pause_button())


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
    print("MPD is alive!")

    print("Starting processes....")
    asyncio.run(processes())

    print("Exiting....")
