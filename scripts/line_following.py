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
THRESHOLD = 400
SPEED = 10  # Speed as a percentage (10% of max speed)
SENSOR_COUNT = 5  # Number of sensors

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
    pwmA.start(SPEED)  # Start with 10% speed
    pwmB.start(SPEED)

# Move forward
def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

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

# Function to read sensor values (replace this with your sensor reading function)
def read_sensors(sensor):
    """Simulates reading 5 sensor values from an array."""
    return sensor.AnalogRead()

# Main line-following logic
def follow_line():
    print("Starting line-following...")
    sensor = TRSensors.TRSensor()
    while True:
        sensor_values = read_sensors(sensor)
        print(f"Sensor values: {sensor_values}")

        # Determine sensor states (0 = on the line, 1 = off the line)
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        print(f"Sensor states: {sensor_states}")

        if sensor_states == [1, 1, 0, 1, 1]:  # Centered on the line
            forward()
        elif sensor_states in ([0, 0, 0, 1, 1], [0, 0, 1, 1, 1], [0, 1, 1, 1, 1]):  # Off to the right
            turn_left()
        elif sensor_states in ([1, 1, 1, 0, 0], [1, 1, 0, 0, 0], [1, 1, 1, 1, 0]):  # Off to the left
            turn_right()
        else:  # Stop if completely off the line
            stop()

        time.sleep(0.2)  # Read sensor values 5 times per second (every 200 ms)

# Cleanup GPIO
def cleanup():
    GPIO.cleanup()

# Run the script
if __name__ == "__main__":
    try:
        setup_motors()
        follow_line()
    except KeyboardInterrupt:
        print("Line-following interrupted. Stopping...")
        cleanup()
