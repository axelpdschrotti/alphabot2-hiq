#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# GPIO Pins (Verify these match your Alphabot2!)
CS_PIN = 5
CLOCK_PIN = 25
ADDRESS_PIN = 24
DATAOUT_PIN = 23

# Sensor-Channel Mapping (CRITICAL - Adjust if necessary)
PHYSICAL_SENSORS_TO_ADC_CHANNELS = {
    1: 1,  # Physical Sensor 1 -> ADC Channel 0
    2: 1,  # Physical Sensor 2 -> ADC Channel 1
    3: 1,  # Physical Sensor 3 -> ADC Channel 2
    4: 1,  # Physical Sensor 4 -> ADC Channel 3
    5: 1   # Physical Sensor 5 -> ADC Channel 4
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(ADDRESS_PIN, GPIO.OUT)
GPIO.setup(DATAOUT_PIN, GPIO.IN)

GPIO.output(CS_PIN, GPIO.HIGH)
GPIO.output(CLOCK_PIN, GPIO.LOW)
GPIO.output(ADDRESS_PIN, GPIO.LOW)

def read_ir_sensors():
    values = [0] * 5  # Index 0=Sensor1, 1=Sensor2, etc.
    channels = list(PHYSICAL_SENSORS_TO_ADC_CHANNELS.values())
    
    GPIO.output(CS_PIN, GPIO.LOW)
    time.sleep(0.001)
    
    # Prime the ADC with a dummy read
    dummy_channel = channels[0]
    for _ in range(10):
        GPIO.output(CLOCK_PIN, GPIO.LOW)
        if _ < 4:
            bit = (dummy_channel >> (3 - _)) & 1
            GPIO.output(ADDRESS_PIN, bit)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        time.sleep(0.00001)
    
    # Now read actual values
    prev_channel = dummy_channel
    for current_channel in channels:
        value = 0
        for i in range(10):
            GPIO.output(CLOCK_PIN, GPIO.LOW)
            
            # Send address for NEXT channel
            if i < 4:
                bit = (current_channel >> (3 - i)) & 1
                GPIO.output(ADDRESS_PIN, bit)
            
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            data_bit = GPIO.input(DATAOUT_PIN)
            value = (value << 1) | data_bit
            time.sleep(0.00001)
        
        # Map to physical sensor based on previous channel
        sensor_index = list(PHYSICAL_SENSORS_TO_ADC_CHANNELS.keys())[
            list(PHYSICAL_SENSORS_TO_ADC_CHANNELS.values()).index(prev_channel)
        ]
        values[sensor_index-1] = value  # -1 converts to 0-based list
        prev_channel = current_channel
    
    GPIO.output(CS_PIN, GPIO.HIGH)
    return values

print("Starting calibrated sensor readings...")
try:
    while True:
        values = read_ir_sensors()
        for idx, val in enumerate(values):
            print(f"Sensor {idx+1}: {val:4d}", end=" | ")
        print()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    GPIO.cleanup()