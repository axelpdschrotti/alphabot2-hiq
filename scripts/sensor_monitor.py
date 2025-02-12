import RPi.GPIO as GPIO
import time

# IR sensor pins (BCM numbering)
IR_LEFT = 16     # Left IR sensor (swapped)
IR_RIGHT = 19    # Right IR sensor (swapped)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize sensor pins
GPIO.setup(IR_LEFT, GPIO.IN)
GPIO.setup(IR_RIGHT, GPIO.IN)

try:
    while True:
        # Read IR sensors
        left_detected = GPIO.input(IR_LEFT) == GPIO.LOW
        right_detected = GPIO.input(IR_RIGHT) == GPIO.LOW

        # Check for obstacles
        if left_detected or right_detected:
            left_status = "Obstacle" if left_detected else "No Obstacle"
            right_status = "Obstacle" if right_detected else "No Obstacle"
            print(f"Left: {left_status}, Right: {right_status}")

        time.sleep(0.2)  # Short delay between readings

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nProgram stopped")
