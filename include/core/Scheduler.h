#pragma once
#include <vector>
#include <string>
#include "Task.h"
#include "Job.h"
#include "../algorithms/ISchedulingAlgorithm.h"

struct TimelineEvent {
    int time;
    int jobId;
    int taskId;
    std::string type;
};

class Scheduler {
private:
    std::vector<Task> periodicTasks;   // Renamed from tasks
    std::vector<Task> aperiodicTasks;  // New
    
    std::vector<Job*> readyQueue;      // For Periodic + Server Jobs
    std::vector<Job*> aperiodicQueue;  // For Aperiodic Jobs

    ISchedulingAlgorithm* algorithm;
    int hyperperiod;
    std::string serverPolicy;

    Task* serverTaskDefinition; // Helper to create Server Jobs

    int gcd(int a, int b);
    int lcm(int a, int b);
    int calculateHyperperiod();

public:
    // Constructor signature changed
    Scheduler(const std::vector<Task>& pTasks, const std::vector<Task>& aTasks, 
              ISchedulingAlgorithm* algo, std::string policy);
    ~Scheduler();

    void run();
    void exportToFile(const std::string& filename);
    std::vector<TimelineEvent> history;
};