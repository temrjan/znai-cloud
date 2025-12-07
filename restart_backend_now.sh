#!/bin/bash
cd /home/temrjan/znai-cloud
pkill -f 'uvicorn backend.app.main' 2>/dev/null
sleep 1
nohup /home/temrjan/znai-cloud/venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 2 --log-level info > logs/backend.log 2>&1 &
sleep 3
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo '✅ Backend restarted successfully!'
else
    echo '❌ Backend failed to start. Check logs/backend.log'
fi
