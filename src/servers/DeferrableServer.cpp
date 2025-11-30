#include "../../include/servers/DeferrableServer.h"

bool DeferrableServer::run(Job* serverJob, std::vector<Job*>& aperiodicQueue, 
                           std::vector<TimelineEvent>& history, int currentTime) {
    
    if (!aperiodicQueue.empty()) {
        // 1. We have work! (Same as Poller)
        Job* aJob = aperiodicQueue.front();
        history.push_back({currentTime, aJob->jobId, aJob->task->id, "ServerExec(DS)"});

        aJob->remainingExecutionTime--;
        serverJob->remainingExecutionTime--; 

        if (aJob->remainingExecutionTime <= 0) {
            history.push_back({currentTime + 1, aJob->jobId, aJob->task->id, "AperiodicFinish"});
            delete aJob;
            aperiodicQueue.erase(aperiodicQueue.begin());
        }
        return true;
    } else {
        // 2. Queue is Empty -> DEFERRABLE RULE: PRESERVE BUDGET
        // We do NOT set remainingExecutionTime to 0.
        // We simply return false. The Scheduler will see we didn't run, 
        // and ideally should pick the *next* periodic job for this tick.
        
        // Note: In a simple loop, this might require the Scheduler 
        // to be smart enough to "skip" the Server if it yields.
        return false; 
    }
}