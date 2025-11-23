#!/bin/bash
# Debug znai.cloud 500 error
# Run with: sudo bash /home/temrjan/ai-avangard/debug_znai.sh

echo "=== Nginx Error Log (last 30 lines) ==="
tail -30 /var/log/nginx/error.log

echo ""
echo "=== Nginx Access Log (last 10 lines) ==="
tail -10 /var/log/nginx/access.log

echo ""
echo "=== Current znai-cloud.conf ==="
cat /etc/nginx/sites-enabled/znai-cloud.conf

echo ""
echo "=== Frontend files check ==="
ls -la /var/www/ai-avangard/

echo ""
echo "=== Index.html content ==="
cat /var/www/ai-avangard/index.html
