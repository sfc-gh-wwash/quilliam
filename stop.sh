#!/bin/bash

# FNOL Application Stop Script
echo "🛑 Stopping FNOL Application..."

# Function to kill processes by name
kill_process() {
    local process_name=$1
    echo "🛑 Stopping $process_name processes..."
    pkill -f "$process_name" 2>/dev/null || true
    sleep 1
}

# Function to check if a port is in use and kill the process using it
kill_port() {
    local port=$1
    echo "🔍 Checking port $port..."
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🛑 Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Navigate to project directory
cd "$(dirname "$0")"

# Stop processes using saved PIDs
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    echo "🛑 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm backend.pid
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo "🛑 Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm frontend.pid
fi

# Kill processes by name (backup method)
kill_process "uvicorn"
kill_process "python.*main.py"
kill_process "npm.*start"
kill_process "react-scripts"

# Kill processes on specific ports (final cleanup)
kill_port 8080  # Backend port
kill_port 3000  # Frontend port

echo ""
echo "✅ FNOL Application stopped successfully!"
echo "💡 To restart the application, run: ./restart.sh"
