#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Configuration: Change these values as needed
SERVO_PIN = 18       # GPIO pin connected to the servo's signal line
FREQUENCY = 50       # Typical servo frequency (50Hz)
FORWARD_ANGLE = 90   # Angle for "forward" position (center)
UPWARD_ANGLE = 45    # Angle for "upward" position (adjust as needed)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM on the servo pin
pwm = GPIO.PWM(SERVO_PIN, FREQUENCY)
pwm.start(0)
time.sleep(1)  # Give some time for PWM to settle

def set_servo_angle(angle):
    """
    Moves the servo to the specified angle.
    The conversion from angle to duty cycle is based on the assumption that:
       0° corresponds to ~2.5% duty cycle and 180° to ~12.5%.
    Adjust the formula if your servo behaves differently.
    """
    duty_cycle = (angle / 18.0) + 2.5
    print(f"Setting servo to {angle}° (Duty Cycle: {duty_cycle}%)")
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Wait for the servo to reach the position
    # Stopping the PWM signal can reduce servo jitter.
    pwm.ChangeDutyCycle(0)
    time.sleep(0.5)

try:
    # Set the camera to the forward position
    print("Moving camera to forward position...")
    set_servo_angle(FORWARD_ANGLE)
    time.sleep(2)

    # Now move the camera upward
    print("Moving camera upward...")
    set_servo_angle(UPWARD_ANGLE)
    time.sleep(2)

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # Clean up the GPIO and stop PWM
    print("Cleaning up GPIO...")
    pwm.stop()
    GPIO.cleanup()
    print("Done.")
