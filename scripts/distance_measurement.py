import RPi.GPIO as GPIO
import time

# Encoder GPIO Pins
ENCODER_LEFT = 17
ENCODER_RIGHT = 18

# Wheel properties (adjust according to your AlphaBot2 wheel size)
WHEEL_CIRCUMFERENCE = 13.2  # cm (example, adjust as needed)
PULSES_PER_REV = 20  # Number of encoder pulses per wheel revolution

# Global variables to store encoder counts
left_count = 0
right_count = 0
start_time = None

def setup_encoders():
    """ Initializes GPIO and encoder interrupts """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(ENCODER_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(ENCODER_LEFT, GPIO.RISING, callback=left_wheel_callback)
    GPIO.add_event_detect(ENCODER_RIGHT, GPIO.RISING, callback=right_wheel_callback)

def left_wheel_callback(channel):
    """ Callback function for left wheel encoder """
    global left_count
    left_count += 1

def right_wheel_callback(channel):
    """ Callback function for right wheel encoder """
    global right_count
    right_count += 1

def start_distance_measurement():
    """ Resets encoder counts and starts measuring distance """
    global left_count, right_count, start_time
    left_count = 0
    right_count = 0
    start_time = time.time()
    print("Started distance measurement.")

def stop_distance_measurement():
    """ Stops measuring and calculates distance traveled """
    global start_time
    if start_time is None:
        print("Measurement has not been started.")
        return None

    # Calculate distance based on encoder counts
    left_distance = (left_count / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE
    right_distance = (right_count / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE
    avg_distance = (left_distance + right_distance) / 2  # Average distance

    elapsed_time = time.time() - start_time
    start_time = None  # Reset start time

    print(f"Distance traveled: {avg_distance:.2f} cm in {elapsed_time:.2f} seconds.")
    return avg_distance

def start_orientation_measurement():
    """ Resets encoder counts and starts measuring rotation """
    global left_count, right_count, start_time
    left_count = 0
    right_count = 0
    start_time = time.time()
    print("Started orientation measurement.")

def stop_orientation_measurement():
    """ Stops measuring and calculates the rotation in degrees """
    global start_time
    if start_time is None:
        print("Orientation measurement was not started.")
        return None

    # Compute the distance each wheel traveled
    left_distance = (left_count / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE
    right_distance = (right_count / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE

    # Compute the change in orientation (θ in degrees)
    theta_degrees = ((right_distance - left_distance) / D_TRACK) * (180 / math.pi)

    elapsed_time = time.time() - start_time
    start_time = None  # Reset start time

    print(f"Orientation change: {theta_degrees:.2f} degrees in {elapsed_time:.2f} seconds.")
    return theta_degrees

def cleanup():
    """ Cleans up GPIO before exiting """
    GPIO.cleanup()
