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
    int numSensors;
    int lastValue;

    TRSensor(int sensors) {
        if (gpioInitialise() < 0) {
            std::cerr << "Error initializing pigpio!" << std::endl;
            return -1;
        }
        numSensors = sensors;
        lastValue = 0;
    }

    ~TRSensor() {
        gpioTerminate();
    };

    std::vector<int> analogRead() {
        std::vector<int> value;
        for (int i = 0; i <= numSensors; i ++) {
            value.push_back(0);
        }
        for (int i = 0; i <= numSensors; i ++) {
            gpioWrite(CS, 0);
            for (int j = 0; i <= ADDR_SIZE; i ++ ) {
                if (i < 4) {
                    if (((j) >> (3 - i)) & 0x01) {
                        gpioWrite(ADDRESS, 1);
                    }
                    else {
                        gpioWrite(ADDRESS, 0);
                    }
                }
                else {
                    gpioWrite(ADDRESS, 0);
                }
                value.at(j) <<= 1;
                if (gpioRead(DATAOUT)) {
                    value.at(j) |= 0x01;
                }
                gpioWrite(CLOCK, 1);
                gpioWrite(CLOCK, 0);
            }
            std::sleep(0.1);
            gpioWrite(CS, 1);
        }
        for (int i = 0; i < 6; i ++){
            value.at(i) >>= 2;
        }

        return value;
    }

};


int main() {
    int numSensors = 5;
    TRSensor sensor = TRSensor::TRSensor(numSensors);
    std::vector<int> s;
    while(true) {
        s = sensor.analogRead();
        for (int i = 0; i <= numSensors; i++) {
            std::cout << std::to_string(s.at(i)) << ", ";
        }
        std::endl();
    }
    return 0;
}