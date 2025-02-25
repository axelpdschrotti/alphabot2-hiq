#include <SensorLagSimulator.hpp>

class EnhancedSensorSimulator {
private:
    // For the delayed buffer approach
    std::queue<int> sensorBuffer;
    int baseLagAmount;       // Base amount of lag
    int lagVariability;      // How much the lag can vary
    int sensorIndex;         // Which sensor to affect
    int defaultValue;

    // For intermittent failures
    bool enableFailures;     // Whether failures are enabled
    double failureRate;      // Probability of failure (0.0-1.0)
    int failureValue;        // Value to return when failing
    bool currentlyFailing;   // Is the sensor currently failing
    int failureDuration;     // How long failures last (in readings)
    int failureCounter;      // Current failure counter

    // Random number generation
    std::mt19937 rng;

public:
    EnhancedSensorSimulator(int sensorIndex, int baseLagAmount, int lagVariability = 0, 
                          int defaultValue = 500)
        : sensorIndex(sensorIndex), 
          baseLagAmount(baseLagAmount),
          lagVariability(lagVariability),
          defaultValue(defaultValue),
          enableFailures(false),
          failureRate(0.05),
          failureValue(-1),  // -1 could indicate using last valid reading
          currentlyFailing(false),
          failureDuration(3),
          failureCounter(0) {
        
        // Seed the random number generator
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        rng.seed(seed);
        
        // Fill buffer with default values initially
        // Use a random lag amount within the variability range
        std::uniform_int_distribution<int> lagDist(
            std::max(1, baseLagAmount - lagVariability),
            baseLagAmount + lagVariability);
            
        int initialLag = lagDist(rng);
        for (int i = 0; i < initialLag; i++) {
            sensorBuffer.push(defaultValue);
        }
    }

    // Enable intermittent failures
    void setFailureParameters(bool enable, double rate = 0.05, int duration = 3, int value = -1) {
        enableFailures = enable;
        failureRate = std::max(0.0, std::min(1.0, rate)); // Clamp between 0 and 1
        failureDuration = duration;
        failureValue = value;
        currentlyFailing = false;
        failureCounter = 0;
    }
    
    // Apply effects to a vector of sensor readings
    std::vector<int> processReadings(const std::vector<int>& sensorValues) {
        if (sensorIndex >= sensorValues.size()) {
            return sensorValues; // Safety check
        }

        std::vector<int> result = sensorValues;
        int currentReading = sensorValues[sensorIndex];
        int modifiedReading = currentReading;
        
        // Check for intermittent failures
        if (enableFailures) {
            if (currentlyFailing) {
                // Continue existing failure
                failureCounter--;
                if (failureCounter <= 0) {
                    currentlyFailing = false;
                }
                
                if (failureValue >= 0) {
                    // Use specified failure value
                    modifiedReading = failureValue;
                } else {
                    // Use last valid reading (already in the buffer)
                    modifiedReading = sensorBuffer.back();
                }
            } else {
                // Check if a new failure should start
                std::uniform_real_distribution<double> failDist(0.0, 1.0);
                if (failDist(rng) < failureRate) {
                    currentlyFailing = true;
                    failureCounter = failureDuration;
                    
                    if (failureValue >= 0) {
                        // Use specified failure value
                        modifiedReading = failureValue;
                    }
                }
            }
        }
        
        // Handle variable lag (if not already modified by failure)
        if (!currentlyFailing || failureValue < 0) {
            // Occasionally vary the lag amount
            std::uniform_int_distribution<int> lagChangeDist(0, 10);
            if (lagChangeDist(rng) == 0 && lagVariability > 0) {
                // Adjust buffer size while maintaining minimum lag
                std::uniform_int_distribution<int> lagDist(
                    std::max(1, baseLagAmount - lagVariability),
                    baseLagAmount + lagVariability);
                    
                int newLagAmount = lagDist(rng);
                
                // Adjust buffer size to match new lag amount
                while (sensorBuffer.size() > newLagAmount && sensorBuffer.size() > 1) {
                    sensorBuffer.pop();
                }
                
                while (sensorBuffer.size() < newLagAmount) {
                    sensorBuffer.push(currentReading);
                }
            }
            
            // Get the oldest value from the buffer (if not in failure mode)
            if (!currentlyFailing) {
                modifiedReading = sensorBuffer.front();
                sensorBuffer.pop();
            }
        }
        
        // Always store the current actual reading
        sensorBuffer.push(currentReading);
        
        // Replace current reading with the modified one
        result[sensorIndex] = modifiedReading;
        
        return result;
    }
};