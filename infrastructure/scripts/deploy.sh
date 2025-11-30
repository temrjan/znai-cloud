#!/bin/bash
# Deployment script for AI-Avangard on temrjan.com

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Deploying AI-Avangard to temrjan.com..."

# 1. Create log directory
echo "📁 Creating log directory..."
sudo mkdir -p /var/log/znai-cloud
sudo chown temrjan:temrjan /var/log/znai-cloud

# 2. Stop existing services
echo "🛑 Stopping existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process on port 8000"
lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "No process on port 5173"

# 3. Install systemd service
echo "⚙️  Installing systemd service..."
sudo cp "$PROJECT_ROOT/infrastructure/systemd/znai-cloud-backend.service" \
    /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable znai-cloud-backend
sudo systemctl restart znai-cloud-backend

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if sudo systemctl is-active --quiet znai-cloud-backend; then
    echo "✅ Backend service started successfully"
else
    echo "❌ Backend service failed to start"
    sudo systemctl status znai-cloud-backend
    exit 1
fi

# 4. Install Nginx configuration
echo "🌐 Installing Nginx configuration..."
sudo cp "$PROJECT_ROOT/infrastructure/nginx/znai-cloud.conf" \
    /etc/nginx/sites-available/znai-cloud.conf
sudo ln -sf /etc/nginx/sites-available/znai-cloud.conf \
    /etc/nginx/sites-enabled/znai-cloud.conf

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

echo "✅ Deployment completed!"
echo ""
echo "📊 Service Status:"
sudo systemctl status znai-cloud-backend --no-pager -l
echo ""
echo "🌍 Application is now available at:"
echo "   HTTP: http://temrjan.com"
echo ""
echo "🔒 To enable HTTPS, run:"
echo "   sudo certbot --nginx -d temrjan.com -d www.temrjan.com"
