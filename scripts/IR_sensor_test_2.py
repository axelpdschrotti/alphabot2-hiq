#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# Define TLC1543 (IR sensor array) pins
CS_PIN       = 5    # Chip Select
CLOCK_PIN    = 25   # Clock
ADDRESS_PIN  = 24   # Address (sent serially)
DATAOUT_PIN  = 23   # Data output from ADC

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up pins: CS, CLOCK, ADDRESS as outputs; DATAOUT as input.
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(ADDRESS_PIN, GPIO.OUT)
GPIO.setup(DATAOUT_PIN, GPIO.IN)

# Initialize outputs to default states
GPIO.output(CS_PIN, GPIO.HIGH)
GPIO.output(CLOCK_PIN, GPIO.LOW)
GPIO.output(ADDRESS_PIN, GPIO.LOW)

def read_ir_sensors():
    """
    Reads all 5 IR sensor values from the TLC1543 ADC.
    Correctly sends the 4-bit address for each sensor during read.
    Returns a list of 5 integer values.
    """
    sensor_values = []
    channels = [0, 1, 2, 3, 4]  # Assuming sensors are on channels 0-4
    
    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)
    
    for channel in channels:
        value = 0
        # Prepare the 4-bit address (MSB first)
        address = channel  # Channels 0-4 (addresses 0b0000 to 0b0100)
        
        for i in range(10):
            GPIO.output(CLOCK_PIN, GPIO.LOW)
            
            # Send address bits during the first 4 cycles
            if i < 4:
                bit = (address >> (3 - i)) & 1  # MSB first
                GPIO.output(ADDRESS_PIN, bit)
            
            time.sleep(0.00001)  # Short delay
            
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            time.sleep(0.00001)
            
            # Read data bit after clock rises
            data_bit = GPIO.input(DATAOUT_PIN)
            value = (value << 1) | data_bit  # Build the 10-bit value
        
        sensor_values.append(value)
    
    GPIO.output(CS_PIN, GPIO.HIGH)
    return sensor_values

print("Starting IR sensor reading mode for all 5 sensors.")
print("Press Ctrl+C to exit.")

try:
    while True:
        values = read_ir_sensors()
        for idx, val in enumerate(values):
            print(f"Sensor {idx+1}: {val:3d} (binary: {val:010b})", end=" | ")
        print()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting IR sensor reading mode.")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")