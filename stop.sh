#!/bin/bash
# WebReg Monitor - Stop All Services

echo "🛑 Stopping WebReg Monitor..."

# Kill all processes
pkill -f "api.py"
pkill -f "monitor_web.py"
pkill -f "http.server 8000"

# Also kill any Chrome instances opened by the bot
pkill -f "ChromeDriver"

echo "✅ All services stopped"