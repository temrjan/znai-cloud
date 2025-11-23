#!/bin/bash
# Fix znai.cloud nginx config - correct frontend path
# Run with: sudo bash /home/temrjan/ai-avangard/fix_znai_nginx.sh

set -e

echo "Fixing znai.cloud nginx config..."

# Fix the root path
sed -i 's|root /var/www/ai-avangard/frontend;|root /var/www/ai-avangard;|g' /etc/nginx/sites-available/znai-cloud.conf

# Test config
nginx -t

# Reload
systemctl reload nginx

echo "Done! Testing..."
curl -s -o /dev/null -w "HTTPS Status: %{http_code}\n" https://znai.cloud
