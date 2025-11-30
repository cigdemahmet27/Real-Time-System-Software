cmake_minimum_required(VERSION 3.10)
project(real_time_scheduling)

# 1. Set the C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 2. Include the header directories
include_directories(include)

# 3. Create the executable with ALL source files listed explicitly
# This prevents "Unresolved External Symbol" errors
add_executable(rt_scheduler 
    src/main.cpp
    src/utils/FileReader.cpp
    src/core/Scheduler.cpp
    src/servers/PollingServer.cpp
    src/servers/DeferrableServer.cpp
    # If you later decide to move Algorithms to .cpp files, add them here:
    # src/algorithms/RateMonotonic.cpp
)

# 4. Check for Python to run the visualizer
find_package(Python3 COMPONENTS Interpreter)

if(Python3_FOUND)
    # Define a custom target "plot"
    # This runs: python3 src/ui/visualizer.py
    add_custom_target(plot
        COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/src/ui/visualizer.py"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
        COMMENT "Generating Scheduling Gantt Chart..."
    )
    message(STATUS "UI Visualizer enabled. Run 'make plot' (Linux) or build the 'plot' target (Windows) to generate the chart.")
else()
    message(WARNING "Python3 not found. The UI visualizer will not be available.")
endif()