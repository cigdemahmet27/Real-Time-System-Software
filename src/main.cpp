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
        std::cout << "Error: No tasks found in " << inputPath << std::endl;
        return 1;
    }

    std::cout << "\n========================================\n";
    std::cout << "  Real-Time Scheduling Simulator\n";
    std::cout << "========================================\n\n";
    
    std::cout << "Loaded Tasks:\n";
    std::cout << "  - Periodic: " << result.periodicTasks.size() << "\n";
    std::cout << "  - Aperiodic: " << result.aperiodicTasks.size() << "\n";
    std::cout << "  - Server Policy: " << result.serverPolicy << "\n\n";

    std::cout << "Select Scheduling Algorithm:\n";
    std::cout << "  1. Rate Monotonic (RM)\n";
    std::cout << "  2. Deadline Monotonic (DM)\n";
    std::cout << "  3. Earliest Deadline First (EDF)\n";
    std::cout << "  4. Least Slack Time (LST)\n";
    std::cout << "\nEnter your choice (1-4): ";

    int choice = 1;
    std::cin >> choice;
    
    ISchedulingAlgorithm* algo = nullptr;
    
    switch (choice) {
        case 1:
            algo = new RateMonotonic();
            break;
        case 2:
            algo = new DeadlineMonotonic();
            break;
        case 3:
            algo = new EDF();
            break;
        case 4:
            algo = new LeastSlackTime();
            break;
        default:
            std::cout << "Invalid choice. Using Rate Monotonic.\n";
            algo = new RateMonotonic();
            break;
    }
    
    std::cout << "\nUsing Algorithm: " << algo->getName() << "\n";
    std::cout << "----------------------------------------\n\n";

    Scheduler scheduler(result.periodicTasks, result.aperiodicTasks, algo, result.serverPolicy);
    scheduler.run();
    
    std::string outputName = "output.txt";
    scheduler.exportToFile(outputName);

    std::cout << "\n========================================\n";
    std::cout << "  Simulation Complete!\n";
    std::cout << "========================================\n";

    delete algo;
    return 0;
}
