#!/bin/bash
# RAG Pipeline Diagnostics
# Run with: sudo bash /home/temrjan/znai-cloud/diagnose_rag.sh

echo "=== RAG Pipeline Diagnostics ==="
echo ""

# 1. Check services
echo "[1] Services Status:"
echo "  PostgreSQL: $(systemctl is-active postgresql)"
echo "  Redis: $(systemctl is-active redis-server 2>/dev/null || systemctl is-active redis)"
echo "  Backend: $(systemctl is-active znai-cloud-backend)"
curl -s http://localhost:8000/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Qdrant: {d.get(\"qdrant\")}')" 2>/dev/null || echo "  Qdrant: unknown"
echo ""

# 2. Check OpenAI API
echo "[2] OpenAI API Key check:"
OPENAI_KEY=$(grep OPENAI_API_KEY /home/temrjan/znai-cloud/.env | cut -d'=' -f2)
if [[ $OPENAI_KEY == sk-* ]]; then
    echo "  Key format: Valid (starts with sk-)"
else
    echo "  Key format: INVALID"
fi
echo ""

# 3. Check uploads directory
echo "[3] Uploads directory:"
ls -la /home/temrjan/znai-cloud/uploads/ 2>/dev/null | head -5
echo ""

# 4. Check backend logs
echo "[4] Backend logs (last 20 lines):"
journalctl -u znai-cloud-backend -n 20 --no-pager 2>/dev/null || echo "  No access to logs"
echo ""

# 5. Restart suggestion
echo "[5] To restart backend with debug:"
echo "    sudo systemctl stop znai-cloud-backend"
echo "    cd /home/temrjan/znai-cloud"
echo "    PYTHONPATH=. ./venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
