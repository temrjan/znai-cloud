#!/bin/bash
# Fix nginx API proxy - strip /api prefix
# Run with: sudo bash /home/temrjan/znai-cloud/fix_nginx_api.sh

set -e

echo "Fixing nginx API proxy..."

# Fix the proxy_pass to strip /api/ prefix
sed -i 's|proxy_pass http://127.0.0.1:8000/api/;|proxy_pass http://127.0.0.1:8000/;|g' /etc/nginx/sites-available/znai-cloud.conf

# Test config
nginx -t

# Reload
systemctl reload nginx

echo "Done! Testing login endpoint..."
sleep 1

# Test the login endpoint
RESULT=$(curl -s -X POST https://znai.cloud/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}')

echo "Response: $RESULT"

if [[ "$RESULT" == *"Incorrect"* ]] || [[ "$RESULT" == *"token"* ]]; then
    echo "✅ API proxy fixed! Login endpoint working."
else
    echo "❌ Still issues. Response: $RESULT"
fi
