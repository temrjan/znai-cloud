#!/bin/bash
# Frontend deploy script
# Run with: sudo bash /home/temrjan/znai-cloud/deploy_frontend.sh

set -e

echo "=== Frontend Deploy ==="

# Backup current version
echo "1. Creating backup..."
if [ -d /var/www/znai-cloud ]; then
    cp -r /var/www/znai-cloud /var/www/znai-cloud_backup_$(date +%Y%m%d_%H%M%S)
fi

# Remove old files
echo "2. Removing old files..."
rm -rf /var/www/znai-cloud/*

# Copy new build
echo "3. Copying new build..."
cp -r /home/temrjan/znai-cloud/frontend/dist/* /var/www/znai-cloud/

# Set permissions
echo "4. Setting permissions..."
chown -R www-data:www-data /var/www/znai-cloud
chmod -R 755 /var/www/znai-cloud

# Reload nginx
echo "5. Reloading nginx..."
nginx -t && systemctl reload nginx

echo "=== Deploy complete! ==="
echo "Check: https://your-domain.com"
