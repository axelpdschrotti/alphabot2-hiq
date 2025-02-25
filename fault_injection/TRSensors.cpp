#include <iostream>
#include <pigpio.h>
#include <thread>
#include <chrono>
#include <vector>

#define CS 5
#define CLOCK 25
#define ADDRESS 24
#define DATAOUT 23
#define BUTTON 7
#define ADDR_SIZE 2

class TRSensor {
public:
    int numSensors;
    int lastValue;

    // Constructor
    TRSensor(int sensors) {
        if (gpioInitialise() < 0) {
            std::cerr << "Error initializing pigpio!" << std::endl;
            exit(1);
        }
        numSensors = sensors;
        lastValue = 0;

        gpioSetMode(CS, PI_OUTPUT);
        gpioSetMode(CLOCK, PI_OUTPUT);
        gpioSetMode(ADDRESS, PI_OUTPUT);
        gpioSetMode(DATAOUT, PI_INPUT);
        gpioSetMode(BUTTON, PI_INPUT);

        gpioSetPullUpDown(DATAOUT, PI_PUD_UP);
        gpioSetPullUpDown(BUTTON, PI_PUD_UP);
    }

    // Destructor
    ~TRSensor() {
        gpioTerminate();
    }

    // Function to read analog sensor values
    std::vector<int> analogRead() {
        std::vector<int> value(numSensors, 0);

        gpioWrite(CS, 0);  // Activate Chip Select

        for (int i = 0; i < numSensors; i++) {
            // Send the sensor address (one at a time)
            for (int j = 0; j < ADDR_SIZE; j++) {
                int bitValue = (i >> (ADDR_SIZE - 1 - j)) & 0x01;
                gpioWrite(ADDRESS, bitValue);

                gpioWrite(CLOCK, 1);  // Pulse clock high
                std::this_thread::sleep_for(std::chrono::microseconds(10));
                gpioWrite(CLOCK, 0);  // Pulse clock low
            }

            // Read sensor value
            for (int j = 0; j < 10; j++) {  // Assuming 10-bit sensor resolution
                value[i] <<= 1;
                if (gpioRead(DATAOUT)) {
                    value[i] |= 0x01;
                }

                gpioWrite(CLOCK, 1);
                std::this_thread::sleep_for(std::chrono::microseconds(10));
                gpioWrite(CLOCK, 0);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(5));  // Short delay
        }

        gpioWrite(CS, 1);  // Deactivate Chip Select

        // Debug: Print the raw sensor values
        std::cout << "Sensor Readings: ";
        for (int i = 0; i < numSensors; i++) {
            std::cout << "S" << i << ":" << value[i] << " ";
        }
        std::cout << std::endl;

        return value;
    }
};

int main() {
    int numSensors = 5;
    TRSensor sensor(numSensors);

    while (true) {
        std::vector<int> readings = sensor.analogRead();

        // Check if values change independently when a sensor is touched
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    return 0;
}
