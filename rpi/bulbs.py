import time
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Bulbs:
    def __init__(self, gpin, init_on=True):
        self.gpin = gpin
        self.init_on = init_on

        GPIO.setup(gpin, GPIO.OUT)
        self.initialize()

    def blink(self, interval: float = 1.0, intensity: int = 10, repeat=1):
        """
        :param repeat:
        :type repeat:
        :param interval: seconds off then on, total time is 2x or 3x interval
        :type interval: float
        :param intensity: 1 to 10, will cycle bulb for lower brightness
        :type intensity: int
        """
        if 1 < intensity > 10:
            raise ValueError("Intensity must be int from 1 to 10")

        hertz = (intensity * 4) + 20  # intensity 1 to 10 translates to 24 to 60 hertz

        if self.gpio_status():  # if off turn on first
            for i in range(repeat):
                self.cycle(hertz, interval)
                time.sleep(interval)
                self.off()
                time.sleep(interval)
        else:  # if on turn off first
            self.off()
            time.sleep(interval)
            if repeat > 1:
                for i in range(repeat - 1):
                    self.cycle(hertz, interval)
                    time.sleep(interval)
                    self.off()
                    time.sleep(interval)
            self.on()

    def cycle(self, hertz: float = 1.0, period: float = 1.0):
        s = 1 / hertz
        cycles = int(hertz * period)
        print(s, cycles)
        for i in range(cycles):
            self.toggle()
            time.sleep(s)
            self.toggle()
            time.sleep(s)

    def gpio_status(self):
        return GPIO.input(self.gpin)

    def initialize(self):
        if self.init_on:
            self.on()
        else:
            self.off()

    def on(self):
        GPIO.output(self.gpin, GPIO.LOW)

    def off(self):
        GPIO.output(self.gpin, GPIO.HIGH)

    def toggle(self):
        if GPIO.input(self.gpin):  # NC relay means 1 is off
            self.on()
        else:
            self.off()

    def __del__(self):
        GPIO.cleanup(self.gpin)
