#!/bin/bash
# Deploy chat history feature
# Run with: sudo bash /home/temrjan/ai-avangard/deploy_chat_history.sh

set -e

echo "=== Deploying Chat History Feature ==="
echo ""

# 1. Run database migration
echo "[1/4] Running database migration..."
sudo -u postgres psql -d ai_avangard -c "
-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL DEFAULT 'Новый чат',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_chat_sessions_id ON chat_sessions(id);
CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_chat_sessions_updated_at ON chat_sessions(updated_at);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_chat_messages_id ON chat_messages(id);
CREATE INDEX IF NOT EXISTS ix_chat_messages_session_id ON chat_messages(session_id);
"
echo "   ✓ Migration complete"

# 2. Deploy frontend
echo ""
echo "[2/4] Deploying frontend..."
cp -r /home/temrjan/ai-avangard/frontend/dist/* /var/www/ai-avangard/
chown -R www-data:www-data /var/www/ai-avangard/
echo "   ✓ Frontend deployed"

# 3. Restart backend
echo ""
echo "[3/4] Restarting backend..."
systemctl restart ai-avangard-backend
sleep 2
echo "   ✓ Backend restarted"

# 4. Verify
echo ""
echo "[4/4] Verifying..."
curl -s https://znai.cloud/health
echo ""

echo ""
echo "=== Deployment Complete ==="
echo "Test: https://znai.cloud/chat"
