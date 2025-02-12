import smbus
import time

# I2C address of the TRSensor module (default may be 0x48 or check in your manual)
I2C_ADDR = 0x40
bus = smbus.SMBus(1)  # Use I2C bus 1 on Raspberry Pi

def read_trsensors():
    """Read values from the TRSensors via I2C and return a list of sensor readings."""
    sensor_values = []
    for i in range(5):  # Assuming there are 5 sensors
        value = bus.read_byte_data(I2C_ADDR, i)
        sensor_values.append(value)
    return sensor_values

def main():
    print("Reading TRSensors...")
    while True:
        values = read_trsensors()
        print(f"Sensor values: {values}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
