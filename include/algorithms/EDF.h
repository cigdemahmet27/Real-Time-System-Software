#pragma once
#include "ISchedulingAlgorithm.h"
#include <algorithm>
#include <vector>

class EDF : public ISchedulingAlgorithm {
public:
    Job* pickNextJob(std::vector<Job*>& readyQueue, int currentTime) override {
        if (readyQueue.empty()) return nullptr;

        // Sort based on Absolute Deadline (Dynamic)
        std::sort(readyQueue.begin(), readyQueue.end(), [](Job* a, Job* b) {
            if (a->absoluteDeadline != b->absoluteDeadline) {
                return a->absoluteDeadline < b->absoluteDeadline;
            }
            // Tie-breaker is important for stability
            return a->jobId < b->jobId; 
        });

        return readyQueue.front();
    }

    std::string getName() const override { return "Earliest Deadline First"; }
};