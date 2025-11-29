cmake_minimum_required(VERSION 3.10)
project(real_time_scheduling)

# 1. Set the C++ Standard (C++17 is good for modern features)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 2. Include the header directories
include_directories(include)

# 3. Gather all source files
# This grabs main.cpp and everything inside src/utils, src/core, etc.
file(GLOB_RECURSE SOURCES "src/*.cpp")

# 4. Create the executable
add_executable(rt_scheduler ${SOURCES})