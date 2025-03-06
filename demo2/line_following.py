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

# Turn/intersection timing configuration (calibrate these values)
TURN_90_TIME = 0.9    # Time needed for 90° turn at current speed
MOVE_INTERSECTION_TIME = 0.3    # Time needed for intersection

speedRight = 5
speedLeft = 5

# Global variable to store the last known line direction: 'L', 'R', or 'N' (for center)
last_line_direction = 'N'

# --------------------- Motor Setup and Basic Movements ---------------------
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

def forward(skew='N'):
    global speedLeft, speedRight, last_line_direction
    if skew == 'L':
        speedLeft = 6
        speedRight = 9
        last_line_direction = 'L'
    elif skew == 'R':
        speedRight = 6
        speedLeft = 9
        last_line_direction = 'R'
    else:
        speedRight = 6
        speedLeft = 6
        last_line_direction = 'N'
    pwmA.ChangeDutyCycle(speedRight)
    pwmB.ChangeDutyCycle(speedLeft)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward():
    # Move backward
    pwmA.ChangeDutyCycle(6)
    pwmB.ChangeDutyCycle(6)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    time.sleep(0.2)
    stop()

def slight_left():
    # Slight left pivot
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(10)
    # For slight left, reverse left motor and forward right motor for a short period.
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    time.sleep(0.3)
    stop()

def slight_right():
    # Slight right pivot
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(10)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    time.sleep(0.3)
    stop()

def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)  # Left motor backward
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)   # Right motor forward

def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)   # Left motor forward
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)  # Right motor backward

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

# --------------------- Sensor and Calibration ---------------------
def read_sensors(sensor):
    """Reads 5 sensor values from the sensor array."""
    return sensor.AnalogRead()

def calibrate_static(sensor):
    global THRESHOLD
    sensor_values = read_sensors(sensor)
    min_val = min(sensor_values)
    max_val = max(sensor_values)
    THRESHOLD = (min_val + max_val) // 2
    print("Static Calibration: sensor_values =", sensor_values)
    print("Calculated THRESHOLD =", THRESHOLD)

def calibrate_individual(sensor):
    global THRESHOLD
    sensor_values = read_sensors(sensor)
    center_value = sensor_values[SENSOR_COUNT // 2]
    edge_avg = (sensor_values[0] + sensor_values[-1]) / 2.0
    THRESHOLD = int((center_value + edge_avg) // 2)
    print("Individual Calibration: sensor_values =", sensor_values)
    print("Center =", center_value, "Edge average =", edge_avg)
    print("Calculated THRESHOLD =", THRESHOLD)

def calibrate_multi_sample(sensor, samples=50, delay=0.05):
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

# --------------------- Recovery Methods ---------------------
def recover_line_simple():
    """
    Simple recovery using the last known direction.
    If the last known was left, move backward a bit then pivot slightly left;
    similarly for right. If no direction is known, try a small pivot both ways.
    """
    global last_line_direction
    print("Attempting simple recovery. Last known direction:", last_line_direction)
    if last_line_direction == 'L':
        backward()
        slight_left()
    elif last_line_direction == 'R':
        backward()
        slight_right()
    else:
        slight_left()
        time.sleep(0.1)
        slight_right()

def recover_line_spin():
    """
    Recovery by slowly spinning in place to search for the line.
    The robot rotates (first to the last known side) until a sensor
    detects the line.
    """
    global last_line_direction
    print("Attempting spinning recovery. Last known direction:", last_line_direction)
    start_time = time.time()
    timeout = 3  # seconds
    if last_line_direction == 'R':
        spin_direction = 'R'
    else:
        spin_direction = 'L'
    
    while time.time() - start_time < timeout:
        if spin_direction == 'L':
            slight_left()
        else:
            slight_right()
        sensor_values = read_sensors(TRSensors.TRSensor())
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        print("Spin recovery sensor states:", sensor_states)
        if 0 in sensor_states:  # line detected on at least one sensor
            print("Line detected during spin recovery.")
            return
    print("Spinning recovery timed out, try another method.")

def recover_line_zigzag():
    """
    Recovery by driving in a zig-zag pattern: drive forward a little,
    then turn left, then right, repeatedly until the line is found.
    """
    print("Attempting zig-zag recovery.")
    for i in range(3):
        forward()
        time.sleep(0.3)
        stop()
        sensor_values = read_sensors(TRSensors.TRSensor())
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        if 0 in sensor_states:
            print("Line detected during zig-zag forward phase.")
            return
        slight_left()
        sensor_values = read_sensors(TRSensors.TRSensor())
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        if 0 in sensor_states:
            print("Line detected during zig-zag left turn.")
            return
        slight_right()
        sensor_values = read_sensors(TRSensors.TRSensor())
        sensor_states = [1 if value > THRESHOLD else 0 for value in sensor_values]
        if 0 in sensor_states:
            print("Line detected during zig-zag right turn.")
            return
    print("Zig-zag recovery did not find the line.")

# Choose which recovery method to use:
# Set recovery_method = 'simple', 'spin', or 'zigzag'
recovery_method = 'spin'

def recover_line():
    print("Line lost. Initiating recovery routine using method:", recovery_method)
    if recovery_method == 'simple':
        recover_line_simple()
    elif recovery_method == 'spin':
        recover_line_spin()
    elif recovery_method == 'zigzag':
        recover_line_zigzag()
    else:
        print("No valid recovery method specified.")

# --------------------- Main Line-Following Logic ---------------------
def forward_step():
    print("Starting line-following...")
    sensor = TRSensors.TRSensor()
    calibrate_static(sensor)  # Calibrate the sensors before starting

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
            print("Line following lost. Initiating recovery...")
            stop()
            recover_line()
        time.sleep(0.1)

# Cleanup GPIO
def cleanup():
    GPIO.cleanup()

# --------------------- Run the Script ---------------------
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
        
        print("Final THRESHOLD value for line detection:", THRESHOLD)
        
        forward_step()
        turn_right_90()
        forward_step()
    except KeyboardInterrupt:
        print("Line-following interrupted. Stopping...")
        cleanup()
