#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from Adafruit_PCA9685 import PCA9685

# ----- Servo Setup -----
# Initialize the PCA9685 using its default address (0x40)
pwm = PCA9685()
pwm.set_pwm_freq(50)  # 50 Hz is standard for servos

def set_servo_angle(channel, angle, pulse_min=150, pulse_max=600):
    """
    Convert an angle (0 to 180) into a PWM pulse and send it to the given channel.
    Adjust pulse_min and pulse_max to calibrate your servo.
    """
    pulse = int(pulse_min + (pulse_max - pulse_min) * angle / 180)
    pwm.set_pwm(channel, 0, pulse)

# Initial servo positions:
pan_angle = 90    # Center (facing forward)
tilt_angle = 45   # Tilt upward (adjust as needed)

# Update servos to initial positions:
set_servo_angle(0, pan_angle)   # Pan servo on channel 0
set_servo_angle(1, tilt_angle)  # Tilt servo on channel 1

# ----- Joystick (Button) Setup -----
# Define GPIO pins for joystick directions
PIN_UP    = 8   # Up direction (increase tilt)
PIN_RIGHT = 9   # Right direction (increase pan)
PIN_DOWN  = 10  # Down direction (decrease tilt)
PIN_LEFT  = 11  # Left direction (decrease pan)

# Set up GPIO
GPIO.setmode(GPIO.BCM)
# Set joystick pins as inputs with pull-up resistors
for pin in [PIN_UP, PIN_RIGHT, PIN_DOWN, PIN_LEFT]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define how much to change angles per button press
ANGLE_STEP = 5
# Define servo limits
PAN_MIN, PAN_MAX = 0, 180
TILT_MIN, TILT_MAX = 0, 180

def update_servos():
    """Update the servo positions using the global pan_angle and tilt_angle."""
    set_servo_angle(0, pan_angle)
    set_servo_angle(1, tilt_angle)
    print("Pan: {}°, Tilt: {}°".format(pan_angle, tilt_angle))

print("Joystick control running. Press CTRL+C to exit.")

try:
    while True:
        # Check each direction.
        # Note: Buttons are assumed active LOW (pressed => GPIO.LOW)
        if GPIO.input(PIN_UP) == GPIO.LOW:
            # Joystick up: Increase tilt (raise camera)
            tilt_angle = min(tilt_angle + ANGLE_STEP, TILT_MAX)
            update_servos()
            time.sleep(0.3)  # Debounce delay

        if GPIO.input(PIN_DOWN) == GPIO.LOW:
            # Joystick down: Decrease tilt (lower camera)
            tilt_angle = max(tilt_angle - ANGLE_STEP, TILT_MIN)
            update_servos()
            time.sleep(0.3)

        if GPIO.input(PIN_RIGHT) == GPIO.LOW:
            # Joystick right: Increase pan (turn camera right)
            pan_angle = min(pan_angle + ANGLE_STEP, PAN_MAX)
            update_servos()
            time.sleep(0.3)

        if GPIO.input(PIN_LEFT) == GPIO.LOW:
            # Joystick left: Decrease pan (turn camera left)
            pan_angle = max(pan_angle - ANGLE_STEP, PAN_MIN)
            update_servos()
            time.sleep(0.3)

        # Small delay to prevent busy waiting
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
