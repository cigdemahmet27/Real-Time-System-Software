#pragma once
#include "ISchedulingAlgorithm.h"
#include <algorithm>
#include <vector>

class LeastSlackTime : public ISchedulingAlgorithm {
public:
    Job* pickNextJob(std::vector<Job*>& readyQueue, int currentTime) override {
        if (readyQueue.empty()) return nullptr;

        // We capture 'currentTime' in the lambda []
        std::sort(readyQueue.begin(), readyQueue.end(), [currentTime](Job* a, Job* b) {
            int slackA = a->getSlack(currentTime);
            int slackB = b->getSlack(currentTime);

            if (slackA != slackB) {
                return slackA < slackB; // Smaller slack = Higher priority
            }
            return a->jobId < b->jobId; // Tie-breaker
        });

        return readyQueue.front();
    }

    std::string getName() const override { return "Least Slack Time"; }
};