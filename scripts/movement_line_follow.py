#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import threading
import sys, select, tty, termios

# -------------------------------
# Motor and Sensor Pin Configuration
# -------------------------------
IN1 = 13
IN2 = 12
ENA = 6
IN3 = 21
IN4 = 20
ENB = 26
IR_LEFT = 16
IR_RIGHT = 19

# Turn timing configuration (calibrate these values)
TURN_90_TIME = 0.4    # Time needed for 90° turn at current speed
TURN_180_TIME = 0.8   # Time needed for 180° turn (typically 2×90° time)

# Global flag for line-follow mode (used to disable emergency sensor stop)
line_following = False

# -------------------------------
# GPIO Initialization
# -------------------------------
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

# -------------------------------
# Movement Functions
# -------------------------------
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
    pwmA.ChangeDutyCycle(20)
    pwmB.ChangeDutyCycle(20)
    print("Turning 90° left")
    turn_left()
    time.sleep(TURN_90_TIME)
    stop()
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

def turn_right_90():
    pwmA.ChangeDutyCycle(20)
    pwmB.ChangeDutyCycle(20)
    print("Turning 90° right")
    turn_right()
    time.sleep(TURN_90_TIME)
    stop()
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

def turn_180():
    pwmA.ChangeDutyCycle(20)
    pwmB.ChangeDutyCycle(20)
    print("Turning 180°")
    turn_left()  # Change to turn_right() if desired
    time.sleep(TURN_180_TIME)
    stop()
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)

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

# -------------------------------
# Sensor Monitoring Thread (Emergency Stop)
# -------------------------------
def check_sensors():
    while True:
        # Only check for emergency obstacles if NOT in line-follow mode
        if not line_following:
            left_detected = GPIO.input(IR_LEFT) == GPIO.LOW
            right_detected = GPIO.input(IR_RIGHT) == GPIO.LOW
            if left_detected or right_detected:
                left_status = "Line" if left_detected else "No Line"
                right_status = "Line" if right_detected else "No Line"
                print(f"Emergency Stop! Left: {left_status}, Right: {right_status}")
                stop()
        time.sleep(0.1)

sensor_thread = threading.Thread(target=check_sensors, daemon=True)
sensor_thread.start()

# -------------------------------
# Line Follow Mode Function
# -------------------------------
def line_follow_mode():
    global line_following
    print("Entering line follow mode. Press 'e' to exit this mode.")
    line_following = True
    # Save current terminal settings and switch to cbreak (nonblocking) mode
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            # Check if a key is pressed to exit line-follow mode
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if dr:
                ch = sys.stdin.read(1)
                if ch == 'e':  # press 'e' to exit line follow mode
                    print("Exiting line follow mode.")
                    break

            # Read IR sensors: assume sensor returns LOW when detecting a dark line
            left_on_line = (GPIO.input(IR_LEFT) == GPIO.LOW)
            right_on_line = (GPIO.input(IR_RIGHT) == GPIO.LOW)

            # Decision algorithm:
            if left_on_line and right_on_line:
                # Both sensors see the line: go straight
                move_forward()
            elif left_on_line and not right_on_line:
                # Only left sensor sees the line: adjust left
                turn_left()
            elif not left_on_line and right_on_line:
                # Only right sensor sees the line: adjust right
                turn_right()
            else:
                # Neither sensor sees the line: move forward (search for line)
                move_forward()

            time.sleep(0.05)
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        line_following = False
        stop()

# -------------------------------
# Main Control Loop
# -------------------------------
try:
    print("Control the robot with keys:")
    print("w: forward, s: backward, a: left (continuous), d: right (continuous)")
    print("l: enter line-follow mode, r: 90° right, u: 180° turn")
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
            # Enter line-follow mode (this will block until mode is exited)
            line_follow_mode()
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
            print("Exiting program...")
            break
        else:
            print("Unknown command")
        time.sleep(0.1)

finally:
    stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
