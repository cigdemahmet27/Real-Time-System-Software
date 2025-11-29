#pragma once
#include "ISchedulingAlgorithm.h"
#include <algorithm>
#include <vector>

class DeadlineMonotonic : public ISchedulingAlgorithm {
public:
    Job* pickNextJob(std::vector<Job*>& readyQueue, int currentTime) override {
        if (readyQueue.empty()) return nullptr;

        // Sort based on Relative Deadline (Static)
        std::sort(readyQueue.begin(), readyQueue.end(), [](Job* a, Job* b) {
            if (a->task->relativeDeadline != b->task->relativeDeadline) {
                return a->task->relativeDeadline < b->task->relativeDeadline;
            }
            return a->jobId < b->jobId; // Tie-breaker: FIFO
        });

        return readyQueue.front();
    }

    std::string getName() const override { return "Deadline Monotonic"; }
};