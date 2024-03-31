from time import sleep

import gpiod
from mpd import MPDClient


print("Setting up....")

chip = gpiod.Chip("gpiochip4")


class Gpio:
    def __init__(self, pin_num, direction: str, gpiod_chip=chip):
        self.line = gpiod_chip.get_line(pin_num)
        self.direction = direction

        if self.direction == "ip":
            self.line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        elif self.direction == "op":
            self.line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
        else:
            raise ValueError('Direction must be input "ip" or output "op"')

    def on(self):
        if self.direction == "ip":
            raise TypeError('Expected direction output "op"')
        else:
            self.line.set_value(1)

    def off(self):
        if self.direction == "ip":
            raise TypeError('Expected direction output "op"')
        else:
            self.line.set_value(0)

    def toggle(self):
        if self.direction == "ip":
            raise TypeError('Expected direction output "op"')
        else:
            if self.line.get_value() == 0:
                self.line.set_value(1)
            else:
                self.line.set_value(0)

    def blink(self, seconds: [int, float]):
        if self.direction == "ip":
            raise TypeError('Expected direction output "op"')
        else:
            self.toggle()
            sleep(seconds)
            self.toggle()
            sleep(seconds)
            self.toggle()


def get_mpd_status(host="localhost", port=6600):
    client = MPDClient()
    try:
        client.connect(host, port)
        client.disconnect()
        return True
    except ConnectionRefusedError:
        return False


#
# # left rotary encoder
# rot_left_1 = Gpio(23, "ip")
# rot_left_2 = Gpio(24, "ip")
# rot_left_sw = Gpio(4, "ip")
#
# # right rotary encoder
# rot_right_1 = Gpio(5, "ip")
# rot_right_2 = Gpio(6, "ip")
# rot_right_sw = Gpio(25, "ip")
#
#
# led_closed.off()
# led_open.off()
# sleep(1)
# led_closed.on()
# sleep(5)
# led_closed.off()
# led_closed.blink(2)
# led_open.blink(1)


# status = dict()
# try:
#     while True:
#         status["action"] = None
#
#         status["mpd"] = get_mpd_status()
#         if status["mpd"] is True:
#             status["action"] = "led on"
#         else:
#             status["action"] = "led blink"
#         print(status, sep="", end="\r")
#         sleep(1)
# finally:
#     led_open.set_value(0)
#     chip.close()
