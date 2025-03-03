#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <deque>
#include <fstream>
#include <iomanip>
#include "../sensor_adaptation/TRSensors.hpp"

void printSensorData(TRSensor sensor, std::string filename) {

    std::vector<int> sensorData;
    time_t timestamp;
    time_t startTime;
    time(&startTime);
    std::ofstream(myfile);
    myfile.open(filename);
    while(true) {
        sensorData = sensor.AnalogRead();
        time(&timestamp);
        myfile << timestamp << ": ";
        for (int value : sensorData) {
            myfile << value << ", ";
        }
        myfile << "\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        if(difftime(timestamp, startTime) > 20) {
            break;
        }
    }
    myfile.close();
}

int main() {
    TRSensor sensor1(5);
    TRSensor sensor2(5);

    std::thread t1(printSensorData, sensor1, "sensor1_data.txt");
    std::thread t2(printSensorData, sensor2, "sensor2_data.txt");
    t1.join():
    t2.join();

    return 0;
};
