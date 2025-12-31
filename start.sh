#!/bin/bash
# WebReg Monitor - Easy Startup Script

echo "================================================"
echo "🎓 WEBREG MONITOR - STARTING UP"
echo "================================================"
echo ""

# Kill any existing instances
echo "🧹 Cleaning up old processes..."
pkill -f "api.py"
pkill -f "monitor_web.py"
pkill -f "http.server 8000"
sleep 2

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: backend directory not found at $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Start API in background
echo "🚀 Starting API server (port 5001)..."
cd "$BACKEND_DIR"
nohup python3 api.py > ../logs/api.log 2>&1 &
API_PID=$!
echo "   ✅ API running (PID: $API_PID)"
sleep 2

# Start Frontend in background
echo "🚀 Starting frontend server (port 8000)..."
cd "$FRONTEND_DIR"
nohup python3 -m http.server 8000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Frontend running (PID: $FRONTEND_PID)"
sleep 2

# Open browser to the frontend
echo "🌐 Opening browser to http://localhost:8000/index.html"
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:8000/index.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:8000/index.html"
fi

echo ""
echo "================================================"
echo "✅ SERVERS STARTED!"
echo "================================================"
echo "📊 Web Interface: http://localhost:8000/index.html"
echo "🔧 API Endpoint: http://localhost:5001/api"
echo ""
echo "📝 Logs are in: $SCRIPT_DIR/logs/"
echo "   - API: logs/api.log"
echo "   - Frontend: logs/frontend.log"
echo ""
echo "================================================"
echo "🤖 STARTING MONITOR"
echo "================================================"
echo ""
echo "ℹ️  The monitor will:"
echo "   1. Open Chrome browser"
echo "   2. Ask you to log into WebReg"
echo "   3. Start checking courses every hour"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Login ONCE when the browser opens"
echo "   - Minimize the browser (don't close it!)"
echo "   - Leave your Mac on (or use 'caffeinate')"
echo ""
echo "Press Enter when you're ready to start the monitor..."
read

# Start monitor in foreground (needs to stay open for browser)
echo "🤖 Starting monitor..."
cd "$BACKEND_DIR"
caffeinate -s python3 monitor_web.py

# This only runs when monitor is stopped (Ctrl+C)
echo ""
echo "================================================"
echo "🛑 SHUTTING DOWN"
echo "================================================"
kill $API_PID $FRONTEND_PID 2>/dev/null
echo "✅ All services stopped"