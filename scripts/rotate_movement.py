import RPi.GPIO as GPIO
import time

# Define motor control pins
IN1 = 13
IN2 = 12
ENA = 6
IN3 = 21
IN4 = 20
ENB = 26

# Initialize global PWM variables
pwmA = None
pwmB = None
default_speed = 50  # Default speed (50% PWM)
rotation_speed = 20  # Rotation speed (20% PWM)

# Function to initialize GPIO settings
def setup():
    global pwmA, pwmB
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)

    # Set up PWM control
    pwmA = GPIO.PWM(ENA, 50)  # 50Hz PWM frequency
    pwmB = GPIO.PWM(ENB, 50)
    pwmA.start(default_speed)
    pwmB.start(default_speed)

# Function to move forward
def move_forward(duration=1):
    print("Moving Forward")
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    time.sleep(duration)
    stop_bot()

# Function to move backward
def move_backward(duration=1):
    print("Moving Backward")
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    time.sleep(duration)
    stop_bot()

# Function to rotate 90 degrees left
def rotate_left_90():
    print("Rotating Left 90 Degrees")
    set_speed(rotation_speed)  # Reduce speed before rotation

    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)  # Left motor moves backward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)   # Right motor moves forward

    time.sleep(0.6)  # Adjust for accurate 90-degree rotation
    stop_bot()

    reset_speed()  # Reset speed after rotation
    print("Rotation Left Complete")

# Function to rotate 90 degrees right
def rotate_right_90():
    print("Rotating Right 90 Degrees")
    set_speed(rotation_speed)  # Reduce speed before rotation

    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)   # Left motor moves forward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)  # Right motor moves backward

    time.sleep(0.6)  # Adjust for accurate 90-degree rotation
    stop_bot()

    reset_speed()  # Reset speed after rotation
    print("Rotation Right Complete")

# Function to stop the robot
def stop_bot():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# Function to set a temporary speed (for rotations)
def set_speed(speed):
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    print(f"Speed set to {speed}%")

# Function to reset speed back to default
def reset_speed():
    pwmA.ChangeDutyCycle(default_speed)
    pwmB.ChangeDutyCycle(default_speed)
    print(f"Speed reset to {default_speed}%")

# Function to clean up GPIO
def cleanup():
    stop_bot()
    GPIO.cleanup()

# Main execution loop
if __name__ == "__main__":
    setup()
    try:
        while True:
            command = input("Enter command (w=forward, s=backward, a=left, d=right, q=exit): ").strip().lower()

            if command == "w":
                move_forward()
            elif command == "s":
                move_backward()
            elif command == "a":
                rotate_left_90()
            elif command == "d":
                rotate_right_90()
            elif command == "q":
                print("Exiting program...")
                break
            else:
                print("Invalid command! Use w, s, a, d, or q.")

    finally:
        cleanup()


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

        time.sleep(0.1)  # Short delay between readings