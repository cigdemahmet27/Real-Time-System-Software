#include "../../include/utils/FileReader.h"
#include <fstream>
#include <sstream>
#include <iostream>

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

        TaskType type = TaskType::Periodic;
        if (typeChar == 'P') type = TaskType::Periodic;
        else if (typeChar == 'D') type = TaskType::Sporadic;
        else if (typeChar == 'A') type = TaskType::Aperiodic;
        else continue;

        std::vector<int> numbers;
        int num;
        while (ss >> num) numbers.push_back(num);
        
        // Check for Server Strategy text
        if (type == TaskType::Aperiodic) {
            ss.clear();
            std::string remaining;
            std::getline(ss, remaining);
            if (remaining.find("Poller") != std::string::npos) result.serverPolicy = "Poller";
            else if (remaining.find("Deferrable") != std::string::npos) result.serverPolicy = "Deferrable";
        }

        int r = 0, e = 0, p = 0, d = 0;
        // Parsing logic remains same as before...
        if (numbers.size() == 2) { r = 0; e = numbers[0]; p = numbers[1]; d = numbers[1]; }
        else if (numbers.size() == 3) { r = numbers[0]; e = numbers[1]; p = numbers[2]; d = numbers[2]; }
        else if (numbers.size() >= 4) { r = numbers[0]; e = numbers[1]; p = numbers[2]; d = numbers[3]; }

        if (type == TaskType::Aperiodic && numbers.size() == 2) {
            r = numbers[0]; e = numbers[1]; p = 0; d = 0;
        }

        Task newTask(taskIdCounter++, type, r, e, p, d);
        
        // SPLIT LOGIC HERE
        if (type == TaskType::Aperiodic) result.aperiodicTasks.push_back(newTask);
        else result.periodicTasks.push_back(newTask);
    }
    file.close();
    return result;
}