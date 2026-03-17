import datetime
import time
import random
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

# Controllers
mouse = MouseController()
keyboard = KeyboardController()

def bezier_curve(p0, p1, p2, t):
    """Quadratic Bezier interpolation"""
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

# Parameters
STEP_DISTANCE = 240 #50          # max horizontal movement each direction
ARC_HEIGHT = 25 #5             # vertical arc height for natural curve
STEPS_PER_CURVE = 30        # steps along each curve
INTERVAL_BETWEEN_CURVES = 3 # 0.05
JITTER_STD = 0.8 #0.3            # damped Gaussian standard deviation
DAMPING = 0.8               # damping factor for jitter

SHIFT_INTERVAL = 2     # press Shift every 10 sec minutes

last_shift = time.time()

# Damped Gaussian jitter
jitter = 0

# Direction: 1 = right, -1 = left
direction = 1

try:
    while True:
        start_x, start_y = mouse.position
        end_x = start_x + STEP_DISTANCE * direction
        end_y = start_y

        # Control point for smooth arc
        control_x = (start_x + end_x) / 2
        control_y = start_y - ARC_HEIGHT + random.gauss(0, JITTER_STD)

        for i in range(STEPS_PER_CURVE):
            t = i / (STEPS_PER_CURVE - 1)
            x = bezier_curve(start_x, control_x, end_x, t)
            y = bezier_curve(start_y, control_y, end_y, t)

            # Damped Gaussian jitter
            jitter = DAMPING * jitter + random.gauss(0, JITTER_STD)
            jitter = max(min(jitter, 5), -5)  # optional clamp
            y += jitter

            # pyautogui.moveTo(int(x), int(y), duration=0)
            mouse.position = (x, y)

            if time.time() - last_shift > SHIFT_INTERVAL:
                keyboard.press(Key.shift)
                keyboard.release(Key.shift)
                last_shift = time.time()
                print("pressed shift", datetime.datetime.now())

            # Accelerate: slower at start, faster at end
            time.sleep(max(0.01, 0.05 * (1 - t)))

        # Small pause between curves
        time.sleep(INTERVAL_BETWEEN_CURVES)

        # Reverse direction
        direction *= -1

except KeyboardInterrupt:
    print("Stopped.")