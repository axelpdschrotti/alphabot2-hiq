#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# Define TLC1543 (IR sensor array) pins
CS_PIN       = 5    # Chip Select
CLOCK_PIN    = 25   # Clock
ADDRESS_PIN  = 24   # Address (often used for channel selection; not actively changed here)
DATAOUT_PIN  = 23   # Data output from ADC

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up pins: CS, CLOCK, and ADDRESS as outputs; DATAOUT as input.
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(ADDRESS_PIN, GPIO.OUT)
GPIO.setup(DATAOUT_PIN, GPIO.IN)

# Initialize outputs to default states
GPIO.output(CS_PIN, GPIO.HIGH)
GPIO.output(CLOCK_PIN, GPIO.LOW)
GPIO.output(ADDRESS_PIN, GPIO.LOW)  # You may need to set this if channel selection is desired

def read_ir_sensors():
    sensor_values = []
    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)
    for ch in range(5):
        # Toggle ADDRESS_PIN based on channel number (this is an example)
        if ch % 2 == 0:
            GPIO.output(ADDRESS_PIN, GPIO.LOW)
        else:
            GPIO.output(ADDRESS_PIN, GPIO.HIGH)
        value = 0
        for i in range(10):
            GPIO.output(CLOCK_PIN, GPIO.LOW)
            time.sleep(0.00001)
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            time.sleep(0.00001)
            bit = GPIO.input(DATAOUT_PIN)
            value = (value << 1) | bit
        sensor_values.append(value)
    GPIO.output(CS_PIN, GPIO.HIGH)
    return sensor_values


print("Starting IR sensor reading mode for all 5 sensors.")
print("Press Ctrl+C to exit.")

try:
    while True:
        # Read the 5 sensor values
        values = read_ir_sensors()
        # Print each sensor's raw value in decimal and as a 10-bit binary string.
        for idx, val in enumerate(values):
            print(f"Sensor {idx+1}: {val:3d} (binary: {val:010b})", end=" | ")
        print()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting IR sensor reading mode.")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
