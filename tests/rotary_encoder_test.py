from time import sleep

import gpiozero


rotor = gpiozero.RotaryEncoder(
    23, 24, bounce_time=0.01, max_steps=100, threshold_steps=(0, 100), wrap=False
)

rotor.steps = 10
min = rotor.threshold_steps[0]
max = rotor.threshold_steps[1]

while True:
    if rotor.steps <= min:
        rotor.steps = min

    if rotor.steps >= max:
        rotor.steps = max

    print(
        "\r",
        rotor.max_steps,
        rotor.steps,
        rotor.threshold_steps,
        rotor.wrap,
        rotor.value,
        rotor.is_active,
        end="",
    )
    sleep(0.05)
