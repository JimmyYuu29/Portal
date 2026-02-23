#!/bin/bash
# =============================================================
# Portal Deployment Script
# Deploys Portal with Flask backend + Nginx reverse proxy
# =============================================================
set -e

echo "================================================"
echo "Portal Deployment Script - Forvis Mazars"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Server config
SERVER_IP="80.225.186.223"
REPO_DIR="/home/rootadmin/Portal"
DATA_DIR="/home/rootadmin/data/portal"
VENV_DIR="${REPO_DIR}/portal/venv"

echo -e "${YELLOW}Step 1/9: Checking permissions...${NC}"
if [[ $EUID -ne 0 ]]; then
   if ! sudo -v; then
       echo -e "${RED}Error: sudo required${NC}"
       exit 1
   fi
fi
echo -e "${GREEN}✓ Permissions OK${NC}"

echo ""
echo -e "${YELLOW}Step 2/9: Updating system packages...${NC}"
sudo apt update
echo -e "${GREEN}✓ System packages updated${NC}"

echo ""
echo -e "${YELLOW}Step 3/9: Installing dependencies...${NC}"
sudo apt install -y git nginx curl net-tools python3 python3-pip python3-venv
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 4/9: Creating data directory...${NC}"
mkdir -p "${DATA_DIR}"
echo -e "${GREEN}✓ DATA_DIR created: ${DATA_DIR}${NC}"

echo ""
echo -e "${YELLOW}Step 5/9: Setting up Python virtual environment...${NC}"
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${REPO_DIR}/portal/requirements.txt"
echo -e "${GREEN}✓ Python packages installed${NC}"

echo ""
echo -e "${YELLOW}Step 6/9: Syncing portal data...${NC}"
chmod +x "${REPO_DIR}/scripts/sync-portal-data.sh"
export DATA_DIR="${DATA_DIR}"
export REPO_DIR="${REPO_DIR}"
"${REPO_DIR}/scripts/sync-portal-data.sh"
echo -e "${GREEN}✓ Data synced${NC}"

echo ""
echo -e "${YELLOW}Step 7/9: Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/portal > /dev/null <<'NGINXEOF'
# Portal Forvis Mazars - Nginx Configuration
server {
    listen 80;
    server_name 80.225.186.223;

    # Logging
    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    # Portal Flask backend (login, dashboard, /go/<app_id>)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30;
        proxy_send_timeout 60;
        proxy_read_timeout 60;
    }

    # API version - route to port 8000
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit version - route to port 8501
    location /app/ {
        proxy_pass http://127.0.0.1:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit WebSocket
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Health check (bypass Flask for speed)
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration error${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 8/9: Installing systemd service...${NC}"
sudo cp "${REPO_DIR}/portal.service" /etc/systemd/system/portal.service
sudo systemctl daemon-reload
sudo systemctl enable portal.service
echo -e "${GREEN}✓ portal.service installed and enabled${NC}"

echo ""
echo -e "${YELLOW}Step 9/9: Starting services...${NC}"
sudo systemctl restart portal.service
sleep 2
if sudo systemctl is-active --quiet portal.service; then
    echo -e "${GREEN}✓ Portal service running${NC}"
else
    echo -e "${RED}✗ Portal service failed to start${NC}"
    echo "Check: sudo journalctl -u portal.service -n 30"
fi

sudo systemctl restart nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx running${NC}"
else
    echo -e "${RED}✗ Nginx failed${NC}"
fi

# Restart InformePT services if they exist
if sudo systemctl is-active --quiet informept-api.service 2>/dev/null; then
    sudo systemctl restart informept-api.service
    echo -e "${GREEN}✓ API service restarted${NC}"
fi
if sudo systemctl is-active --quiet streamlit-informept.service 2>/dev/null; then
    sudo systemctl restart streamlit-informept.service
    echo -e "${GREEN}✓ Streamlit service restarted${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✓ Portal deployment complete!${NC}"
echo "================================================"
echo ""
echo "Access URLs:"
echo "  • Portal:        http://${SERVER_IP}/"
echo "  • Login:         http://${SERVER_IP}/login"
echo "  • API:           http://${SERVER_IP}/api/"
echo "  • Streamlit:     http://${SERVER_IP}/app/"
echo "  • Health:        http://${SERVER_IP}/health"
echo ""
echo "Default Admin:"
echo "  • Username: Admin"
echo "  • Password: Admin123"
echo ""
echo "IMPORTANT: Change SECRET_KEY in portal.service before production!"
echo "  sudo systemctl edit portal.service"
echo "================================================"
