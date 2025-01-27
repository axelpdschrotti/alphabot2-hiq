import RPi.GPIO as GPIO
import time
import keyboard  # For keyboard input

# Motor pins (BCM numbering)
IN1 = 12    # Left motor forward
IN2 = 13    # Left motor backward
IN3 = 20    # Right motor forward
IN4 = 21    # Right motor backward
ENA = 26    # Left motor speed (PWM)
ENB = 19    # Right motor speed (PWM)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize motor pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Set up PWM
pwm_left = GPIO.PWM(ENA, 50)  # 50Hz frequency
pwm_right = GPIO.PWM(ENB, 50)
pwm_left.start(50)  # Start at 50% duty cycle
pwm_right.start(50)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward():
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

# Control the robot using keyboard input
try:
    print("Use arrow keys to control the robot. Press 'q' to quit.")
    while True:
        if keyboard.is_pressed('up'):
            forward()
        elif keyboard.is_pressed('down'):
            backward()
        elif keyboard.is_pressed('left'):
            turn_left()
        elif keyboard.is_pressed('right'):
            turn_right()
        elif keyboard.is_pressed('q'):  # Exit the loop
            break
        else:
            stop()
        time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
