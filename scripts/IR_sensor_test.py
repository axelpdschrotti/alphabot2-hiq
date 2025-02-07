#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# Define IR sensor pins
IR_LEFT = 16
IR_RIGHT = 19

# GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up IR sensor pins as input
GPIO.setup(IR_LEFT, GPIO.IN)
GPIO.setup(IR_RIGHT, GPIO.IN)

print("Starting IR sensor reading mode. Press Ctrl+C to exit.")

try:
    while True:
        # Read the sensor values
        left_value = GPIO.input(IR_LEFT)
        right_value = GPIO.input(IR_RIGHT)
        
        # Interpret sensor output: assuming LOW means line detected.
        left_status = "Detected" if left_value == GPIO.LOW else "Not Detected"
        right_status = "Detected" if right_value == GPIO.LOW else "Not Detected"
        
        # Print the sensor statuses
        print(f"Left IR: {left_status}, Right IR: {right_status}")
        
        time.sleep(0.1)  # adjust delay as needed for responsiveness
        
except KeyboardInterrupt:
    print("\nExiting IR sensor reading mode...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
