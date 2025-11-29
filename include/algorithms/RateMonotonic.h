#pragma once
#include "algorithms/ISchedulingAlgorithm.h"
#include <algorithm>

class RateMonotonic : public ISchedulingAlgorithm {
public:
    Job* pickNextJob(std::vector<Job*>& readyQueue, int currentTime) override {
        if (readyQueue.empty()) return nullptr;

        // Sort based on Period (Static Priority)
        // If periods are equal, use ID as tie-breaker
        std::sort(readyQueue.begin(), readyQueue.end(), [](Job* a, Job* b) {
            if (a->task->period != b->task->period) {
                return a->task->period < b->task->period; // Smaller period = Higher priority
            }
            return a->jobId < b->jobId; // FIFO for ties
        });

        // The first element is now the highest priority
        return readyQueue.front();
    }

    std::string getName() const override {
        return "Rate Monotonic";
    }
};