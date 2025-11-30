#include "../../include/servers/PollingServer.h"

bool PollingServer::run(Job* serverJob, std::vector<Job*>& aperiodicQueue, 
                        std::vector<TimelineEvent>& history, int currentTime) {
    
    // Rule: Check Aperiodic Queue
    if (!aperiodicQueue.empty()) {
        // 1. We have work! Run the Aperiodic Job.
        Job* aJob = aperiodicQueue.front();

        // Log the execution
        history.push_back({currentTime, aJob->jobId, aJob->task->id, "ServerExec"});

        // Decrement both the Aperiodic Job AND the Server Budget
        aJob->remainingExecutionTime--;
        serverJob->remainingExecutionTime--; 

        // Check completion of Aperiodic Job
        if (aJob->remainingExecutionTime <= 0) {
            history.push_back({currentTime + 1, aJob->jobId, aJob->task->id, "AperiodicFinish"});
            delete aJob;
            aperiodicQueue.erase(aperiodicQueue.begin());
        }
        return true; // We did work
    } else {
        // 2. Queue is Empty -> POLLING RULE: LOSE BUDGET IMMEDIATELY
        // By setting time to 0, the Scheduler will remove the Server Job 
        // from the Ready Queue this tick.
        serverJob->remainingExecutionTime = 0; 
        return false; // We yielded
    }
}