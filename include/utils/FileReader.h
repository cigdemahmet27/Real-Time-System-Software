#pragma once
#include <vector>
#include <string>
#include "../core/Task.h"

class FileReader {
public:
    struct ParseResult {
        std::vector<Task> periodicTasks;  // Was just 'tasks'
        std::vector<Task> aperiodicTasks; // New separate list
        std::string serverPolicy;
    };

    static ParseResult readInputFile(const std::string& filename);
};