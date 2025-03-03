#ifndef SENSOR_LAG_SIMULATOR_HPP
#define SENSOR_LAG_SIMULATOR_HPP

#include <queue>
#include <vector>
#include <random>
#include <chrono>

class EnhancedSensorSimulator {
private:
    std::queue<int> sensorBuffer;
    int baseLagAmount;
    int lagVariability;
    int sensorIndex;
    int defaultValue;

    bool enableFailures;
    double failureRate;
    int failureValue;
    bool currentlyFailing;
    int failureDuration;
    int failureCounter;

    std::mt19937 rng;

public:
    EnhancedSensorSimulator(int sensorIndex, int baseLagAmount, int lagVariability = 0, int defaultValue = 500);

    void setFailureParameters(bool enable, double rate = 0.05, int duration = 3, int value = -1);
    std::vector<int> processReadings(const std::vector<int>& sensorValues);
};

#endif // SENSOR_LAG_SIMULATOR_HPP