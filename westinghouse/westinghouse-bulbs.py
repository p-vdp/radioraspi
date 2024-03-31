from utils import Gpio

# LED control
led_closed = Gpio(12, "op")
led_open = Gpio(17, "op")
