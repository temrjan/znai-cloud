#!/usr/bin/env bash
#
# AI-Avangard Installation Script
# Installs all system dependencies and sets up the environment
#
# Usage: sudo ./infrastructure/scripts/setup.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

PROJECT_DIR="/home/temrjan/ai-avangard"
USER="temrjan"

echo -e "${GREEN}==============================================\n"
echo "  AI-Avangard Installation Script"
echo -e "  Version: 1.0.0"
echo -e "==============================================\n${NC}"

# ============================================================
# 1. UPDATE SYSTEM
# ============================================================
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt update
apt upgrade -y

# ============================================================
# 2. INSTALL PYTHON 3.12
# ============================================================
echo -e "${YELLOW}[2/8] Installing Python 3.12...${NC}"
apt install -y python3.12 python3.12-venv python3-pip python3-dev build-essential

# ============================================================
# 3. INSTALL PostgreSQL 16
# ============================================================
echo -e "${YELLOW}[3/8] Installing PostgreSQL 16...${NC}"

# Add PostgreSQL repository
apt install -y wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

apt update
apt install -y postgresql-16 postgresql-contrib-16

# Start PostgreSQL
systemctl enable postgresql
systemctl start postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE ai_avangard;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER ai_avangard_admin WITH ENCRYPTED PASSWORD 'ai_avangard_2025';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_avangard TO ai_avangard_admin;"
sudo -u postgres psql -c "ALTER DATABASE ai_avangard OWNER TO ai_avangard_admin;"

echo -e "${GREEN}✓ PostgreSQL installed and configured${NC}"

# ============================================================
# 4. INSTALL Redis
# ============================================================
echo -e "${YELLOW}[4/8] Installing Redis...${NC}"
apt install -y redis-server

# Configure Redis
sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf

systemctl enable redis-server
systemctl start redis-server

echo -e "${GREEN}✓ Redis installed and configured${NC}"

# ============================================================
# 5. INSTALL Qdrant
# ============================================================
echo -e "${YELLOW}[5/8] Installing Qdrant...${NC}"

cd /tmp
curl -L https://github.com/qdrant/qdrant/releases/download/v1.12.1/qdrant-x86_64-unknown-linux-gnu.tar.gz -o qdrant.tar.gz
tar xzf qdrant.tar.gz
mv qdrant /usr/local/bin/
chmod +x /usr/local/bin/qdrant
rm qdrant.tar.gz

# Create Qdrant data directory
mkdir -p /var/lib/qdrant
chown -R $USER:$USER /var/lib/qdrant

# Create Qdrant systemd service
cat > /etc/systemd/system/qdrant.service << 'EOF'
[Unit]
Description=Qdrant Vector Database
After=network.target

[Service]
Type=simple
User=temrjan
WorkingDirectory=/var/lib/qdrant
ExecStart=/usr/local/bin/qdrant
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qdrant
systemctl start qdrant

echo -e "${GREEN}✓ Qdrant installed and configured${NC}"

# ============================================================
# 6. INSTALL Nginx
# ============================================================
echo -e "${YELLOW}[6/8] Installing Nginx...${NC}"
apt install -y nginx certbot python3-certbot-nginx

systemctl enable nginx
systemctl start nginx

echo -e "${GREEN}✓ Nginx installed${NC}"

# ============================================================
# 7. INSTALL Node.js (if not already installed)
# ============================================================
echo -e "${YELLOW}[7/8] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    echo "Node.js already installed: $(node --version)"
fi

echo -e "${GREEN}✓ Node.js ready${NC}"

# ============================================================
# 8. SETUP Python Virtual Environment
# ============================================================
echo -e "${YELLOW}[8/8] Setting up Python virtual environment...${NC}"

cd $PROJECT_DIR
sudo -u $USER python3.12 -m venv venv

echo -e "${GREEN}✓ Python venv created${NC}"

# ============================================================
# SUMMARY
# ============================================================
echo -e "\n${GREEN}==============================================\n"
echo "  ✓ Installation Complete!"
echo -e "==============================================\n${NC}"

echo "Installed services:"
echo "  ✓ PostgreSQL 16 (port 5432)"
echo "  ✓ Redis (port 6379)"
echo "  ✓ Qdrant (port 6333)"
echo "  ✓ Nginx (port 80/443)"
echo "  ✓ Python 3.12 + venv"
echo "  ✓ Node.js $(node --version)"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "  1. cd $PROJECT_DIR"
echo "  2. source venv/bin/activate"
echo "  3. pip install -r backend/requirements.txt"
echo "  4. cd frontend && npm install"
echo "  5. cp .env.example .env"
echo "  6. Edit .env with your API keys"

echo -e "\n${YELLOW}Check services status:${NC}"
echo "  systemctl status postgresql"
echo "  systemctl status redis-server"
echo "  systemctl status qdrant"
echo "  systemctl status nginx"

echo -e "\n${GREEN}Installation log saved to: /var/log/ai-avangard-install.log${NC}"
