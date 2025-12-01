#include "../../include/utils/FileReader.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <cmath> // for round

// --- CONFIG ---
const int SCALE_FACTOR = 10; // 1 unit = 10 ticks (0.1 resolution)

FileReader::ParseResult FileReader::readInputFile(const std::string& filename) {
    ParseResult result;
    result.serverPolicy = "Background"; 
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return result;
    }

    std::string line;
    int taskIdCounter = 1;

    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;

        std::stringstream ss(line);
        char typeChar;
        ss >> typeChar;

        // D is also Periodic, just with explicit deadline
        TaskType type = TaskType::Periodic;
        bool hasExplicitDeadline = false;
        
        if (typeChar == 'P') {
            type = TaskType::Periodic;
            hasExplicitDeadline = false;
        }
        else if (typeChar == 'D') {
            type = TaskType::Periodic;  // D is also periodic!
            hasExplicitDeadline = true;
        }
        else if (typeChar == 'A') {
            type = TaskType::Aperiodic;
        }
        else continue;

        std::vector<double> rawNumbers;
        double num;
        while (ss >> num) rawNumbers.push_back(num);
        
        // Check Policy Tags for Aperiodic tasks
        if (type == TaskType::Aperiodic) {
            ss.clear();
            std::string remaining;
            std::getline(ss, remaining);
            if (remaining.find("Poller") != std::string::npos) result.serverPolicy = "Poller";
            else if (remaining.find("Deferrable") != std::string::npos) result.serverPolicy = "Deferrable";
        }

        // Default vars
        double r_d = 0, e_d = 0, p_d = 0, d_d = 0;

        // --- MAPPING LOGIC ---
        
        if (rawNumbers.size() == 2) {
            // P e p  or  A r e
            if (type == TaskType::Aperiodic) {
                // A r e -> Aperiodic: release, exec
                r_d = rawNumbers[0]; 
                e_d = rawNumbers[1]; 
                p_d = 0; 
                d_d = 0;
            } else {
                // P e p -> Periodic: exec, period (r=0, d=p)
                r_d = 0; 
                e_d = rawNumbers[0]; 
                p_d = rawNumbers[1]; 
                d_d = rawNumbers[1]; // deadline = period
            }
        } 
        else if (rawNumbers.size() == 3) {
            if (hasExplicitDeadline) {
                // D e p d -> Periodic with deadline: exec, period, deadline (r=0)
                r_d = 0;
                e_d = rawNumbers[0];
                p_d = rawNumbers[1];
                d_d = rawNumbers[2]; // explicit deadline
            } else {
                // P r e p -> Periodic: release, exec, period (d=p)
                r_d = rawNumbers[0];
                e_d = rawNumbers[1];
                p_d = rawNumbers[2];
                d_d = rawNumbers[2]; // deadline = period
            }
        } 
        else if (rawNumbers.size() >= 4) {
            // P r e p d or D r e p d -> release, exec, period, deadline
            r_d = rawNumbers[0]; 
            e_d = rawNumbers[1]; 
            p_d = rawNumbers[2]; 
            d_d = rawNumbers[3];
        }

        // SCALE AND CAST TO INT
        int r = (int)std::round(r_d * SCALE_FACTOR);
        int e = (int)std::round(e_d * SCALE_FACTOR);
        int p = (int)std::round(p_d * SCALE_FACTOR);
        int d = (int)std::round(d_d * SCALE_FACTOR);

        Task newTask(taskIdCounter++, type, r, e, p, d);
        
        if (type == TaskType::Aperiodic) result.aperiodicTasks.push_back(newTask);
        else result.periodicTasks.push_back(newTask);
    }
    file.close();
    return result;
}
