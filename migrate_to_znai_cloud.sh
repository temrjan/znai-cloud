#!/bin/bash
# Migration script: temrjan.com -> znai.cloud
# Run with: sudo bash /home/temrjan/ai-avangard/migrate_to_znai_cloud.sh

set -e

echo "=== Migration to znai.cloud ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Backup current config
echo -e "${YELLOW}[1/5] Backing up current nginx config...${NC}"
cp /etc/nginx/sites-available/ai-avangard.conf /etc/nginx/sites-available/ai-avangard.conf.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✓ Backup created${NC}"

# Step 2: Read current config and show it
echo ""
echo -e "${YELLOW}[2/5] Current nginx config:${NC}"
cat /etc/nginx/sites-available/ai-avangard.conf
echo ""

# Step 3: Create new config for znai.cloud
echo -e "${YELLOW}[3/5] Creating new nginx config for znai.cloud...${NC}"

cat > /etc/nginx/sites-available/znai-cloud.conf << 'NGINX_CONFIG'
# znai.cloud - AI Avangard Platform
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name znai.cloud www.znai.cloud;

    # For certbot verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Main HTTPS server (will be updated by certbot)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name znai.cloud www.znai.cloud;

    # Temporary self-signed cert (certbot will replace)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # Frontend (React)
    root /var/www/ai-avangard/frontend;
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
        proxy_connect_timeout 75s;
        client_max_body_size 50M;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # WebSocket support (if needed)
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINX_CONFIG

echo -e "${GREEN}✓ Config created: /etc/nginx/sites-available/znai-cloud.conf${NC}"

# Step 4: Enable new config
echo ""
echo -e "${YELLOW}[4/5] Enabling znai.cloud config...${NC}"
ln -sf /etc/nginx/sites-available/znai-cloud.conf /etc/nginx/sites-enabled/znai-cloud.conf

# Test nginx config
nginx -t
echo -e "${GREEN}✓ Nginx config valid${NC}"

# Reload nginx
systemctl reload nginx
echo -e "${GREEN}✓ Nginx reloaded${NC}"

# Step 5: Get SSL certificate
echo ""
echo -e "${YELLOW}[5/5] Getting SSL certificate from Let's Encrypt...${NC}"
certbot --nginx -d znai.cloud -d www.znai.cloud --non-interactive --agree-tos --email x.temrjan@gmail.com --redirect

echo ""
echo -e "${GREEN}=== Migration Complete ===${NC}"
echo ""
echo "znai.cloud is now live!"
echo ""
echo "Next steps:"
echo "  1. Test: https://znai.cloud"
echo "  2. Update frontend API_URL if needed"
echo "  3. Optionally redirect temrjan.com to znai.cloud"
echo ""
