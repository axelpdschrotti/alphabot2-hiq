#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# Define pins for the TLC1543-based IR sensor array
CS_PIN       = 5    # Chip Select
CLOCK_PIN    = 25   # Clock
ADDRESS_PIN  = 24   # (Not actively changed in this script; may be used for channel selection in some setups)
DATAOUT_PIN  = 23   # ADC data output

# Increase clock delay to give the ADC time to settle between bits.
CLOCK_DELAY = 0.00005  # 50 microseconds; you can try increasing to 100e-6 if needed

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(ADDRESS_PIN, GPIO.OUT)
GPIO.setup(DATAOUT_PIN, GPIO.IN)

# Initialize output pins
GPIO.output(CS_PIN, GPIO.HIGH)
GPIO.output(CLOCK_PIN, GPIO.LOW)
GPIO.output(ADDRESS_PIN, GPIO.LOW)  # Depending on your wiring, this might need to be toggled

def read_adc_channel():
    """
    Reads 10 bits from the ADC for the current sensor channel.
    Returns a tuple (value, bit_string) where:
      - value is the decimal value (0-1023)
      - bit_string is the 10-bit string representation.
    """
    value = 0
    bit_string = ""
    for i in range(10):
        # Pulse the clock: lower then raise it
        GPIO.output(CLOCK_PIN, GPIO.LOW)
        time.sleep(CLOCK_DELAY)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        time.sleep(CLOCK_DELAY)
        bit = GPIO.input(DATAOUT_PIN)
        bit_string += str(bit)
        value = (value << 1) | bit
    return value, bit_string

def read_all_ir():
    """
    Reads all five sensor channels sequentially.
    Assumes that the ADC outputs 10 bits per sensor consecutively.
    Returns a list of 5 tuples: (value, bit_string)
    """
    results = []
    # Start the conversion cycle
    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)  # Allow conversion to begin
    for ch in range(5):
        val, bits = read_adc_channel()
        results.append((val, bits))
    GPIO.output(CS_PIN, GPIO.HIGH)  # End the conversion cycle
    return results

print("Starting IR sensor debug mode (5 channels).")
print("Using CLOCK_DELAY =", CLOCK_DELAY, "seconds")
print("Move your hand in front of the sensors to see changes.")
print("Press Ctrl+C to exit.\n")

try:
    while True:
        sensor_readings = read_all_ir()
        for idx, (value, bits) in enumerate(sensor_readings):
            print(f"Sensor {idx+1}: Value = {value:3d}  Bits = {bits}")
        print("-" * 50)
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nExiting IR sensor debug mode...")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
