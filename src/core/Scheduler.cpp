#include "../../include/core/Scheduler.h"
#include "../../include/servers/PollingServer.h"
#include "../../include/servers/DeferrableServer.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <cmath>

// --- CONFIGURATION (SCALED FOR 0.1 QUANTUM) ---
// 1 Unit = 10 Ticks. 
// Server Capacity 2.0 -> 20 ticks
// Server Period 5.0 -> 50 ticks
const int SERVER_CAPACITY = 20; 
const int SERVER_PERIOD = 50;
const int SERVER_TASK_ID = 999;
const int SAFETY_LIMIT = 10000; // Increased limit for higher tick count

Scheduler::Scheduler(const std::vector<Task>& pTasks, const std::vector<Task>& aTasks, 
                     ISchedulingAlgorithm* algo, std::string policy) 
    : periodicTasks(pTasks), aperiodicTasks(aTasks), algorithm(algo), serverPolicy(policy), 
      serverTaskDefinition(nullptr), serverAlgo(nullptr) {
    
    hyperperiod = calculateHyperperiod();

    // Initialize Server Strategy
    if (serverPolicy == "Poller") {
        serverAlgo = new PollingServer();
        serverTaskDefinition = new Task(SERVER_TASK_ID, TaskType::Periodic, 0, SERVER_CAPACITY, SERVER_PERIOD, SERVER_PERIOD);
        periodicTasks.push_back(*serverTaskDefinition);
    } 
    else if (serverPolicy == "Deferrable") {
        serverAlgo = new DeferrableServer();
        serverTaskDefinition = new Task(SERVER_TASK_ID, TaskType::Periodic, 0, SERVER_CAPACITY, SERVER_PERIOD, SERVER_PERIOD);
        periodicTasks.push_back(*serverTaskDefinition);
    }
}

Scheduler::~Scheduler() {
    for (Job* j : readyQueue) delete j;
    for (Job* j : aperiodicQueue) delete j;
    if (serverTaskDefinition) delete serverTaskDefinition;
    if (serverAlgo) delete serverAlgo; 
}

int Scheduler::gcd(int a, int b) { 
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int Scheduler::lcm(int a, int b) { 
    if (a == 0 || b == 0) return 0;
    return (a / gcd(a, b)) * b; 
}

int Scheduler::calculateHyperperiod() {
    long long h = 1;
    
    // 1. Periodic LCM
    for (const auto& task : periodicTasks) {
        if (task.period > 0) {
            long long gcdVal = gcd((int)h, task.period);
            h = (h / gcdVal) * task.period;
            
            if (h > SAFETY_LIMIT) {
                std::cout << "Warning: Hyperperiod exceeded limit. Capping." << std::endl;
                h = SAFETY_LIMIT;
                break;
            }
        }
    }

    // 2. Aperiodic Extension
    int maxArrival = 0;
    for (const auto& task : aperiodicTasks) {
        // Buffer scaled: 20 -> 200 ticks
        int neededTime = task.releaseTime + task.computationTime + 200;
        if (neededTime > maxArrival) maxArrival = neededTime;
    }

    if (h < maxArrival) {
        long long extendedH = h;
        while (extendedH < maxArrival && extendedH < SAFETY_LIMIT) {
            extendedH += h;
        }
        h = extendedH;
    }
    
    if (h > SAFETY_LIMIT) h = SAFETY_LIMIT;

    return (int)h;
}

void Scheduler::run() {
    std::cout << "Starting Simulation. Hyperperiod (Ticks): " << hyperperiod << ", Policy: " << serverPolicy << std::endl;
    int jobCounter = 1;

    for (int t = 0; t < hyperperiod; t++) {
        
        // --- 0. REPLENISHMENT / CLEANUP ---
        // Remove old server jobs that have expired to prevent "False Deadline Misses"
        auto it = readyQueue.begin();
        while (it != readyQueue.end()) {
            Job* j = *it;
            if (j->task->id == SERVER_TASK_ID && j->absoluteDeadline <= t) {
                delete j;
                it = readyQueue.erase(it);
            } else {
                ++it;
            }
        }

        // --- 1. PERIODIC ARRIVALS ---
        for (const auto& task : periodicTasks) {
            if (t >= task.releaseTime && (t - task.releaseTime) % task.period == 0) {
                Job* newJob = new Job(jobCounter++, &task, t);
                readyQueue.push_back(newJob);
            }
        }

        // --- 2. APERIODIC ARRIVALS ---
        for (const auto& task : aperiodicTasks) {
            if (t == task.releaseTime) {
                Job* newAJob = new Job(jobCounter++, &task, t);
                aperiodicQueue.push_back(newAJob);
                history.push_back({t, newAJob->jobId, task.id, "AperiodicArrival"});
            }
        }

        // --- 3. SCHEDULING DECISION ---
        algorithm->pickNextJob(readyQueue, t); 
        
        Job* currentJob = nullptr;

        if (!readyQueue.empty()) {
            Job* bestJob = readyQueue.front();

            // SERVER LOGIC INTERCEPTION
            if (bestJob->task->id == SERVER_TASK_ID && serverAlgo != nullptr) {
                
                bool hasWork = !aperiodicQueue.empty(); 
                
                if (hasWork) {
                    currentJob = bestJob;
                    
                    // Delegate execution to Strategy (Poller/Deferrable)
                    serverAlgo->run(currentJob, aperiodicQueue, history, t);
                    
                    // CHECK: Did the server finish its budget just now?
                    if (currentJob->remainingExecutionTime <= 0) {
                        auto s_it = std::find(readyQueue.begin(), readyQueue.end(), currentJob);
                        if (s_it != readyQueue.end()) {
                            readyQueue.erase(s_it);
                            delete currentJob;
                        }
                    }
                    // Server executed work, skip normal execution step
                    goto end_of_tick; 
                } 
                else {
                    // SERVER YIELDS
                    if (serverPolicy == "Poller") {
                        // Poller burns budget immediately
                        auto p_it = std::find(readyQueue.begin(), readyQueue.end(), bestJob);
                        if (p_it != readyQueue.end()) {
                            readyQueue.erase(p_it);
                            delete bestJob;
                        }
                        // Pick next best job
                        if (!readyQueue.empty()) currentJob = readyQueue.front();
                        else currentJob = nullptr;
                    } 
                    else {
                        // Deferrable preserves budget but skips turn
                        // Pick 2nd best job (Task 1)
                        if (readyQueue.size() > 1) {
                            currentJob = readyQueue[1]; 
                        } else {
                            currentJob = nullptr;
                        }
                    }
                }
            } else {
                currentJob = bestJob;
            }
        }

        // --- 4. NORMAL EXECUTION ---
        if (currentJob != nullptr && currentJob->remainingExecutionTime > 0) {
            
            if (currentJob->startTime == -1) currentJob->startTime = t;
            
            history.push_back({t, currentJob->jobId, currentJob->task->id, "Running"});
            currentJob->remainingExecutionTime--;

            if (currentJob->remainingExecutionTime <= 0) {
                currentJob->finishTime = t + 1;
                history.push_back({t + 1, currentJob->jobId, currentJob->task->id, "Finish"});
                
                auto j_it = std::find(readyQueue.begin(), readyQueue.end(), currentJob);
                if (j_it != readyQueue.end()) {
                    readyQueue.erase(j_it);
                    delete currentJob;
                }
            }
        } else {
            // --- 5. BACKGROUND EXECUTION ---
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

        end_of_tick:;

        // --- 6. DEADLINE CHECK ---
        for (Job* job : readyQueue) {
            // Ignore Server tasks for deadline checks
            if (job->task->id == SERVER_TASK_ID) continue;

            if (t + 1 > job->absoluteDeadline) {
                std::cerr << "\n!!! DEADLINE MISS DETECTED !!!\n";
                std::cerr << "Time (Tick): " << t + 1 << "\n";
                std::cerr << "Job ID: " << job->jobId << " (Task " << job->task->id << ")\n";
                history.push_back({t + 1, job->jobId, job->task->id, "DEADLINE_MISS"});
                exportToFile("output_ABORTED.txt");
                return;
            }
        }
    }
}

void Scheduler::exportToFile(const std::string& filename) {
    std::string fullPath = "../../data/" + filename;   

    std::ofstream outFile(fullPath);
    if (!outFile.is_open()) {
        std::cout << "Error opening file: " << fullPath << std::endl;
        return;
    }

    outFile << "Time\tJobID\tTaskID\tDescription\tEvent\n";
    outFile << "--------------------------------------------------------\n";

    for (const auto& event : history) {
        std::string desc = "Unknown";
        
        // Identify Description
        if (event.type == "DEADLINE_MISS") {
            desc = "FAILURE";
        }
        else if (event.type.find("ServerExec") != std::string::npos || event.taskId == SERVER_TASK_ID) {
            desc = "Server(" + serverPolicy + ")";
        } 
        else {
            bool found = false;
            for (const auto& t : periodicTasks) {
                if (t.id == event.taskId) { desc = "Periodic"; found = true; break; }
            }
            if (!found) {
                for (const auto& t : aperiodicTasks) {
                    if (t.id == event.taskId) { desc = "Aperiodic"; break; }
                }
            }
        }

        // UNSCALE TIME: Convert ticks (int) back to user time (double)
        double userTime = (double)event.time / 10.0;

        outFile << userTime << "\t" 
                << event.jobId << "\t" 
                << event.taskId << "\t" 
                << desc << "\t" 
                << event.type << "\n";
    }

    outFile.close();
    std::cout << "Results saved to " << fullPath << std::endl;
}