@echo off
echo ========================================
echo  Real-Time Scheduling System - Build
echo ========================================
echo.

REM Check if g++ is available
g++ --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] g++ not found! Please install MinGW or add g++ to PATH.
    pause
    exit /b 1
)

echo [INFO] g++ found. Starting build...
echo.

REM Create build directory if not exists
if not exist "build" mkdir build

REM Compile all source files
echo [1/5] Compiling FileReader.cpp...
g++ -c -std=c++17 -I include src/utils/FileReader.cpp -o build/FileReader.o
if errorlevel 1 goto :error

echo [2/5] Compiling Scheduler.cpp...
g++ -c -std=c++17 -I include src/core/Scheduler.cpp -o build/Scheduler.o
if errorlevel 1 goto :error

echo [3/5] Compiling PollingServer.cpp...
g++ -c -std=c++17 -I include src/servers/PollingServer.cpp -o build/PollingServer.o
if errorlevel 1 goto :error

echo [4/5] Compiling DeferrableServer.cpp...
g++ -c -std=c++17 -I include src/servers/DeferrableServer.cpp -o build/DeferrableServer.o
if errorlevel 1 goto :error

echo [5/5] Compiling main.cpp and linking...
g++ -std=c++17 -I include src/main.cpp build/FileReader.o build/Scheduler.o build/PollingServer.o build/DeferrableServer.o -o build/rt_scheduler.exe
if errorlevel 1 goto :error

echo.
echo ========================================
echo  BUILD SUCCESSFUL!
echo ========================================
echo.
echo Executable: build\rt_scheduler.exe
echo.
echo To run: cd build ^&^& rt_scheduler.exe
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo  BUILD FAILED!
echo ========================================
pause
exit /b 1

