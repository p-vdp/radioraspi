from os import system
from time import sleep

from RPi import GPIO


def command(cmd):
    print(cmd)
    system(cmd)


# reset_sw = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(reset_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        print("initial wait")
        GPIO.wait_for_edge(reset_sw, GPIO.FALLING)

        print("edge detected")
        samples = 0
        for i in range(300):
            sleep(0.01)  # iter for 3 secs
            state = GPIO.input(reset_sw)
            if not i % 100:
                print(int(i / 100) + 1, samples, state)
            if state == 0:
                samples += 1
        print(samples)

        if samples < 250:
            print("no action, wait\n")
            sleep(2.0)
        else:
            command("sudo shutdown")
finally:
    GPIO.cleanup()
