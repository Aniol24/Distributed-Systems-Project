#!/bin/bash

# Kill any old instances of your Python scripts
pkill -f screen_server.py
pkill -f hwa.py
pkill -f hwb.py

# clean the Terminal
clear

# Start screen server first
python screen_server.py &
PID_SCREEN=$!

# Start hwa.py in background
python hwa.py 5000 &
PID_HWA=$!

# Give it a moment to start
sleep 1

# Start hwb.py in background
python hwb.py 5000 &
PID_HWB=$!

# Cleanup function
cleanup() {
    echo "Stopping all processes..."
    kill -9 $PID_SCREEN $PID_HWA $PID_HWB 2>/dev/null
    exit 0
}

# Trap Ctrl+C and run cleanup
trap cleanup SIGINT

# Keep script alive until you press Ctrl+C
wait
# End of script