#include <iostream>
#include <pigpio.h>
#include <thread>
#include <chrono>
#include <vector>

#define CS 5         // Chip Select
#define CLOCK 25     // Clock Signal
#define ADDRESS 24   // Address Line
#define DATAOUT 23   // Data Out (Sensor readings)
#define BUTTON 7     // Button Input
#define ADDR_SIZE 4  // Number of address bits (adjust if needed)

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
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    return 0;
}


// int main() {
//     int numSensors = 5;
//     TRSensor sensor(numSensors);

//     while (true) {
//         std::vector<int> s = sensor.analogRead();

//         for (int i = 0; i < numSensors; i++) {
//             std::cout << s[i] << ", ";
//         }

//         std::cout << std::endl;

//         std::this_thread::sleep_for(std::chrono::milliseconds(500));
//     }

//     return 0;
// }
