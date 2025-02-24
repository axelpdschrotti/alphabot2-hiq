#include <iostream>
#include <pigpio.h>
#include <thread>
#include <chrono>
#include <vector>

#define CS 5
#define CLOCK 25
#define ADDRESS 0
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

        for (int i = 0; i < numSensors; i++) {
            gpioWrite(CS, 0);

            for (int j = 0; j < ADDR_SIZE; j++) {
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

            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            gpioWrite(CS, 1);
        }

        for (int i = 0; i < 6; i++) {
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

        for (int i = 0; i < numSensors; i++) {
            std::cout << s[i] << ", ";
        }

        std::cout << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    return 0;
}
