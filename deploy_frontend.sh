#!/bin/bash
# Frontend deploy script
# Run with: sudo bash /home/temrjan/ai-avangard/deploy_frontend.sh

set -e

echo "=== Frontend Deploy ==="

# Backup current version
echo "1. Creating backup..."
if [ -d /var/www/ai-avangard ]; then
    cp -r /var/www/ai-avangard /var/www/ai-avangard_backup_$(date +%Y%m%d_%H%M%S)
fi

# Remove old files
echo "2. Removing old files..."
rm -rf /var/www/ai-avangard/*

# Copy new build
echo "3. Copying new build..."
cp -r /home/temrjan/ai-avangard/frontend/dist/* /var/www/ai-avangard/

# Set permissions
echo "4. Setting permissions..."
chown -R www-data:www-data /var/www/ai-avangard
chmod -R 755 /var/www/ai-avangard

# Reload nginx
echo "5. Reloading nginx..."
nginx -t && systemctl reload nginx

echo "=== Deploy complete! ==="
echo "Check: https://your-domain.com"
