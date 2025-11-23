#!/bin/bash
# Restart AI-Avangard Backend

cd /home/temrjan/ai-avangard

# Kill existing uvicorn processes
pkill -f "uvicorn backend.app.main" 2>/dev/null
sleep 2

# Start backend
export PYTHONPATH=/home/temrjan/ai-avangard
nohup /home/temrjan/ai-avangard/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 > /home/temrjan/ai-avangard/logs/backend.log 2>&1 &

sleep 3

# Check if running
if lsof -i :8000 | grep -q LISTEN; then
    echo "Backend started successfully on port 8000"
else
    echo "Failed to start backend. Check logs: tail -50 /home/temrjan/ai-avangard/logs/backend.log"
fi
