#!/usr/bin/env python
import time
from Adafruit_PCA9685 import PCA9685

# Initialize the PCA9685 using its default address (0x40)
pwm = PCA9685()

# Set the PWM frequency to 50hz, common for servos
pwm.set_pwm_freq(50)

def set_servo_angle(channel, angle, pulse_min=150, pulse_max=600):
    """
    Set a servo on the given channel to a specific angle (0-180 degrees).
    pulse_min and pulse_max are the calibration values corresponding to 0° and 180°.
    Adjust these values if your servo does not respond correctly.
    """
    # Calculate pulse length
    pulse = int(pulse_min + (pulse_max - pulse_min) * angle / 180)
    pwm.set_pwm(channel, 0, pulse)

if __name__ == '__main__':
    # Set pan servo (channel 0) to 90 degrees for straight ahead.
    set_servo_angle(0, 90)
    
    # Set tilt servo (channel 1) to 45 degrees for an upward tilt.
    set_servo_angle(1, 45)
    
    # Allow time for the servos to move to the desired position.
    time.sleep(1)
