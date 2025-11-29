#pragma once
#include <vector>
#include <string>
#include "../core/Job.h"

class ISchedulingAlgorithm {
public:
    virtual ~ISchedulingAlgorithm() = default;

    // The core function: Look at the queue, pick the best job
    virtual Job* pickNextJob(std::vector<Job*>& readyQueue, int currentTime) = 0;
    
    virtual std::string getName() const = 0;
};