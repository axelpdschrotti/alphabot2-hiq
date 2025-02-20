#include <iostream>
#include <thread>
#include <chrono>
#include <vector>

// Simulated function to get IR sensor data
std::vector<int> getSensorData() {
    
}

// Introduce artificial delay in sensor response
std::vector<int> getDelayedSensorData(int delay_ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    return getSensorData();
}

int main() {
    int delay_ms = 200;  // Simulated lag in milliseconds

    while (true) {
        std::vector<int> sensorData = getDelayedSensorData(delay_ms);
        
        std::cout << "Sensor Data (Lagged): ";
        for (int value : sensorData) {
            std::cout << value << " ";
        }
        std::cout << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(500)); // Regular polling
    }

    return 0;
}
