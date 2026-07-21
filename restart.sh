#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
PYTHON_BIN="python3"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKEND_LOG="$LOG_DIR/backend_$TIMESTAMP.log"
FRONTEND_LOG="$LOG_DIR/frontend_$TIMESTAMP.log"

echo "Restarting Quilliam..."

kill_process() {
    pkill -f "$1" 2>/dev/null || true
}

kill_port() {
    local pid
    pid=$(lsof -ti:"$1" 2>/dev/null) || true
    if [ -n "$pid" ]; then
        echo "Killing process on port $1 (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

mkdir -p "$LOG_DIR"

echo "Cleaning up existing processes..."
kill_process "uvicorn"
kill_process "python.*main.py"
kill_process "npm.*start"
kill_process "react-scripts"
kill_port 8080
kill_port 3000

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with $PYTHON_BIN..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Installing backend dependencies..."
"$VENV_PIP" install -q --upgrade pip setuptools
"$VENV_PIP" install -q -r "$BACKEND_DIR/requirements.txt"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd "$FRONTEND_DIR" && npm install)
fi

echo "Starting Python backend (logging to $BACKEND_LOG)..."
cd "$BACKEND_DIR"
"$VENV_PYTHON" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

sleep 3

echo "Starting React frontend (logging to $FRONTEND_LOG)..."
cd "$FRONTEND_DIR"
npm start > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo "$BACKEND_PID" > "$PROJECT_DIR/backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_DIR/frontend.pid"

echo ""
echo "Quilliam restarted!"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8080"
echo "  API Docs: http://localhost:8080/docs"
echo "  Backend log:  $BACKEND_LOG"
echo "  Frontend log: $FRONTEND_LOG"
echo ""
echo "To tail logs: tail -f $LOG_DIR/*_$TIMESTAMP.log"
echo "To stop: ./stop.sh"
