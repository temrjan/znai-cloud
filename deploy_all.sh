#!/bin/bash
# Full deploy script - Frontend + Backend restart + Set platform owner
# Run with: sudo bash /home/temrjan/ai-avangard/deploy_all.sh

set -e

echo "=========================================="
echo "   AI-Avangard Full Deploy"
echo "=========================================="
echo ""

# 1. Deploy frontend
echo "[1/4] Deploying frontend..."
if [ -d /var/www/ai-avangard ]; then
    cp -r /var/www/ai-avangard /var/www/ai-avangard_backup_$(date +%Y%m%d_%H%M%S)
fi
rm -rf /var/www/ai-avangard/*
cp -r /home/temrjan/ai-avangard/frontend/dist/* /var/www/ai-avangard/
chown -R www-data:www-data /var/www/ai-avangard
chmod -R 755 /var/www/ai-avangard
echo "   ✓ Frontend deployed"

# 2. Reload nginx
echo "[2/4] Reloading nginx..."
nginx -t && systemctl reload nginx
echo "   ✓ Nginx reloaded"

# 3. Set platform owner
echo "[3/4] Setting platform owner..."
PGPASSWORD=$(grep POSTGRES_PASSWORD /home/temrjan/ai-avangard/.env | cut -d'=' -f2) \
psql -h localhost -U ai_avangard_user -d ai_avangard -c \
"UPDATE users SET is_platform_admin = true, role = 'admin' WHERE email = 'x.temrjan@gmail.com';" 2>/dev/null || echo "   Note: DB update may have failed"
echo "   ✓ Platform owner set"

# 4. Restart backend
echo "[4/4] Restarting backend..."
systemctl restart ai-avangard-backend 2>/dev/null || supervisorctl restart ai-avangard 2>/dev/null || echo "   Note: Restart backend manually if needed"
echo "   ✓ Backend restart initiated"

echo ""
echo "=========================================="
echo "   Deploy Complete!"
echo "=========================================="
echo ""
echo "Check: http://temrjan.com"
echo ""
echo "To verify platform owner, run:"
echo "psql -h localhost -U ai_avangard_user -d ai_avangard -c \"SELECT id, email, role, is_platform_admin FROM users WHERE email = 'x.temrjan@gmail.com';\""
