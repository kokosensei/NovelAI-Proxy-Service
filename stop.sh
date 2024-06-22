#!/bin/bash

# Set the name of your Python script
script_name="run.py"

# Find the process ID (PID) of the running script
pid=$(ps aux | grep "$script_name" | grep -v grep | awk '{print $2}')

# Check if the script is running
if [ -z "$pid" ]; then
    echo "The script '$script_name' is not running."
else
    # Terminate the script
    kill "$pid"
    echo "The script '$script_name' with PID $pid has been terminated."
fi


