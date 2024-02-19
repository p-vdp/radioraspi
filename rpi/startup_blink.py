from time import sleep

from mpd import MPDClient

from bulbs import Bulbs


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False


blink_interval = 1.1  # seconds, cycle duration will be 2x this value
bulb_nc = Bulbs(12, mode="nc")  # GPIO 12 normally closed relay
bulb_no = Bulbs(17, mode="no")  # GPIO 17 normally open relay

while True:
    if get_mpd_status() is True:
        print("alive")
        bulb_nc.on()
        bulb_no.on()
        sleep(1)
    else:
        print("dead")
        bulb_no.off()
        bulb_nc.blink(blink_interval, intensity=2, repeat=2)
