#!/bin/bash
# Fix znai.cloud nginx config - correct frontend path
# Run with: sudo bash /home/temrjan/znai-cloud/fix_znai_nginx.sh

set -e

echo "Fixing znai.cloud nginx config..."

# Fix the root path
sed -i 's|root /var/www/znai-cloud/frontend;|root /var/www/znai-cloud;|g' /etc/nginx/sites-available/znai-cloud.conf

# Test config
nginx -t

# Reload
systemctl reload nginx

echo "Done! Testing..."
curl -s -o /dev/null -w "HTTPS Status: %{http_code}\n" https://znai.cloud
