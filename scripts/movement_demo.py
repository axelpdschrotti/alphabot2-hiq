import RPi.GPIO as GPIO
import time
import threading

# Motor and Sensor Pin Configuration
IN1 = 13
IN2 = 12
ENA = 6
IN3 = 21
IN4 = 20
ENB = 26
IR_LEFT = 16
IR_RIGHT = 19

# Turn timing configuration (calibrate these values)
TURN_90_TIME = 0.8    # Time needed for 90° turn at current speed
TURN_180_TIME = 1.6   # Time needed for 180° turn (typically 2×90° time)

# GPIO Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor Pins Setup
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Sensor Pins Setup
GPIO.setup(IR_LEFT, GPIO.IN)
GPIO.setup(IR_RIGHT, GPIO.IN)

# PWM Setup for Motors
pwmA = GPIO.PWM(ENA, 50)
pwmB = GPIO.PWM(ENB, 50)
speed = 30
pwmA.start(speed)
pwmB.start(speed)

# Movement Functions
def move_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def move_backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# New timed turn functions
def turn_left_90():
    print("Turning 90° left")
    turn_left()
    time.sleep(TURN_90_TIME)
    stop()

def turn_right_90():
    print("Turning 90° right")
    turn_right()
    time.sleep(TURN_90_TIME)
    stop()

def turn_180():
    print("Turning 180°")
    turn_left()  # Can be changed to turn_right() for right rotation
    time.sleep(TURN_180_TIME)
    stop()

def increase_speed():
    global speed
    if speed < 100:
        speed += 10
        pwmA.ChangeDutyCycle(speed)
        pwmB.ChangeDutyCycle(speed)
        print(f"Speed increased to {speed}%")

def decrease_speed():
    global speed
    if speed > 10:
        speed -= 10
        pwmA.ChangeDutyCycle(speed)
        pwmB.ChangeDutyCycle(speed)
        print(f"Speed decreased to {speed}%")

# Sensor Monitoring Thread
def check_sensors():
    while True:
        left_detected = GPIO.input(IR_LEFT) == GPIO.LOW
        right_detected = GPIO.input(IR_RIGHT) == GPIO.LOW
        if left_detected or right_detected:
            left_status = "Obstacle" if left_detected else "No Obstacle"
            right_status = "Obstacle" if right_detected else "No Obstacle"
            print(f"Left: {left_status}, Right: {right_status} - Emergency Stop!")
            stop()
        time.sleep(0.1)

# Start Sensor Thread
sensor_thread = threading.Thread(target=check_sensors, daemon=True)
sensor_thread.start()

# Main Control Loop
try:
    print("Control the robot with keys:")
    print("w: forward, s: backward, a: left (continuous), d: right (continuous)")
    print("l: 90° left, r: 90° right, u: 180° turn")
    print("q: stop, +/-: speed, e: exit")
    
    while True:
        cmd = input("Enter command: ").strip().lower()
        if cmd == 'w':
            print("Moving forward")
            move_forward()
        elif cmd == 's':
            print("Moving backward")
            move_backward()
        elif cmd == 'a':
            print("Turning left (continuous)")
            turn_left()
        elif cmd == 'd':
            print("Turning right (continuous)")
            turn_right()
        elif cmd == 'l':
            turn_left_90()
        elif cmd == 'r':
            turn_right_90()
        elif cmd == 'u':
            turn_180()
        elif cmd == 'q':
            print("Stopping")
            stop()
        elif cmd == '+':
            increase_speed()
        elif cmd == '-':
            decrease_speed()
        elif cmd == 'e':
            print("Exiting...")
            break
        else:
            print("Unknown command")
        time.sleep(0.1)

finally:
    stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")