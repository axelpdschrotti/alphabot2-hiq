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
#define ADDR_SIZE 8

class TRSensor {
public:
    int numSensors;
    int lastValue;

    // Constructor
    TRSensor(int sensors) {
        if (gpioInitialise() < 0) {
            std::cerr << "Error initializing pigpio!" << std::endl;
            exit(1); // Use exit() instead of return
        }
        numSensors = sensors;
        lastValue = 0;

        // Set GPIO modes
        gpioSetMode(CS, PI_OUTPUT);
        gpioSetMode(CLOCK, PI_OUTPUT);
        gpioSetMode(ADDRESS, PI_OUTPUT);
        gpioSetMode(DATAOUT, PI_INPUT);
    }

    // Destructor
    ~TRSensor() {
        gpioTerminate();
    }

    // Function to read analog sensor values
    std::vector<int> analogRead() {
        std::vector<int> value(numSensors, 0);

        for (int i = 0; i < numSensors; i++) {  // Fixed loop condition
            gpioWrite(CS, 0);  // Start communication

            for (int j = 0; j < ADDR_SIZE; j++) {  // Fixed loop variable
                if (j < 4) {
                    gpioWrite(ADDRESS, ((i >> (3 - j)) & 0x01));
                } else {
                    gpioWrite(ADDRESS, 0);
                }

                value[i] <<= 1;
                if (gpioRead(DATAOUT)) {
                    value[i] |= 0x01;
                }

                gpioWrite(CLOCK, 1);
                gpioWrite(CLOCK, 0);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(100));  // Fixed sleep syntax
            gpioWrite(CS, 1);  // Stop communication
        }

        // Right-shift values
        for (int i = 0; i < numSensors; i++) {
            value[i] >>= 2;
        }

        return value;
    }
};

int main() {
    int numSensors = 5;
    TRSensor sensor(numSensors);

    while (true) {
        std::vector<int> s = sensor.analogRead();

        for (int i = 0; i < numSensors; i++) {  // Fixed loop condition
            std::cout << s[i] << ", ";
        }

        std::cout << std::endl;  // Fixed std::endl usage

        std::this_thread::sleep_for(std::chrono::milliseconds(500));  // 500ms delay
    }

    return 0;
}
