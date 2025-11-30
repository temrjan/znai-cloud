#!/bin/bash
echo "=== Backend Logs (last 50 lines) ==="
journalctl -u znai-cloud-backend -n 50 --no-pager
