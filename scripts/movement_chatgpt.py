import RPi.GPIO as GPIO
import time

# Pin configuration for AlphaBot2 motors
IN1 = 13
IN2 = 12
ENA = 6
IN3 = 21
IN4 = 20
ENB = 26

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup motor control pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Initialize PWM for speed control
pwmA = GPIO.PWM(ENA, 50)  # Left motor
pwmB = GPIO.PWM(ENB, 50)  # Right motor
speed = 30  # Initial speed (0-100, in percentage)
pwmA.start(speed)  # Start with the defined speed
pwmB.start(speed)


# Movement functions
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


# Main loop for terminal input
try:
    print("Control the robot using these keys:")
    print("w: forward, s: backward, a: left, d: right, q: stop, e: exit")
    while True:
        command = input("Enter command: ").strip().lower()
        if command == 'w':
            print("Moving forward")
            move_forward()
        elif command == 's':
            print("Moving backward")
            move_backward()
        elif command == 'a':
            print("Turning left")
            turn_left()
        elif command == 'd':
            print("Turning right")
            turn_right()
        elif command == 'q':
            print("Stopping")
            stop()
        elif command == '+':
            increase_speed()
        elif command == '-':
            decrease_speed()
        elif command == 'e':
            print("Exiting program")
            break
        else:
            print("Unknown command. Please use w, a, s, d, q, or e.")
        time.sleep(0.1)

finally:
    print("Cleaning up GPIO...")
    stop()
    GPIO.cleanup()
