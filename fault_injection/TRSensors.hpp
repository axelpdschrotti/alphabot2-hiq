#ifndef TRSENSOR_HPP
#define TRSENSOR_HPP

#include <iostream>
#include <pigpio.h>
#include <vector>
#include <algorithm>
#include <chrono>
#include <thread>

class EnhancedSensorSimulator;

class TRSensor {
private:
    int numSensors;
    std::vector<int> calibratedMin;
    std::vector<int> calibratedMax;
    int last_value;
    EnhancedSensorSimulator* sensorSimulator;

public:
    TRSensor(int numSensors = 5);
    ~TRSensor();
    
    void enableSensorSimulation(int sensorIndex, int baseLag, int lagVariability = 0);
    void enableIntermittentFailures(bool enable, double rate = 0.05, int duration = 3, int failureValue = 0);
    void disableSensorSimulation();
    std::vector<int> AnalogRead();
    void calibrate();
    std::vector<int> readCalibrated();
    std::pair<int, std::vector<int>> readLine(bool white_line = false);
};

#endif // TRSENSOR_HPP