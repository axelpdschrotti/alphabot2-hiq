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

# Default threshold for sensor readings to determine if it's on the line.
THRESHOLD = 750  
SENSOR_COUNT = 5  # Number of sensors

# Turn timing configuration (calibrate these values)
TURN_90_TIME = 0.9    # Time needed for 90° turn at current speed
# Intersection timing configuration (calibrate these values)
MOVE_INTERSECTION_TIME = 0.3    # Time needed for intersection

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
    pwmA.start(0)
    pwmB.start(0)

# Move forward
def forward(skew='N'): # skew can be 'N' (none), 'R' (right), or 'L' (left)
    global speedLeft, speedRight
    if skew == 'L':
        speedLeft = 6
        speedRight = 9
    elif skew == 'R':
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
    """Reads 5 sensor values from the sensor array."""
    return sensor.AnalogRead()

# --------------------- Calibration Methods ---------------------

# 1. Static Midpoint Calibration:
def calibrate_static(sensor):
    """
    Calibrates by taking one reading from all sensors and setting the threshold
    as the midpoint between the minimum and maximum sensor values.
    Assumes the robot starts with the outer sensors (white) and the center (black).
    """
    global THRESHOLD
    sensor_values = read_sensors(sensor)
    min_val = min(sensor_values)
    max_val = max(sensor_values)
    THRESHOLD = (min_val + max_val) // 2
    print("Static Calibration: sensor_values =", sensor_values)
    print("Calculated THRESHOLD =", THRESHOLD)

# 2. Individual Sensor Calibration:
def calibrate_individual(sensor):
    """
    Calibrates using the assumption that the center sensor sees the black line
    and the two outer sensors see the white surface. The threshold is set as
    the average between the center sensor reading and the average of the edge readings.
    """
    global THRESHOLD
    sensor_values = read_sensors(sensor)
    center_value = sensor_values[SENSOR_COUNT // 2]  # Middle sensor
    edge_avg = (sensor_values[0] + sensor_values[-1]) / 2.0  # Average of first and last sensor
    THRESHOLD = int((center_value + edge_avg) // 2)
    print("Individual Calibration: sensor_values =", sensor_values)
    print("Center =", center_value, "Edge average =", edge_avg)
    print("Calculated THRESHOLD =", THRESHOLD)

# 3. Multi-Sample Adaptive Calibration:
def calibrate_multi_sample(sensor, samples=50, delay=0.05):
    """
    Takes multiple readings over a period and computes, for each sensor, the minimum
    and maximum values seen. It then calculates a threshold for each sensor as the midpoint,
    and finally sets a global threshold as the average of these midpoints.
    """
    global THRESHOLD
    min_vals = [float('inf')] * SENSOR_COUNT
    max_vals = [0] * SENSOR_COUNT

    print("Starting multi-sample calibration...")
    for i in range(samples):
        values = read_sensors(sensor)
        for j in range(SENSOR_COUNT):
            if values[j] < min_vals[j]:
                min_vals[j] = values[j]
            if values[j] > max_vals[j]:
                max_vals[j] = values[j]
        time.sleep(delay)

    thresholds = [(min_vals[j] + max_vals[j]) // 2 for j in range(SENSOR_COUNT)]
    THRESHOLD = sum(thresholds) // SENSOR_COUNT
    print("Multi-Sample Calibration:")
    print("Min values: ", min_vals)
    print("Max values: ", max_vals)
    print("Individual thresholds: ", thresholds)
    print("Calculated global THRESHOLD =", THRESHOLD)

# --------------------- End Calibration Methods ---------------------

# Main line-following logic
def forward_step():
    print("Starting line-following...")
    sensor = TRSensors.TRSensor()
    calibrate_multi_sample(sensor) # Calibrate the sensors before starting
    while True:
        sensor_values = read_sensors(sensor)
        print(f"Sensor values: {sensor_values}")
        # Determine sensor states (0 = on the line, 1 = off the line)
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        print(f"Sensor states: {sensor_states}")

        if sensor_states in ([1, 1, 0, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 0], [0, 0, 1, 0, 1], [1, 0, 1, 0, 1]):  
            forward('N')
        elif sensor_states in ([1, 0, 1, 1, 1], [0, 1, 1, 1, 1], [1, 0, 0, 1, 1], [0, 0, 1, 1, 1], 
                               [0, 0, 0, 1, 1], [0, 0, 0, 0, 1], [0, 1, 0, 1, 1]):  
            forward('R')
        elif sensor_states in ([1, 1, 0, 0, 1], [1, 1, 1, 0, 1], [1, 1, 1, 1, 0], [1, 1, 1, 0, 0],
                               [1, 1, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 0, 1, 0]):  
            forward('L')
        elif sensor_states == [0, 0, 0, 0, 0]:  # Intersection reached
            time.sleep(MOVE_INTERSECTION_TIME)
            stop()
            print("We have reached an intersection")
            return
        else:
            print("Line following lost")
            stop()
        time.sleep(0.1)

# Cleanup GPIO
def cleanup():
    GPIO.cleanup()

# Run the script
if __name__ == "__main__":
    try:
        setup_motors()
        sensor = TRSensors.TRSensor()
        
        # --- Choose one calibration method before starting ---
        # Option 1: Static Midpoint Calibration
        calibrate_static(sensor)
        
        # Option 2: Individual Sensor Calibration
        # calibrate_individual(sensor)
        
        # Option 3: Multi-Sample Adaptive Calibration
        # calibrate_multi_sample(sensor)
        # -------------------------------------------------------
        
        # Print the final threshold value calculated during calibration
        print("Final THRESHOLD value for line detection:", THRESHOLD)
        
        forward_step()
        turn_right_90()
        forward_step()
    except KeyboardInterrupt:
        print("Line-following interrupted. Stopping...")
        cleanup()
