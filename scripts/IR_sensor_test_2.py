#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# Define TLC1543 pins
CS_PIN = 5
CLOCK_PIN = 25
ADDRESS_PIN = 24
DATAOUT_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(ADDRESS_PIN, GPIO.OUT)
GPIO.setup(DATAOUT_PIN, GPIO.IN)

# Initialize pins
GPIO.output(CS_PIN, GPIO.HIGH)
GPIO.output(CLOCK_PIN, GPIO.LOW)
GPIO.output(ADDRESS_PIN, GPIO.LOW)

def read_ir_sensors():
    sensor_values = [0] * 5  # Initialize list for 5 sensors
    channels = [0, 1, 2, 3, 4]  # ADC channels for sensors 1-5

    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)

    previous_channel = channels[-1]  # Start with last channel for first read

    for idx in range(5):
        current_channel = channels[idx]
        value = 0

        # Send address for NEXT channel (current_channel)
        # while reading previous_channel's data
        DELAY = 0.00005  # 50 microseconds; adjust as needed

        for i in range(10):
            GPIO.output(CLOCK_PIN, GPIO.LOW)
            if i < 4:
                bit = (current_channel >> (3 - i)) & 1
                GPIO.output(ADDRESS_PIN, bit)
            time.sleep(DELAY)
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            data_bit = GPIO.input(DATAOUT_PIN)
            value = (value << 1) | data_bit
            time.sleep(DELAY)


        # Store value for previous_channel
        sensor_values[previous_channel] = value
        previous_channel = current_channel

    GPIO.output(CS_PIN, GPIO.HIGH)
    return sensor_values

print("Starting corrected IR sensor readings...")
try:
    while True:
        values = read_ir_sensors()
        ordered_values = [ values[4], values[0], values[1], values[2], values[3] ]
        for idx, val in enumerate(ordered_values):
            print(f"Sensor {idx+1}: {val:4d}", end=" | ")
        print()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    GPIO.cleanup()