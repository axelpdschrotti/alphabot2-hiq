#!/usr/bin/env python
import time
import RPi.GPIO as GPIO

# ----- Servo Output Setup -----
# Choose GPIO pins for servo outputs:
PAN_SERVO_PIN = 12   # Pan servo (horizontal)
TILT_SERVO_PIN = 13  # Tilt servo (vertical)

# Set the PWM frequency (50Hz is standard for servos)
PWM_FREQ = 50

# Initialize GPIO mode
GPIO.setmode(GPIO.BCM)

# Setup servo pins as output
GPIO.setup(PAN_SERVO_PIN, GPIO.OUT)
GPIO.setup(TILT_SERVO_PIN, GPIO.OUT)

# Create PWM instances on the servo pins
pan_pwm = GPIO.PWM(PAN_SERVO_PIN, PWM_FREQ)
tilt_pwm = GPIO.PWM(TILT_SERVO_PIN, PWM_FREQ)

# Start PWM with an initial duty cycle corresponding to the desired angle.
# We'll initialize pan at 90° (forward) and tilt at 45° (upwards).
def angle_to_duty(angle):
    """Convert an angle (0-180) to a duty cycle percentage."""
    return (angle / 18.0) + 2.5

pan_angle = 90   # initial horizontal angle (forward)
tilt_angle = 45  # initial vertical angle (upward)

pan_pwm.start(angle_to_duty(pan_angle))
tilt_pwm.start(angle_to_duty(tilt_angle))

# ----- Joystick Input Setup -----
# Define GPIO pins for joystick directions.
# Assumed wiring: normally open switches with internal pull-ups enabled.
PIN_UP    = 8    # "Up" button increases tilt (camera tilts upward)
PIN_RIGHT = 9    # "Right" button increases pan (camera turns right)
PIN_DOWN  = 10   # "Down" button decreases tilt (camera tilts downward)
PIN_LEFT  = 11   # "Left" button decreases pan (camera turns left)

# Set joystick pins as inputs with pull-up resistors
for pin in [PIN_UP, PIN_RIGHT, PIN_DOWN, PIN_LEFT]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define parameters for angle adjustment
ANGLE_STEP = 5  # degrees to change per press
PAN_MIN, PAN_MAX = 0, 180
TILT_MIN, TILT_MAX = 0, 180

def update_servos():
    """Update the PWM duty cycles for both servos based on current angles."""
    pan_duty = angle_to_duty(pan_angle)
    tilt_duty = angle_to_duty(tilt_angle)
    pan_pwm.ChangeDutyCycle(pan_duty)
    tilt_pwm.ChangeDutyCycle(tilt_duty)
    print("Pan: {}°, Tilt: {}°".format(pan_angle, tilt_angle))

print("Joystick control (GPIO only) running. Press CTRL+C to exit.")

try:
    while True:
        # Check each joystick direction.
        # Buttons are active LOW.
        if GPIO.input(PIN_UP) == GPIO.LOW:
            tilt_angle = min(tilt_angle + ANGLE_STEP, TILT_MAX)
            update_servos()
            time.sleep(0.3)  # Debounce delay

        if GPIO.input(PIN_DOWN) == GPIO.LOW:
            tilt_angle = max(tilt_angle - ANGLE_STEP, TILT_MIN)
            update_servos()
            time.sleep(0.3)

        if GPIO.input(PIN_RIGHT) == GPIO.LOW:
            pan_angle = min(pan_angle + ANGLE_STEP, PAN_MAX)
            update_servos()
            time.sleep(0.3)

        if GPIO.input(PIN_LEFT) == GPIO.LOW:
            pan_angle = max(pan_angle - ANGLE_STEP, PAN_MIN)
            update_servos()
            time.sleep(0.3)
        
        # Short sleep to reduce CPU load
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    pan_pwm.stop()
    tilt_pwm.stop()
    GPIO.cleanup()
