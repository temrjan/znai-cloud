#!/bin/bash
echo "=== Backend Status ==="
systemctl status ai-avangard-backend --no-pager

echo ""
echo "=== Last 30 lines of journal ==="
journalctl -u ai-avangard-backend -n 30 --no-pager
