import smbus
import time

I2C_ADDR = 0x40  # TRSensor I2C address
bus = smbus.SMBus(1)

# Calibration data
min_values = [255] * 5
max_values = [0] * 5

def read_trsensors():
    """Read values from the TRSensors via I2C."""
    sensor_values = []
    for i in range(5):
        value = bus.read_byte_data(I2C_ADDR, i)
        sensor_values.append(value)
    return sensor_values

def calibrate_sensors():
    """Calibrate TRSensors by finding min and max values."""
    print("Calibrating sensors... Move the robot over black and white areas.")
    start_time = time.time()
    while time.time() - start_time < 10:  # Calibrate for 10 seconds
        values = read_trsensors()
        for i in range(5):
            min_values[i] = min(min_values[i], values[i])
            max_values[i] = max(max_values[i], values[i])
        print(f"Current values: {values}")
        time.sleep(0.1)
    print(f"Calibration complete.\nMin values: {min_values}\nMax values: {max_values}")

def normalize_sensor_values():
    """Normalize sensor values based on calibration."""
    values = read_trsensors()
    normalized = []
    for i in range(5):
        if max_values[i] == min_values[i]:
            normalized.append(0)
        else:
            norm = (values[i] - min_values[i]) * 100 // (max_values[i] - min_values[i])
            norm = max(0, min(100, norm))  # Clamp between 0 and 100
            normalized.append(norm)
    return normalized

def main():
    calibrate_sensors()
    print("Following the line...")
    while True:
        values = normalize_sensor_values()
        print(f"Normalized values: {values}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
