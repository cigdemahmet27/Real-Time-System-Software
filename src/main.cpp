#include <iostream>
#include <string>
#include <algorithm>
#include "../include/utils/FileReader.h"
#include "../include/core/Scheduler.h"
#include "../include/algorithms/RateMonotonic.h"
#include "../include/algorithms/DeadlineMonotonic.h"
#include "../include/algorithms/EDF.h"
#include "../include/algorithms/LeastSlackTime.h"

int main() {
    std::string inputPath = "../../data/input.txt"; 
    
    auto result = FileReader::readInputFile(inputPath);

    if (result.periodicTasks.empty() && result.aperiodicTasks.empty()) {
        std::cout << "Error: No tasks found." << std::endl;
        return 1;
    }

    // ... (Menu Selection Code same as before) ...
    int choice;
    // Assume user input code here for brevity
    std::cin >> choice; 
    ISchedulingAlgorithm* algo = new RateMonotonic(); // Simplification for brevity

    // CHANGED LINE: Pass periodicTasks AND aperiodicTasks
    Scheduler scheduler(result.periodicTasks, result.aperiodicTasks, algo, result.serverPolicy);
    scheduler.run();
    
    std::string outputName = "output.txt";
    scheduler.exportToFile(outputName);

    delete algo;
    return 0;
}