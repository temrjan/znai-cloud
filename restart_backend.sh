#!/bin/bash
# Restart AI-Avangard Backend

echo "Stopping existing backend..."
pkill -f "uvicorn backend.app.main:app" || true
sleep 2

echo "Starting backend..."
cd /home/temrjan/znai-cloud
source venv/bin/activate
nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
sleep 3

echo "Checking status..."
curl -s http://localhost:8000/health || echo "Health check failed"

echo ""
echo "Backend logs (last 20 lines):"
tail -20 logs/backend.log
