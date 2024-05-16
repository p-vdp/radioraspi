import unittest
from time import sleep

import westinghouse


class InteractiveTestCases(unittest.TestCase):
    def test_play_pause(self):
        button = westinghouse.Input(4)
        print("Press: play/pause GPIO 4")
        button.wait()
        self.assertEqual(True, True)

    def test_shuffle(self):
        button = westinghouse.Input(17)
        print("Press: shuffle GPIO 17")
        button.wait()
        self.assertEqual(True, True)

    def test_volume(self):
        print("Testing volume")
        clk = westinghouse.Input(23)
        dt = westinghouse.Input(24)
        last_state = dt.value
        x = 0
        for i in range(1000):
            clk_state = clk.value
            dt_state = dt.value
            if clk_state != last_state:
                if dt_state != clk_state:
                    x += 1
                    print("volume up", x)
                else:
                    x -= 1
                    print("volume down", x)
            last_state = clk.value
            sleep(0.01)
        self.assertEqual(True, True)

    def test_seek(self):
        print("test seek")
        clk = westinghouse.Input(5)
        dt = westinghouse.Input(6)
        x = 0
        last_state = dt.value
        while x < 10:
            clk_state = clk.value
            dt_state = dt.value

            if clk_state != last_state:
                if dt_state != clk_state:
                    x -= 1
                    print("back", x)
                else:
                    x += 1
                    print("forward", x)
                sleep(0.05)
            last_state = clk.value

        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
