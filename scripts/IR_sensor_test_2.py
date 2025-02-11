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

def read_channel(channel):
    value = 0
    for i in range(10):
        GPIO.output(CLOCK_PIN, GPIO.LOW)
        if i < 4:
            bit = (channel >> (3 - i)) & 1
            GPIO.output(ADDRESS_PIN, bit)
        time.sleep(DELAY)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        data_bit = GPIO.input(DATAOUT_PIN)
        value = (value << 1) | data_bit
        time.sleep(DELAY)
    # Send extra clocks for settling:
    for i in range(6):
        GPIO.output(CLOCK_PIN, GPIO.LOW)
        time.sleep(DELAY)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        time.sleep(DELAY)
    return value

def read_ir_sensors():
    sensor_values = [0] * 5
    channels = [0, 1, 2, 3, 4]
    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)
    
    # Flush conversion: do a dummy read for one channel
    dummy = read_channel(channels[0])
    
    # Now for each channel, do two conversions:
    for idx in range(5):
        current_channel = channels[idx]
        _ = read_channel(current_channel)  # dummy conversion – discard
        sensor_values[idx] = read_channel(current_channel)  # take real reading
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