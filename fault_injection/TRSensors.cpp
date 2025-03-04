#include "TRSensors.hpp"

// Define GPIO pins
const int CS = 5;
const int Clock = 25;
const int Address = 24;
const int DataOut = 23;
const int Button = 7;

TRSensor::TRSensor(int numSensors) : numSensors(numSensors), last_value(0), sensorSimulator(nullptr) {
    // Initialize calibration values
    calibratedMin.resize(numSensors, 0);
    calibratedMax.resize(numSensors, 1023);

    // Initialize GPIO
    if (gpioInitialise() < 0) {
        std::cerr << "Failed to initialize pigpio" << std::endl;
        exit(1);
    }

    // Set up GPIO pins
    gpioSetMode(Clock, PI_OUTPUT);
    gpioSetMode(Address, PI_OUTPUT);
    gpioSetMode(CS, PI_OUTPUT);
    gpioSetMode(DataOut, PI_INPUT);
    gpioSetPullUpDown(DataOut, PI_PUD_UP);
    gpioSetMode(Button, PI_INPUT);
    gpioSetPullUpDown(Button, PI_PUD_UP);
}

TRSensor::~TRSensor() {
    gpioTerminate();
}

void TRSensor::enableSensorSimulation(int sensorIndex, int baseLag, int lagVariability) {
    sensorSimulator = new EnhancedSensorSimulator(sensorIndex, baseLag, lagVariability);
}

void TRSensor::enableIntermittentFailures(bool enable, double rate, int duration, int failureValue) {
    if (sensorSimulator) {
        sensorSimulator->setFailureParameters(enable, rate, duration, failureValue);
    }
}

void TRSensor::disableSensorSimulation() {
    if (sensorSimulator) {
        sensorSimulator = nullptr;
    }
}

std::vector<int> TRSensor::AnalogRead() {
    std::vector<int> values(numSensors + 1, 0);

    // Read Channel0~channel6 AD value
    for (int j = 0; j <= numSensors; j++) {
        gpioWrite(CS, PI_LOW);
        
        for (int i = 0; i < 8; i++) {
            // Send 8-bit Address
            if (i < 4) {
                if ((j >> (3 - i)) & 0x01) {
                    gpioWrite(Address, PI_HIGH);
                } else {
                    gpioWrite(Address, PI_LOW);
                }
            } else {
                gpioWrite(Address, PI_LOW);
            }

            // Read MSB 4-bit data
            values[j] <<= 1;
            if (gpioRead(DataOut)) {
                values[j] |= 0x01;
            }
            gpioWrite(Clock, PI_HIGH);
            gpioWrite(Clock, PI_LOW);
        }

        for (int i = 0; i < 4; i++) {
            // Read LSB 8-bit data
            values[j] <<= 1;
            if (gpioRead(DataOut)) {
                values[j] |= 0x01;
            }
            gpioWrite(Clock, PI_HIGH);
            gpioWrite(Clock, PI_LOW);
        }

        // Short delay
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        gpioWrite(CS, PI_HIGH);
    }

    // Right shift values by 2
    for (int i = 0; i < 6; i++) {
        values[i] >>= 2;
    }

    // Apply simulation effects if enabled
    if (sensorSimulator) {
        values = sensorSimulator->processReadings(values);
    }

    // Return values[1:] (equivalent to Python's array slicing)
    std::vector<int> result(values.begin() + 1, values.end());

    return result;
}

void TRSensor::calibrate() {
    std::vector<int> max_sensor_values(numSensors, 0);
    std::vector<int> min_sensor_values(numSensors, 0);

    for (int j = 0; j < 10; j++) {
        std::vector<int> sensor_values = AnalogRead();

        for (int i = 0; i < numSensors; i++) {
            // Set the max we found THIS time
            if ((j == 0) || max_sensor_values[i] < sensor_values[i]) {
                max_sensor_values[i] = sensor_values[i];
            }

            // Set the min we found THIS time
            if ((j == 0) || min_sensor_values[i] > sensor_values[i]) {
                min_sensor_values[i] = sensor_values[i];
            }
        }
    }
    
    // Record the min and max calibration values
    for (int i = 0; i < numSensors; i++) {
        if (min_sensor_values[i] > calibratedMin[i]) {
            calibratedMin[i] = min_sensor_values[i];
        }
        if (max_sensor_values[i] < calibratedMax[i]) {
            calibratedMax[i] = max_sensor_values[i];
        }
    }
}

std::vector<int> TRSensor::safeAnalogRead() {
    std::lock_guard<std::mutex> lock(sensorMutex);
    sensorMutex.lock();
    std::vector<int> sensor_values = AnalogRead();
    sensorMutex.unlock();
    return sensor_values;
}

std::vector<int> TRSensor::readCalibrated() {
    // Read the needed values
    std::vector<int> sensor_values = AnalogRead();

    for (int i = 0; i < numSensors; i++) {
        int denominator = calibratedMax[i] - calibratedMin[i];
        int value = 0;

        if (denominator != 0) {
            value = (sensor_values[i] - calibratedMin[i]) * 1000 / denominator;
        }

        if (value < 0) {
            value = 0;
        } else if (value > 1000) {
            value = 1000;
        }

        sensor_values[i] = value;
    }

    return sensor_values;
}

std::pair<int, std::vector<int>> TRSensor::readLine(bool white_line) {
    std::vector<int> sensor_values = readCalibrated();
    int avg = 0;
    int sum = 0;
    bool on_line = false;

    for (int i = 0; i < numSensors; i++) {
        int value = sensor_values[i];

        if (white_line) {
            value = 1000 - value;
        }

        // Keep track of whether we see the line at all
        if (value > 200) {
            on_line = true;
        }

        // Only average in values that are above a noise threshold
        if (value > 50) {
            avg += value * (i * 1000);  // This is for the weighted total
            sum += value;               // This is for the denominator
        }
    }
    
    if (!on_line) {
        // If it last read to the left of center, return 0
        if (last_value < (numSensors - 1) * 1000 / 2) {
            last_value = 0;
        }
        // If it last read to the right of center, return the max
        else {
            last_value = (numSensors - 1) * 1000;
        }
    } else {
        last_value = avg / sum;
    }
    
    return std::make_pair(last_value, sensor_values);
}