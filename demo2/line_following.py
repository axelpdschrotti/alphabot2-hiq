import RPi.GPIO as GPIO
import time
import TRSensors

# GPIO pins for motor control
IN1 = 13
IN2 = 12
ENA = 6  # Motor A PWM
IN3 = 21
IN4 = 20
ENB = 26  # Motor B PWM

# Threshold for sensor readings to determine if it's on the line
THRESHOLD = 700
#MAXDIFF = 200
SENSOR_COUNT = 5  # Number of sensors
# Turn timing configuration (calibrate these values)
TURN_90_TIME = 0.65    # Time needed for 90° turn at current speed



speedRight = 5
speedLeft = 5

# Initialize GPIO
def setup_motors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)

    global pwmA, pwmB
    pwmA = GPIO.PWM(ENA, 50)  # PWM frequency at 50 Hz
    pwmB = GPIO.PWM(ENB, 50)
    pwmA.start(speedRight)  # Start with 10% speed
    pwmB.start(speedLeft)

# Move forward
def forward(skew = 'N'): # skew can be none 'N', right 'R', or left 'L'
    if(skew == 'L'):
        speedLeft = 6
        speedRight = 9
    elif(skew == 'R'):
        speedRight = 6
        speedLeft = 9
    else:
        speedRight = 6
        speedLeft = 6
    pwmA.ChangeDutyCycle(speedRight)
    pwmB.ChangeDutyCycle(speedLeft)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

# Bear left
def bear_left():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

# Bear right
def bear_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)   # Left motor forward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)  # Right motor backward

# Turn left
def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)  # Left motor backward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)   # Right motor forward

# Turn right
def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)   # Left motor forward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)  # Right motor backward

# Stop motors
def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def turn_left_90():
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(10)
    print("Turning 90° left")
    turn_left()
    time.sleep(TURN_90_TIME)
    stop()

def turn_right_90():
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(10)
    print("Turning 90° right")
    turn_right()
    time.sleep(TURN_90_TIME)
    stop()


# Function to read sensor values (replace this with your sensor reading function)
def read_sensors(sensor):
    """Simulates reading 5 sensor values from an array."""
    return sensor.AnalogRead()

# Main line-following logic
def forward_step():
    print("Starting line-following...")
    sensor = TRSensors.TRSensor()
    max_value = 0
    while True:
        sensor_values = read_sensors(sensor)
        print(f"Sensor values: {sensor_values}")
        #max_sensor_value = max(sensor_values)
        # Determine sensor states (0 = on the line, 1 = off the line)
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        #sensor_states = [0 if (max_sensor_value - value) > MAXDIFF and value < THRESHOLD else 1 for value in sensor_values]

        print(f"Sensor states: {sensor_states}")

        if sensor_states == [1, 1, 0, 1, 1]:  # Centered on the line
            forward('N')
        elif sensor_states in ([1, 0, 1, 1, 1], [0, 1, 1, 1, 1], [1, 0, 0, 1, 1], [0, 0, 1, 1, 1], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1], [0, 1, 0, 1, 1]):  # Off to the right
            forward('R')
        elif sensor_states in ([1, 1, 0, 0, 1], [1, 1, 1, 0, 1], [1, 1, 1, 1, 0], [1, 1, 1, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 0, 1, 0], [1, 0, 0, 0, 1] ):  # Off to the left
            forward('L')
        elif sensor_states == [0, 0, 0, 0, 0]: #Intersection reached
            stop()
            print("We have reached an intersection")
            return False
        else:  # Stop i f completely off the line
            stop()

        time.sleep(0.1)  # Read sensor values 5 times per second (every 200 ms)

# Cleanup GPIO
def cleanup():
    GPIO.cleanup()

# Run the script
if __name__ == "__main__":
    try:
        setup_motors()
        forward_step()
        turn_right_90()
        forward_step()
    except KeyboardInterrupt:
        print("Line-following interrupted. Stopping...")
        cleanup()
