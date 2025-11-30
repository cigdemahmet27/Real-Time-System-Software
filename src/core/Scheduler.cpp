#include "../../include/core/Scheduler.h"
#include "../../include/servers/PollingServer.h"
#include "../../include/servers/DeferrableServer.h"
#include <iostream>
#include <fstream>
#include <algorithm>

const int SERVER_CAPACITY = 2; 
const int SERVER_PERIOD = 5;
const int SERVER_TASK_ID = 999;

Scheduler::Scheduler(const std::vector<Task>& pTasks, const std::vector<Task>& aTasks, 
                     ISchedulingAlgorithm* algo, std::string policy) 
    : periodicTasks(pTasks), aperiodicTasks(aTasks), algorithm(algo), serverPolicy(policy), 
      serverTaskDefinition(nullptr), serverAlgo(nullptr) {
    
    hyperperiod = calculateHyperperiod();

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
    for (const auto& task : periodicTasks) {
        if (task.period > 0) {
            long long gcdVal = gcd((int)h, task.period);
            h = (h / gcdVal) * task.period;
            if (h > 1000) { h = 1000; break; }
        }
    }
    int maxArrival = 0;
    for (const auto& task : aperiodicTasks) {
        int neededTime = task.releaseTime + task.computationTime + 20;
        if (neededTime > maxArrival) maxArrival = neededTime;
    }
    if (h < maxArrival) {
        long long extendedH = h;
        while (extendedH < maxArrival && extendedH < 1000) extendedH += h;
        h = extendedH;
    }
    if (h > 1000) h = 1000;
    return (int)h;
}

// Replace the run() method in src/core/Scheduler.cpp

void Scheduler::run() {
    std::cout << "Starting Simulation. Hyperperiod: " << hyperperiod << ", Policy: " << serverPolicy << std::endl;
    int jobCounter = 1;

    for (int t = 0; t < hyperperiod; t++) {
        
        // --- 1. CLEANUP EXPIRED SERVER JOBS (Start of Tick) ---
        auto it = readyQueue.begin();
        while (it != readyQueue.end()) {
            Job* j = *it;
            // If Server Job is expired (Deadline <= Current Time), kill it.
            // Note: We use < because if Deadline is 5 and Time is 5, it expires at the END of this tick.
            // But for replenishment, we want to clear it if it's strictly old.
            if (j->task->id == SERVER_TASK_ID && j->absoluteDeadline <= t) {
                delete j;
                it = readyQueue.erase(it);
            } else {
                ++it;
            }
        }

        // --- 2. ARRIVALS ---
        // Periodic
        for (const auto& task : periodicTasks) {
            if (t >= task.releaseTime && (t - task.releaseTime) % task.period == 0) {
                Job* newJob = new Job(jobCounter++, &task, t);
                readyQueue.push_back(newJob);
            }
        }
        // Aperiodic
        for (const auto& task : aperiodicTasks) {
            if (t == task.releaseTime) {
                Job* newAJob = new Job(jobCounter++, &task, t);
                aperiodicQueue.push_back(newAJob);
                history.push_back({t, newAJob->jobId, task.id, "AperiodicArrival"});
            }
        }

        // --- 3. SCHEDULING ---
        algorithm->pickNextJob(readyQueue, t); 
        
        Job* currentJob = nullptr;

        if (!readyQueue.empty()) {
            Job* bestJob = readyQueue.front();

            if (bestJob->task->id == SERVER_TASK_ID && serverAlgo != nullptr) {
                bool hasWork = !aperiodicQueue.empty(); 
                
                if (hasWork) {
                    currentJob = bestJob;
                    serverAlgo->run(currentJob, aperiodicQueue, history, t);
                    
                    if (currentJob->remainingExecutionTime <= 0) {
                        auto it = std::find(readyQueue.begin(), readyQueue.end(), currentJob);
                        if (it != readyQueue.end()) {
                            readyQueue.erase(it);
                            delete currentJob;
                        }
                    }
                    goto end_of_tick; 
                } 
                else {
                    // Server Yields
                    if (serverPolicy == "Poller") {
                        auto it = std::find(readyQueue.begin(), readyQueue.end(), bestJob);
                        if (it != readyQueue.end()) {
                            readyQueue.erase(it);
                            delete bestJob;
                        }
                        if (!readyQueue.empty()) currentJob = readyQueue.front();
                        else currentJob = nullptr;
                    } 
                    else {
                        // Deferrable yields, pick next task
                        if (readyQueue.size() > 1) currentJob = readyQueue[1]; 
                        else currentJob = nullptr;
                    }
                }
            } else {
                currentJob = bestJob;
            }
        }

        // --- 4. EXECUTION ---
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
            // 5. Background
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

        // --- 6. DEADLINE CHECK (SELF-HEALING) ---
        // We use an iterator so we can remove problematic server jobs safely
        auto d_it = readyQueue.begin();
        while (d_it != readyQueue.end()) {
            Job* job = *d_it;

            // SAFETY: If we find an expired SERVER job here, it's a zombie. Just kill it.
            // Do NOT trigger a deadline miss.
            if (job->task->id == SERVER_TASK_ID) {
                if (t + 1 > job->absoluteDeadline) {
                    std::cout << "[Info] Removing expired Server Job " << job->jobId << " at time " << t+1 << std::endl;
                    delete job;
                    d_it = readyQueue.erase(d_it);
                    continue; // Skip to next job
                }
                ++d_it;
                continue; // It's a server, but valid. Skip checking deadline.
            }

            // REAL CHECK for normal tasks
            if (t + 1 > job->absoluteDeadline) {
                std::cerr << "\n!!! DEADLINE MISS DETECTED !!!\n";
                std::cerr << "Time: " << t + 1 << "\n";
                std::cerr << "Job ID: " << job->jobId << " (Task " << job->task->id << ")\n";
                history.push_back({t + 1, job->jobId, job->task->id, "DEADLINE_MISS"});
                exportToFile("output_ABORTED.txt");
                return;
            }
            ++d_it;
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
        if (event.type == "DEADLINE_MISS") desc = "FAILURE";
        else if (event.type.find("ServerExec") != std::string::npos) desc = "Server(" + serverPolicy + ")";
        else if (event.taskId == SERVER_TASK_ID) desc = "Server(" + serverPolicy + ")";
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
        outFile << event.time << "\t" 
                << event.jobId << "\t" 
                << event.taskId << "\t" 
                << desc << "\t" 
                << event.type << "\n";
    }
    outFile.close();
    std::cout << "Results saved to " << fullPath << std::endl;
}