#pragma once
#include "Task.h"

struct Job {
    int jobId;                  // Unique Job ID (or instance number)
    const Task* task;           // Pointer back to the parent Task Definition
    
    int arrivalTime;            // Absolute time this job arrived (t)
    int absoluteDeadline;       // arrivalTime + task->relativeDeadline
    int remainingExecutionTime; // Starts at task->computationTime, decreases to 0
    int startTime;              // When it first started running (-1 if not started)
    int finishTime;             // When it finished (-1 if not finished)

    // Constructor
    Job(int jId, const Task* t, int arrival)
        : jobId(jId), task(t), arrivalTime(arrival),
          absoluteDeadline(arrival + t->relativeDeadline),
          remainingExecutionTime(t->computationTime),
          startTime(-1), finishTime(-1) {}

    // Helper to calculate Slack for LST
    int getSlack(int currentTime) const {
        // Slack = (Deadline - current_time) - remaining_work
        return (absoluteDeadline - currentTime) - remainingExecutionTime;
    }

    // Check if job is complete
    bool isComplete() const {
        return remainingExecutionTime <= 0;
    }
};