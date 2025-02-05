import RPi.GPIO as GPIO
import time
import threading

class movement:

    def __init__():
        # Start Sensor Thread
        sensor_thread = threading.Thread(target=check_sensors, daemon=True)
        sensor_thread.start()


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
    TURN_90_TIME = 1    # Time needed for 90° turn at current speed
    MOVE_INCREMENT_TIME = 1 #Time that wheels roll as it moves forward

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

    def step_forward():
        start_distance_measurement()
        pwmA.ChangeDutyCycle(30)
        pwmB.ChangeDutyCycle(30)
        move_forward()
        time.sleep(MOVE_INCREMENT_TIME)
        stop()
        stop_distance_measurement()

    # New timed turn functions
    def turn_left_90():
        start_orientation_measurement()
        pwmA.ChangeDutyCycle(10)
        pwmB.ChangeDutyCycle(10)
        print("Turning 90° left")
        turn_left()
        time.sleep(TURN_90_TIME)
        stop()
        pwmA.ChangeDutyCycle(speed)
        pwmB.ChangeDutyCycle(speed)
        stop_orientation_measurement()

    def turn_right_90():
        start_orientation_measurement()
        pwmA.ChangeDutyCycle(10)
        pwmB.ChangeDutyCycle(10)
        print("Turning 90° right")
        turn_right()
        time.sleep(TURN_90_TIME)
        stop()
        pwmA.ChangeDutyCycle(speed)
        pwmB.ChangeDutyCycle(speed)
        stop_orientation_measurement()

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


    def finish():
        stop()
        GPIO.cleanup()
        print("GPIO cleaned up.")

