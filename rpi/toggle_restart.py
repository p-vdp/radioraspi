from os import system
from time import sleep

from RPi import GPIO

from bulbs import Bulbs


def command(cmd):
    print(cmd)
    system(cmd)


sw = 26
wait = 3  # seconds
cmd = "sudo reboot now"

GPIO.setmode(GPIO.BCM)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        print("initial wait")
        GPIO.wait_for_edge(sw, GPIO.FALLING)

        print("edge detected")
        samples = 0
        for i in range(wait * 100):
            sleep(0.01)  # iter for 5 secs
            state = GPIO.input(sw)
            if not i % 100:
                print(int(i / 100) + 1, samples, state)
            if state == 0:
                samples += 1
        print(samples)

        if samples < wait * 80:
            print("no action, wait\n")
            sleep(1.0)
        else:
            b = Bulbs(12)
            b.blink(repeat=2)
            command(cmd)
            break
finally:
    GPIO.cleanup()
