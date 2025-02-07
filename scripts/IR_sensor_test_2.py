#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Use Broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins where your IR sensors are connected.
# These example pins [13, 12, 20, 21, 26] should be replaced with the actual ones from your setup.
IR_SENSOR_PINS = [13, 12, 20, 21, 26]

# Set up each IR sensor pin as an input
for pin in IR_SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN)

try:
    while True:
        # Read and collect the state of each sensor
        sensor_values = [GPIO.input(pin) for pin in IR_SENSOR_PINS]
        # Print the raw sensor data. Depending on your sensor, a value of 0 or 1 may indicate detection.
        print("IR Sensor values:", sensor_values)
        # Pause briefly before reading again
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()
