#!/bin/bash
echo "=== Backend Status ==="
systemctl status znai-cloud-backend --no-pager

echo ""
echo "=== Last 30 lines of journal ==="
journalctl -u znai-cloud-backend -n 30 --no-pager
