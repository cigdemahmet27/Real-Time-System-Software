#pragma once
#include <vector>
#include <string>
#include "Task.h"
#include "Job.h"
#include "../algorithms/ISchedulingAlgorithm.h"

// Forward declaration to avoid circular includes
// (We only need the pointer type here, the implementation is in the .cpp)
class IServer; 

struct TimelineEvent {
    int time;
    int jobId;
    int taskId;
    std::string type; // "Running", "Arrival", "ServerExec", etc.
};

class Scheduler {
private:
    std::vector<Task> periodicTasks;
    std::vector<Task> aperiodicTasks;
    
    std::vector<Job*> readyQueue;      // Main queue (P jobs + Server job)
    std::vector<Job*> aperiodicQueue;  // Waiting area for A jobs

    ISchedulingAlgorithm* algorithm;
    int hyperperiod;
    std::string serverPolicy;

    // --- SERVER MECHANISM ---
    Task* serverTaskDefinition; // The "Fake" periodic task (Task ID 999)
    IServer* serverAlgo;        // The Strategy (Poller or Deferrable logic)

    // Helpers
    int gcd(int a, int b);
    int lcm(int a, int b);
    int calculateHyperperiod();

public:
    Scheduler(const std::vector<Task>& pTasks, const std::vector<Task>& aTasks, 
              ISchedulingAlgorithm* algo, std::string policy);
    
    ~Scheduler();

    void run();
    void exportToFile(const std::string& filename);

    std::vector<TimelineEvent> history;
};