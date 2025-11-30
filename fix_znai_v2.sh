#!/bin/bash
# Fix znai.cloud - comprehensive fix
# Run with: sudo bash /home/temrjan/znai-cloud/fix_znai_v2.sh

set -e

echo "=== Debug Info ==="
echo ""
echo "Nginx error log (last 20 lines):"
tail -20 /var/log/nginx/error.log
echo ""

echo "=== Fixing Config ==="

# Disable old config to avoid conflicts
if [ -f /etc/nginx/sites-enabled/znai-cloud.conf ]; then
    echo "Disabling old znai-cloud.conf to avoid port conflicts..."
    rm -f /etc/nginx/sites-enabled/znai-cloud.conf
fi

# Rewrite znai-cloud.conf completely
echo "Creating clean znai-cloud.conf..."

cat > /etc/nginx/sites-available/znai-cloud.conf << 'NGINX_EOF'
# znai.cloud - AI Avangard Platform

# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name znai.cloud www.znai.cloud;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name znai.cloud www.znai.cloud;

    # SSL managed by Certbot
    ssl_certificate /etc/letsencrypt/live/znai.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/znai.cloud/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Frontend
    root /var/www/znai-cloud;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Redirect old domain to new
server {
    listen 80;
    listen [::]:80;
    server_name temrjan.com www.temrjan.com;
    return 301 https://znai.cloud$request_uri;
}
NGINX_EOF

# Ensure symlink exists
ln -sf /etc/nginx/sites-available/znai-cloud.conf /etc/nginx/sites-enabled/znai-cloud.conf

echo "Testing nginx config..."
nginx -t

echo "Reloading nginx..."
systemctl reload nginx

echo ""
echo "=== Testing ==="
sleep 1
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://znai.cloud)
echo "HTTPS Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ znai.cloud is working!"
else
    echo "❌ Still having issues. Check: sudo tail -50 /var/log/nginx/error.log"
fi
