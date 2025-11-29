#include "../../include/core/Scheduler.h"
#include <iostream>
#include <fstream>
#include <algorithm>

const int SERVER_CAPACITY = 2; 
const int SERVER_PERIOD = 5;
const int SERVER_TASK_ID = 999;

Scheduler::Scheduler(const std::vector<Task>& pTasks, const std::vector<Task>& aTasks, 
                     ISchedulingAlgorithm* algo, std::string policy) 
    : periodicTasks(pTasks), aperiodicTasks(aTasks), algorithm(algo), serverPolicy(policy), serverTaskDefinition(nullptr) {
    
    hyperperiod = calculateHyperperiod();

    // IF Poller, create the fake task
    if (serverPolicy == "Poller" || serverPolicy == "Deferrable") {
        serverTaskDefinition = new Task(SERVER_TASK_ID, TaskType::Periodic, 0, SERVER_CAPACITY, SERVER_PERIOD, SERVER_PERIOD);
        periodicTasks.push_back(*serverTaskDefinition);
    }
}

Scheduler::~Scheduler() {
    for (Job* j : readyQueue) delete j;
    for (Job* j : aperiodicQueue) delete j;
    if (serverTaskDefinition) delete serverTaskDefinition;
}

int Scheduler::gcd(int a, int b) { return (b == 0) ? a : gcd(b, a % b); }
int Scheduler::lcm(int a, int b) { return (a == 0 || b == 0) ? 0 : (a * b) / gcd(a, b); }

int Scheduler::calculateHyperperiod() {
    int h = 1;
    for (const auto& task : periodicTasks) {
        if (task.period > 0) h = lcm(h, task.period);
    }
    return (h > 1000) ? 1000 : h;
}

void Scheduler::run() {
    std::cout << "Starting Simulation. Hyperperiod: " << hyperperiod << ", Policy: " << serverPolicy << std::endl;
    int jobCounter = 1;

    for (int t = 0; t < hyperperiod; t++) {
        
        // 1. Periodic Arrivals
        for (const auto& task : periodicTasks) {
            if (t >= task.releaseTime && (t - task.releaseTime) % task.period == 0) {
                Job* newJob = new Job(jobCounter++, &task, t);
                readyQueue.push_back(newJob);
            }
        }

        // 2. Aperiodic Arrivals (Separate Queue)
        for (const auto& task : aperiodicTasks) {
            if (t == task.releaseTime) {
                Job* newAJob = new Job(jobCounter++, &task, t);
                aperiodicQueue.push_back(newAJob);
                history.push_back({t, newAJob->jobId, task.id, "AperiodicArrival"});
            }
        }

        // 3. Pick Job
        Job* currentJob = algorithm->pickNextJob(readyQueue, t);

        // 4. Server Logic
        bool executedAperiodic = false;
        
        if (currentJob != nullptr && currentJob->task->id == SERVER_TASK_ID) {
            if (serverPolicy == "Poller") {
                if (!aperiodicQueue.empty()) {
                    // Has Budget AND Work -> Run Aperiodic Job
                    Job* aJob = aperiodicQueue.front();
                    history.push_back({t, aJob->jobId, aJob->task->id, "ServerExec"});
                    
                    aJob->remainingExecutionTime--;
                    currentJob->remainingExecutionTime--; // Burn budget

                    if (aJob->remainingExecutionTime <= 0) {
                        delete aJob;
                        aperiodicQueue.erase(aperiodicQueue.begin());
                    }
                    executedAperiodic = true;
                } else {
                    // Poller Rule: No work -> Lose budget immediately
                    currentJob->remainingExecutionTime = 0;
                    currentJob = nullptr; // Yield
                }
            }
        }

        // 5. Normal Execution
        if (!executedAperiodic) {
            if (currentJob != nullptr && currentJob->remainingExecutionTime > 0) {
                if (currentJob->startTime == -1) currentJob->startTime = t;
                
                history.push_back({t, currentJob->jobId, currentJob->task->id, "Running"});
                currentJob->remainingExecutionTime--;

                if (currentJob->remainingExecutionTime <= 0) {
                    currentJob->finishTime = t + 1;
                    history.push_back({t + 1, currentJob->jobId, currentJob->task->id, "Finish"});
                    
                    auto it = std::find(readyQueue.begin(), readyQueue.end(), currentJob);
                    if (it != readyQueue.end()) {
                        readyQueue.erase(it);
                        delete currentJob;
                    }
                }
            } else {
                // 6. Background Execution (Only if Idle)
                if (readyQueue.empty() && !aperiodicQueue.empty()) {
                    Job* aJob = aperiodicQueue.front();
                    history.push_back({t, aJob->jobId, aJob->task->id, "BackgroundRun"});
                    aJob->remainingExecutionTime--;
                    
                    if (aJob->remainingExecutionTime <= 0) {
                        delete aJob;
                        aperiodicQueue.erase(aperiodicQueue.begin());
                    }
                } else {
                    history.push_back({t, -1, -1, "Idle"});
                }
            }
        }
    }
}

void Scheduler::exportToFile(const std::string& filename) {
    std::ofstream outFile(filename);
    if (!outFile.is_open()) return;
    outFile << "Time | JobID | TaskID | Event\n";
    for (const auto& event : history) {
        outFile << event.time << " " << event.jobId << " " << event.taskId << " " << event.type << "\n";
    }
    outFile.close();
    std::cout << "Results saved to " << filename << std::endl;
}