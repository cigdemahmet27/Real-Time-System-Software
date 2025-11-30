#include "../../include/utils/FileReader.h"
#include <fstream>
#include <sstream>
#include <iostream>

FileReader::ParseResult FileReader::readInputFile(const std::string& filename) {
    ParseResult result;
    
    // Default Policy: If no tags are found, we assume Background
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
        
        // --- THE GLOBAL POLICY LOGIC ---
        // We check EVERY Aperiodic line for a policy tag.
        // Since we process the file top-to-bottom, the LAST tag found 
        // will overwrite any previous ones.
        if (type == TaskType::Aperiodic) {
            ss.clear();
            std::string remaining;
            std::getline(ss, remaining); // Read text after numbers like "(Poller)"
            
            if (remaining.find("Poller") != std::string::npos) {
                result.serverPolicy = "Poller";
            } 
            else if (remaining.find("Deferrable") != std::string::npos) {
                result.serverPolicy = "Deferrable";
            }
            // Note: If a line has NO tag, we do NOT reset it to Background. 
            // We keep the last known policy (or the future policy if it appears later).
        }

        // Parsing r, e, p, d logic
        int r = 0, e = 0, p = 0, d = 0;
        if (numbers.size() == 2) { r = 0; e = numbers[0]; p = numbers[1]; d = numbers[1]; }
        else if (numbers.size() == 3) { r = numbers[0]; e = numbers[1]; p = numbers[2]; d = numbers[2]; }
        else if (numbers.size() >= 4) { r = numbers[0]; e = numbers[1]; p = numbers[2]; d = numbers[3]; }

        // Special case for Aperiodic format "A r e"
        if (type == TaskType::Aperiodic && numbers.size() == 2) {
            r = numbers[0]; e = numbers[1]; p = 0; d = 0;
        }

        Task newTask(taskIdCounter++, type, r, e, p, d);
        
        if (type == TaskType::Aperiodic) result.aperiodicTasks.push_back(newTask);
        else result.periodicTasks.push_back(newTask);
    }
    
    file.close();
    
    // At this point, result.serverPolicy holds the value from the LAST tag found.
    // This policy will apply to ALL tasks in result.aperiodicTasks.
    return result;
}