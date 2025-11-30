#pragma once
#include <vector>
#include "../core/Job.h"
#include "../core/Scheduler.h" // For TimelineEvent struct

class IServer {
public:
    virtual ~IServer() = default;

    // Called when the Scheduler decides to run the Server Task
    // Returns: true if it executed work, false if it yielded (did nothing)
    virtual bool run(Job* serverJob, std::vector<Job*>& aperiodicQueue, 
                     std::vector<TimelineEvent>& history, int currentTime) = 0;

    // Returns the name for logging
    virtual std::string getName() const = 0;
};