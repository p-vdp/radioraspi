from subprocess import run
from time import sleep
import unittest

import westinghouse


class AutomatedTestCases(unittest.TestCase):
    def test_leds(self):
        gpio_pins = {12: False, 13: True, 16: False, 27: False}

        print("activating....")
        activated_pins = list()
        for p in gpio_pins:
            normally_closed = gpio_pins[p]
            pin = westinghouse.Output(gpio_pin_num=p, normally_closed=normally_closed)
            initial = pin.value
            print("pin:", p, "initial:", initial, "nc:", normally_closed)
            pin.off()
            activated_pins.append(pin)

        for pin in activated_pins:
            initial = pin.value

            pin.toggle_on_off()
            self.assertNotEqual(pin.value, initial)
            sleep(1)

            pin.toggle_on_off()
            self.assertEqual(pin.value, initial)
            sleep(1)

            pin.off()
            sleep(0.5)

    def test_circuit_normals(self):
        led_yellow_nc = westinghouse.Output(13, normally_closed=True)
        led_yellow_nc.on()
        self.assertEqual(led_yellow_nc.is_on, True)

        led_white_no = westinghouse.Output(27, normally_closed=False)
        led_white_no.on()
        self.assertEqual(led_white_no.is_on, True)

        sleep(1)
        led_yellow_nc.off()
        led_white_no.off()
        self.assertNotEqual(led_yellow_nc.value, led_white_no.value)

    def test_mpd_is_alive(self):
        response = westinghouse.mpd_is_alive()
        self.assertEqual(response, True)
        print("mpd is alive")

        run(["sudo", "killall", "mpd"])
        sleep(0.1)
        response = westinghouse.mpd_is_alive()
        self.assertEqual(response, False)

        i = 0
        while response is False:
            i += 1
            print("waiting for mpd to restart", i)
            response = westinghouse.mpd_is_alive()
            sleep(1)

        self.assertEqual(response, True)

    def test_mpd_get_status(self):
        status = westinghouse.mpd_get_status()
        self.assertEqual(isinstance(status, dict), True)
        print(status)

    def test_mpd_startup(self):
        westinghouse.mpd_startup()
        print(westinghouse.mpd_get_status())

    def test_mpd_toggle_pause(self):
        state1 = westinghouse.mpd_get_status()["state"]
        westinghouse.mpd_toggle_pause()
        state2 = westinghouse.mpd_get_status()["state"]
        self.assertNotEqual(state1, state2)
        sleep(1)
        westinghouse.mpd_toggle_pause()


if __name__ == "__main__":
    unittest.main()
