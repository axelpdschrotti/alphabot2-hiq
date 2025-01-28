import RPi.GPIO as GPIO
import time

# Sensor pins (BCM numbering)
TRIG_LEFT = 17    # Left sensor trigger
ECHO_LEFT = 18    # Left sensor echo
TRIG_RIGHT = 22   # Right sensor trigger
ECHO_RIGHT = 23   # Right sensor echo

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize sensor pins
GPIO.setup(TRIG_LEFT, GPIO.OUT)
GPIO.setup(ECHO_LEFT, GPIO.IN)
GPIO.setup(TRIG_RIGHT, GPIO.OUT)
GPIO.setup(ECHO_RIGHT, GPIO.IN)

# Set trigger pins to low
GPIO.output(TRIG_LEFT, False)
GPIO.output(TRIG_RIGHT, False)
time.sleep(0.5)  # Let sensors settle

def measure_distance(trig_pin, echo_pin):
    # Send trigger pulse
    GPIO.output(trig_pin, True)
    time.sleep(0.00001)
    GPIO.output(trig_pin, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Wait for echo to rise
    timeout = time.time() + 0.04  # 40ms timeout (~6.8m range)
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None

    # Wait for echo to fall
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to cm
    distance = round(distance, 2)

    # Validate reading (HC-SR04 range is 2-400cm)
    if 2 <= distance <= 400:
        return distance
    return None

try:
    while True:
        # Measure both sensors
        left_dist = measure_distance(TRIG_LEFT, ECHO_LEFT)
        right_dist = measure_distance(TRIG_RIGHT, ECHO_RIGHT)

        # Check for obstacles
        if (left_dist and left_dist <= 20) or (right_dist and right_dist <= 20):
            left_str = f"{left_dist:.1f}cm" if left_dist else "N/A"
            right_str = f"{right_dist:.1f}cm" if right_dist else "N/A"
            print(f"Obstacle detected! Left: {left_str}, Right: {right_str}")

        time.sleep(0.1)  # Short delay between readings

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nProgram stopped")