import RPi.GPIO as GPIO
import time

# Set the GPIO numbering mode and disable warnings (optional)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the GPIO pin connected to the servo signal wire
SERVO_PIN = 18

# Setup the servo pin as an output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM on the servo pin at 50Hz (typical for servos)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)  # Start PWM with 0% duty cycle

def set_servo_angle(angle):
    """
    Moves the servo to the specified angle.
    
    Args:
        angle (int or float): The target angle (in degrees). Typically 0 to 180.
    """
    # Calculate the duty cycle.
    # This conversion depends on your servo's specific characteristics.
    # A common approximation is:
    #    duty_cycle = (angle / 18) + 2
    duty_cycle = (angle / 18.0) + 2

    # Move the servo to the desired angle
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Allow time for the servo to reach the position
    pwm.ChangeDutyCycle(0)  # Optional: stop sending signal to avoid jitter

try:
    # Set the camera servo to the forward position (90 degrees)
    print("Setting camera to face forward (90°)...")
    set_servo_angle(90)
    time.sleep(2)  # Keep the position for 2 seconds (adjust as needed)
    
finally:
    # Cleanup the PWM and GPIO to ensure a clean exit
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleanup completed.")
