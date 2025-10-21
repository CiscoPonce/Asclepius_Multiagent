#!/bin/bash
# Asclepius Multi-Agent System - Master Control Script
# Created by: CiscoPonce
# GitHub: https://github.com/CiscoPonce/Asclepius_Multiagent

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Ports
BACKEND_PORT=9050
FRONTEND_PORT=9051

# Function to print colored messages
print_message() {
    echo -e "${1}${2}${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        print_message "$YELLOW" "🔄 Found existing processes on port $port: $pids"
        print_message "$YELLOW" "🔄 Stopping existing processes..."
        echo "$pids" | xargs kill -9 2>/dev/null
        sleep 1
        return 0
    fi
    return 1
}

# Function to start backend
start_backend() {
    print_message "$BLUE" "🔧 Starting Backend Service..."
    
    # Check if port is free
    print_message "$YELLOW" "🔄 Checking for existing processes on port $BACKEND_PORT..."
    if check_port $BACKEND_PORT; then
        print_message "$YELLOW" "⚠️  Port $BACKEND_PORT is already in use"
        return 1
    fi
    print_message "$GREEN" "✅ Port $BACKEND_PORT is free"
    
    # Start backend
    print_message "$BLUE" "📡 Starting FastAPI backend on port $BACKEND_PORT..."
    cd /home/ciscopi/multiagent
    /home/ciscopi/multiagent/agent_env/bin/python backend/main.py > /tmp/backend.log 2>&1 &
    local backend_pid=$!
    
    # Wait for backend to start
    sleep 3
    
    if check_port $BACKEND_PORT; then
        print_message "$GREEN" "✅ Backend started (PID: $backend_pid)"
        return 0
    else
        print_message "$RED" "❌ Backend failed to start"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_message "$BLUE" "💻 Starting Frontend Service..."
    
    # Check if port is free
    print_message "$YELLOW" "🔄 Checking for existing processes on port $FRONTEND_PORT..."
    if check_port $FRONTEND_PORT; then
        print_message "$YELLOW" "⚠️  Port $FRONTEND_PORT is already in use"
        return 1
    fi
    print_message "$GREEN" "✅ Port $FRONTEND_PORT is free"
    
    # Start frontend
    print_message "$BLUE" "🌐 Starting frontend on port $FRONTEND_PORT..."
    cd /home/ciscopi/multiagent
    python3 -m http.server $FRONTEND_PORT --directory frontend > /tmp/frontend.log 2>&1 &
    local frontend_pid=$!
    
    sleep 2
    
    if check_port $FRONTEND_PORT; then
        print_message "$GREEN" "✅ Frontend started (PID: $frontend_pid)"
        return 0
    else
        print_message "$RED" "❌ Frontend failed to start"
        return 1
    fi
}

# Function to stop all services
stop_services() {
    print_message "$YELLOW" "🛑 Stopping Multi-Agent System..."
    
    print_message "$YELLOW" "🔄 Stopping backend..."
    print_message "$YELLOW" "🔄 Checking for existing processes on port $BACKEND_PORT..."
    if kill_port $BACKEND_PORT; then
        print_message "$GREEN" "✅ Port $BACKEND_PORT is free"
    else
        print_message "$GREEN" "✅ Port $BACKEND_PORT is free"
    fi
    
    print_message "$YELLOW" "🔄 Stopping frontend..."
    print_message "$YELLOW" "🔄 Checking for existing processes on port $FRONTEND_PORT..."
    if kill_port $FRONTEND_PORT; then
        print_message "$GREEN" "✅ Port $FRONTEND_PORT is free"
    else
        print_message "$GREEN" "✅ Port $FRONTEND_PORT is free"
    fi
    
    print_message "$GREEN" "✅ All services stopped"
}

# Function to check status
check_status() {
    print_message "$CYAN" "📊 Multi-Agent System Status"
    print_message "$CYAN" "============================"
    
    if check_port $BACKEND_PORT; then
        local backend_pid=$(lsof -ti:$BACKEND_PORT)
        print_message "$GREEN" "Backend (Port $BACKEND_PORT):  ✅ Running (PID: $backend_pid)"
    else
        print_message "$RED" "Backend (Port $BACKEND_PORT):  ❌ Not running"
    fi
    
    if check_port $FRONTEND_PORT; then
        local frontend_pid=$(lsof -ti:$FRONTEND_PORT)
        print_message "$GREEN" "Frontend (Port $FRONTEND_PORT): ✅ Running (PID: $frontend_pid)"
    else
        print_message "$RED" "Frontend (Port $FRONTEND_PORT): ❌ Not running"
    fi
}

# Main script
print_message "$CYAN" "🚀 Asclepius Multi-Agent System"
print_message "$CYAN" "================================"

case "$1" in
    start)
        print_message "$YELLOW" "🔄 Starting Multi-Agent System..."
        start_backend
        start_frontend
        print_message "$GREEN" "🎉 Asclepius Multi-Agent System Started Successfully!"
        print_message "$BLUE" "📍 Backend API: http://localhost:$BACKEND_PORT"
        print_message "$BLUE" "📍 Frontend:    http://localhost:$FRONTEND_PORT"
        ;;
    stop)
        stop_services
        ;;
    restart)
        print_message "$YELLOW" "🔄 Restarting Multi-Agent System..."
        stop_services
        sleep 2
        start_backend
        start_frontend
        print_message "$GREEN" "🎉 Asclepius Multi-Agent System Restarted!"
        ;;
    status)
        check_status
        ;;
    *)
        print_message "$YELLOW" "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
