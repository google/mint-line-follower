# A more advanced example that combines all the sensors shown so far,
# shows how to "collect them" all into a single convenient "robot" object,
# how to define "behaviors" for the robot, and switch among them using a button.

import adafruit_hcsr04
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_motor import servo
import board
from digitalio import DigitalInOut, Direction, Pull
import keypad
import neopixel
import pwmio
import time

# -------------------------------------------------------------------
# Define the robot as a class, encapsulating all its onboard hardware
class Robot:
    def __init__(self):
        self.line_left = DigitalInOut(board.D10)
        self.line_right = DigitalInOut(board.D8)
        self.servo_left = servo.ContinuousServo(pwmio.PWMOut(board.D0, frequency=50))
        self.servo_right = servo.ContinuousServo(pwmio.PWMOut(board.D6, frequency=50))
        self.sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D4, echo_pin=board.D3)
        self.rgb_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
        self.rainbow = Rainbow(self.rgb_pixel, speed=0.1, period=2)
        self.button = keypad.Keys((board.D1,), value_when_pressed=False, pull=True)
        self.led = DigitalInOut(board.LED_GREEN)
        self.led.direction = Direction.OUTPUT

    # Set given speeds left & right wheels
    def drive(self, left, right):
        self.servo_left.throttle = 0.1*left
        self.servo_right.throttle = -0.15*right

    # Return the current sonar distance
    def read_sonar_distance(self):
        try:
            return self.sonar.distance
        except RuntimeError:
            # Do not crash on errors from sonar, return None
            return None

    # Stop all activity (before switching on a new behavior)
    def reset(self):
        self.drive(0, 0)
        self.rgb_pixel[0] = (0, 0, 0)
        self.rgb_pixel.write()

# -------------------------------------------------------------------
# Define three different behaviours that our robot will support
# Each behavior is a function that will be invoked in the main loop
# (but only when that particular behavior is enabled). We will pass a
# "robot" object to the behavior function.

def rainbow(robot):
    # Show a rainbow animation on the neopixel.
    robot.rainbow.animate()

def obstacle_avoidance(robot):
    # Drive straight except when there's an obstacle
    d = robot.read_sonar_distance()
    if d is not None and d < 10:
        robot.drive(-1, 1)     # Turn left
        time.sleep(0.3)
    else:
        robot.drive(1, 1) # Drive straight

def line_following(robot):
    # The naive line-follower
    robot.drive(robot.line_left.value, robot.line_right.value)

# Collect all behaviors in an array
BEHAVIORS = [rainbow, obstacle_avoidance, line_following]
# This variable will hold the index of the current behavior
current_behavior_id = 0

# -------------------------------------------------------------------
# Initialize the robot
robot = Robot()

# Main loop
while True:
    # When the button is clicked, change behavior to the next one
    event = robot.button.events.get()
    if event and event.released:
        current_behavior_id = (current_behavior_id + 1) % len(BEHAVIORS)
        robot.reset()

    # Call the current behavior method
    BEHAVIORS[current_behavior_id](robot)
