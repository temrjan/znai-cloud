#!/bin/bash
# Set x.temrjan@gmail.com as platform owner
# Run with: sudo -u postgres psql ai_avangard -f /home/temrjan/ai-avangard/set_platform_owner.sql
# Or: psql -h localhost -U ai_avangard_user -d ai_avangard

cat << 'EOF'
Run this SQL command in PostgreSQL:

UPDATE users
SET is_platform_admin = true, role = 'admin'
WHERE email = 'x.temrjan@gmail.com';

To verify:
SELECT id, email, role, is_platform_admin FROM users WHERE email = 'x.temrjan@gmail.com';
EOF

echo ""
echo "Executing SQL..."
PGPASSWORD=$(grep POSTGRES_PASSWORD /home/temrjan/ai-avangard/.env | cut -d'=' -f2) \
psql -h localhost -U ai_avangard_user -d ai_avangard -c \
"UPDATE users SET is_platform_admin = true, role = 'admin' WHERE email = 'x.temrjan@gmail.com';"

echo ""
echo "Verifying..."
PGPASSWORD=$(grep POSTGRES_PASSWORD /home/temrjan/ai-avangard/.env | cut -d'=' -f2) \
psql -h localhost -U ai_avangard_user -d ai_avangard -c \
"SELECT id, email, role, is_platform_admin FROM users WHERE email = 'x.temrjan@gmail.com';"
