#!/bin/bash

echo "Starting Healthcare Management System..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Run the application
python3 app.py
