#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <deque>
#include <fstream>
#include <iomanip>
#include "SensorLagSimulator.hpp"
#include "../sensor_adaptation/TRSensors.hpp"

// Class to detect anomalies in sensor readings
class SensorAnomalyDetector {
private:
    // Store recent readings per sensor for analysis
    std::vector<std::deque<int>> sensorHistory;
    std::vector<double> sensorBaselines;
    std::vector<double> sensorVariances;
    
    // Configuration
    int historySize;
    double anomalyThreshold;
    int warmupReadings;
    int numSensors;
    
    // Tracking
    int readingsProcessed;
    std::vector<int> anomalyCounter;
    std::vector<int> lagCounter;
    
    // Logging
    std::ofstream logFile;

public:
    SensorAnomalyDetector(int numSensors, int historySize = 20, double anomalyThreshold = 2.5)
        : numSensors(numSensors), 
          historySize(historySize), 
          anomalyThreshold(anomalyThreshold),
          warmupReadings(historySize * 2),
          readingsProcessed(0)
    {
        // Initialize containers
        sensorHistory.resize(numSensors);
        sensorBaselines.resize(numSensors, 0.0);
        sensorVariances.resize(numSensors, 0.0);
        anomalyCounter.resize(numSensors, 0);
        lagCounter.resize(numSensors, 0);
        
        // Initialize log file
        logFile.open("sensor_anomalies.log");
        if (logFile.is_open()) {
            logFile << "Timestamp,SensorID,Reading,Baseline,StdDev,Z-Score,AnomalyType" << std::endl;
        }
    }
    
    ~SensorAnomalyDetector() {
        if (logFile.is_open()) {
            logFile.close();
        }
    }
    
    // Process new sensor readings
    void processReadings(const std::vector<int>& readings) {
        auto now = std::chrono::system_clock::now();
        auto timestamp = std::chrono::system_clock::to_time_t(now);
        
        if (readings.size() != numSensors) {
            std::cerr << "Warning: Expected " << numSensors << " readings, got " 
                      << readings.size() << std::endl;
            return;
        }
        
        readingsProcessed++;
        
        // Update history for each sensor
        for (int i = 0; i < numSensors; i++) {
            int reading = readings[i];
            sensorHistory[i].push_back(reading);
            
            // Keep history at specified size
            if (sensorHistory[i].size() > historySize) {
                sensorHistory[i].pop_front();
            }
            
            // After warmup period, update baselines and check for anomalies
            if (readingsProcessed >= warmupReadings) {
                // Compute baseline (moving average) and variance
                updateStatistics(i);
                
                // Check for anomalies
                checkForAnomalies(i, timestamp);
            }
            // During warmup, just update statistics
            else if (sensorHistory[i].size() == historySize) {
                updateStatistics(i);
            }
        }
        
        // Cross-sensor anomaly detection (after warmup)
        if (readingsProcessed >= warmupReadings) {
            detectCrossSensorAnomalies(readings, timestamp);
        }
    }
    
    // Print a summary of detected anomalies
    void printSummary() {
        std::cout << "\n===== Sensor Anomaly Detection Summary =====\n";
        std::cout << "Readings processed: " << readingsProcessed << std::endl;
        std::cout << "Anomalies detected per sensor:\n";
        
        for (int i = 0; i < numSensors; i++) {
            std::cout << "  Sensor " << i << ": " << anomalyCounter[i] << " anomalies, " 
                      << lagCounter[i] << " potential lags" << std::endl;
        }
        
        std::cout << "Detailed log saved to 'sensor_anomalies.log'\n";
    }

private:
    // Update baseline and variance for a sensor
    void updateStatistics(int sensorId) {
        const auto& history = sensorHistory[sensorId];
        
        // Calculate mean
        double sum = std::accumulate(history.begin(), history.end(), 0.0);
        double mean = sum / history.size();
        
        // Calculate variance
        double variance = 0.0;
        for (int value : history) {
            double diff = value - mean;
            variance += diff * diff;
        }
        variance /= history.size();
        
        // Exponential moving average for baseline and variance
        const double alpha = 0.1; // Smoothing factor
        if (sensorBaselines[sensorId] == 0.0) {
            // First calculation
            sensorBaselines[sensorId] = mean;
            sensorVariances[sensorId] = std::max(variance, 1.0); // Avoid division by zero
        } else {
            // Update with new data
            sensorBaselines[sensorId] = alpha * mean + (1 - alpha) * sensorBaselines[sensorId];
            sensorVariances[sensorId] = alpha * variance + (1 - alpha) * sensorVariances[sensorId];
            sensorVariances[sensorId] = std::max(sensorVariances[sensorId], 1.0); // Ensure minimum variance
        }
    }
    
    // Check a sensor for anomalies
    void checkForAnomalies(int sensorId, time_t timestamp) {
        if (sensorHistory[sensorId].empty()) return;
        
        int currentReading = sensorHistory[sensorId].back();
        double baseline = sensorBaselines[sensorId];
        double stdDev = std::sqrt(sensorVariances[sensorId]);
        
        // Calculate z-score (distance from mean in standard deviations)
        double zScore = std::abs(currentReading - baseline) / stdDev;
        
        // Check for statistical anomalies (spikes)
        if (zScore > anomalyThreshold) {
            anomalyCounter[sensorId]++;
            logAnomaly(timestamp, sensorId, currentReading, baseline, stdDev, zScore, "Spike");
            
            std::cout << "ANOMALY DETECTED: Sensor " << sensorId 
                      << " reading (" << currentReading << ") is " 
                      << zScore << " standard deviations from baseline" << std::endl;
        }
        
        // Check for lag (repeated or slowly changing values)
        if (sensorHistory[sensorId].size() >= 3) {
            auto it = sensorHistory[sensorId].rbegin();
            int curr = *it++;
            int prev = *it++;
            int prevPrev = *it;
            
            // Simple lag detection: values changing too slowly
            double expectedChange = stdDev * 0.5; // Expect some change around 0.5 stddev
            
            if (std::abs(curr - prev) < expectedChange && 
                std::abs(prev - prevPrev) < expectedChange &&
                stdDev > 5.0) { // Only if we expect significant variation
                
                lagCounter[sensorId]++;
                logAnomaly(timestamp, sensorId, currentReading, baseline, stdDev, zScore, "Lag");
                
                std::cout << "POTENTIAL LAG DETECTED: Sensor " << sensorId 
                          << " showing minimal variation (" << curr << ", " << prev << ", " << prevPrev << ")" 
                          << std::endl;
            }
        }
    }
    
    // Detect anomalies across sensors (comparing patterns)
    void detectCrossSensorAnomalies(const std::vector<int>& readings, time_t timestamp) {
        // Simple correlation check - in a normal system, sensors often change together
        // Find sensors that are moving opposite to the group
        
        // Calculate overall trend
        int trendCount = 0;
        for (int i = 0; i < numSensors; i++) {
            if (sensorHistory[i].size() >= 2) {
                int curr = sensorHistory[i].back();
                int prev = *(sensorHistory[i].rbegin() + 1);
                
                if (curr > prev) trendCount++;
                else if (curr < prev) trendCount--;
            }
        }
        
        // If there's a strong trend, check for sensors going against it
        if (std::abs(trendCount) >= 3) { // 3+ sensors showing same direction
            bool increasingTrend = (trendCount > 0);
            
            for (int i = 0; i < numSensors; i++) {
                if (sensorHistory[i].size() >= 2) {
                    int curr = sensorHistory[i].back();
                    int prev = *(sensorHistory[i].rbegin() + 1);
                    
                    bool sensorIncreasing = (curr > prev);
                    
                    // This sensor is going against the trend
                    if (sensorIncreasing != increasingTrend && 
                        std::abs(curr - prev) > std::sqrt(sensorVariances[i])) {
                        
                        anomalyCounter[i]++;
                        double zScore = std::abs(curr - sensorBaselines[i]) / std::sqrt(sensorVariances[i]);
                        
                        logAnomaly(timestamp, i, curr, sensorBaselines[i], 
                                  std::sqrt(sensorVariances[i]), zScore, "CrossSensor");
                        
                        std::cout << "CROSS-SENSOR ANOMALY: Sensor " << i 
                                  << " moving opposite to group trend" << std::endl;
                    }
                }
            }
        }
    }
    
    // Log an anomaly to the file
    void logAnomaly(time_t timestamp, int sensorId, int reading, 
                    double baseline, double stdDev, double zScore, 
                    const std::string& anomalyType) {
        if (!logFile.is_open()) return;
        
        logFile << std::put_time(std::localtime(&timestamp), "%Y-%m-%d %H:%M:%S") << ","
                << sensorId << ","
                << reading << ","
                << baseline << ","
                << stdDev << ","
                << zScore << ","
                << anomalyType << std::endl;
    }
};

// Robot controller that uses sensor data for navigation
class RobotController {
private:
    // Control parameters
    double baseSpeed;
    double turnSensitivity;
    bool running;
    
    // Last command
    double leftMotorSpeed;
    double rightMotorSpeed;

public:
    RobotController(double baseSpeed = 0.5, double turnSensitivity = 0.2) 
        : baseSpeed(baseSpeed), 
          turnSensitivity(turnSensitivity),
          running(false),
          leftMotorSpeed(0),
          rightMotorSpeed(0) {}
    
    // Start the robot
    void start() {
        running = true;
        std::cout << "Robot controller started" << std::endl;
    }
    
    // Stop the robot
    void stop() {
        running = false;
        leftMotorSpeed = 0;
        rightMotorSpeed = 0;
        std::cout << "Robot controller stopped" << std::endl;
    }
    
    // Process sensor readings and calculate motor commands
    void processReadings(const std::pair<int, std::vector<int>>& sensorData) {
        if (!running) return;
        
        int position = sensorData.first;
        const std::vector<int>& readings = sensorData.second;
        
        // Calculate normalized position (-1.0 to 1.0)
        // Assuming position is between 0 and 4000 (for 5 sensors)
        double normalizedPosition = (position - 2000) / 2000.0;
        
        // Calculate motor speeds based on position
        // Simple proportional control
        leftMotorSpeed = baseSpeed - (normalizedPosition * turnSensitivity);
        rightMotorSpeed = baseSpeed + (normalizedPosition * turnSensitivity);
        
        // Clamp motor speeds
        leftMotorSpeed = std::max(0.0, std::min(1.0, leftMotorSpeed));
        rightMotorSpeed = std::max(0.0, std::min(1.0, rightMotorSpeed));
        
        // Print command (would actually control motors in a real implementation)
        std::cout << "Motor command: L=" << std::fixed << std::setprecision(2) << leftMotorSpeed 
                  << " R=" << rightMotorSpeed << " (position=" << position << ")" << std::endl;
    }
};

// Main program
int main() {
    // Create the sensor, anomaly detector, and robot controller
    TRSensor sensor;
    SensorAnomalyDetector detector(5); // 5 sensors
    RobotController robot(0.6, 0.3);   // Base speed 0.6, sensitivity 0.3
    
    // Configure sensor simulation for testing
    // Middle sensor (index 2) with variable lag
    sensor.enableSensorSimulation(2, 8, 3);  // Base lag 8, variability ±3
    
    // Enable intermittent failures on sensor 4
    sensor.enableIntermittentFailures(true, 0.1, 5, 0);  // 10% chance, 5 readings duration, value 0
    
    std::cout << "Starting robot simulation with sensor anomalies..." << std::endl;
    std::cout << "Press Ctrl+C to stop" << std::endl;
    
    robot.start();
    
    try {
        // Main control loop
        for (int i = 0; i < 500; i++) {  // Run for 500 cycles (or until interrupted)
            // Read sensors
            std::vector<int> rawReadings = sensor.AnalogRead();
            
            // Process raw readings for anomaly detection
            detector.processReadings(rawReadings);
            
            // Get calibrated readings for robot control
            std::pair<int, std::vector<int>> calibratedData = sensor.readLine();
            
            // Control robot based on readings
            robot.processReadings(calibratedData);
            
            // Simulate different line positions over time (for testing)
            if (i % 50 == 0) {
                // Simulate a change in the line position by manipulating the raw readings
                // This is just for testing - in a real robot this would happen naturally
                // as the robot moves over the line
                std::cout << "\n--- Simulating line position change ---\n" << std::endl;
            }
            
            // Sleep to simulate processing time
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "Unknown error" << std::endl;
    }
    
    // Stop the robot
    robot.stop();
    
    // Print anomaly detection summary
    detector.printSummary();
    
    // Disable sensor simulation
    sensor.disableSensorSimulation();
    
    std::cout << "Simulation complete" << std::endl;
    return 0;
}