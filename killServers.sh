#!/bin/bash

# Default ports used by Uvicorn (8000) and standard React/npm apps (3000)
# Change these numbers if your servers run on different ports
UVICORN_PORT=8000
NPM_PORT=3000

echo "Searching for stuck servers..."

echo "killing uvicorn"
pkill -9 -f uvicorn

# 2. Kill Node/npm by Port
NPM_PID=$(lsof -t -i:$NPM_PORT)
if [ -not -z "$NPM_PID" ]; then
    echo "Found npm/Node process on port $NPM_PORT (PID: $NPM_PID). Killing it..."
    kill -9 $NPM_PID
else
    # Fallback: Search for any loose Node processes if port check misses them
    echo "No npm server found on port $NPM_PORT. Checking generic Node processes..."
    NODE_PIDS=$(pgrep -f node)
    if [ -not -z "$NODE_PIDS" ]; then
        echo "Found background Node processes (PIDs: $NODE_PIDS). Killing them..."
        echo "$NODE_PIDS" | xargs kill -9
    else
        echo "No background Node processes found."
    fi
fi

echo "Cleanup complete!"
