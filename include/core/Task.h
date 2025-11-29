#pragma once
#include <string>
#include <iostream>

// Enum to distinguish between Periodic, Aperiodic, Sporadic, and Servers
enum class TaskType {
    Periodic,
    Aperiodic,
    Sporadic,
    Poller,
    DeferrableServer,
    Background
};

struct Task {
    int id;                 // Unique ID
    TaskType type;          // P, A, D, or Server type
    int releaseTime;        // r_i
    int computationTime;    // e_i (WCET)
    int period;             // p_i (or min inter-arrival time)
    int relativeDeadline;   // d_i

    // Constructor
    Task(int id, TaskType type, int r, int c, int p, int d)
        : id(id), type(type), releaseTime(r), computationTime(c), 
          period(p), relativeDeadline(d) {}

    // Default constructor
    Task() : id(-1), type(TaskType::Periodic), releaseTime(0), 
             computationTime(0), period(0), relativeDeadline(0) {}
};