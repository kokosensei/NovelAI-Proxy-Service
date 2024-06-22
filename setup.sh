#!/bin/bash

# Function to display usage instructions
usage() {
    echo "Usage: $0 [-n ENV_NAME] [-s]"
    echo "  -n ENV_NAME  Specify a custom name for the virtual environment folder (default: env)"
    echo "  -s           Skip the installation of dependencies from requirements.txt"
}

# Parse command-line arguments
ENV_NAME="env"
SKIP_DEPENDENCIES=false

while getopts ":n:sh" opt; do
    case $opt in
        n) ENV_NAME=$OPTARG ;;
        s) SKIP_DEPENDENCIES=true ;;
        h) usage; exit 0 ;;
        \?) echo "Invalid option: -$OPTARG" >&2; usage; exit 1 ;;
    esac
done

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the virtual environment folder already exists
if [ -d "$ENV_NAME" ]; then
    echo "The '$ENV_NAME' folder already exists. Exiting script."
    exit 1
fi

# Create a new virtual environment
python3 -m venv "$ENV_NAME"

# Activate the virtual environment
source "$ENV_NAME/bin/activate"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "pip is not available in the virtual environment. Please check your installation."
    deactivate
    exit 1
fi

# Install dependencies from requirements.txt if not skipped
if [ "$SKIP_DEPENDENCIES" = false ]; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "Warning: requirements.txt not found. Skipping dependency installation."
    fi
fi

echo "Python environment setup completed successfully."

# Deactivate the virtual environment
deactivate