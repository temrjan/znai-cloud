#!/bin/bash
echo "=== Backend Logs (last 50 lines) ==="
journalctl -u ai-avangard-backend -n 50 --no-pager
