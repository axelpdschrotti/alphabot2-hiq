import RPi.GPIO as GPIO
import time

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

# Example usage
try:
    while True:
        forward()
        time.sleep(2)
        turn_left()
        time.sleep(1)
        forward()
        time.sleep(2)
        turn_right()
        time.sleep(1)
        backward()
        time.sleep(2)
        stop()
        time.sleep(1)
        
except KeyboardInterrupt:
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()