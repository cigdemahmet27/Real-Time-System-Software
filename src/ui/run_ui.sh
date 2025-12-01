#!/bin/bash
echo "========================================"
echo " Real-Time Scheduling System - UI"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    echo "Please install Python3 first."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check and install dependencies
echo "Checking dependencies..."
if ! python3 -c "import matplotlib" 2>/dev/null; then
    echo "Installing matplotlib..."
    pip3 install matplotlib
fi

echo
echo "Starting Real-Time Scheduling UI..."
echo

python3 "$SCRIPT_DIR/app.py"

