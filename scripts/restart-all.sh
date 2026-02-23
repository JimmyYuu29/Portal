#!/bin/bash
# =============================================================
# Restart All Portal Services
# =============================================================
set -e

echo "================================================"
echo "Restarting Portal Services"
echo "================================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_DIR="${REPO_DIR:-/home/rootadmin/Portal}"
DATA_DIR="${DATA_DIR:-/home/rootadmin/data/portal}"

# Step 0: Sync data before restart
echo -e "${YELLOW}0. Syncing portal data...${NC}"
if [ -x "${REPO_DIR}/scripts/sync-portal-data.sh" ]; then
    export DATA_DIR="${DATA_DIR}"
    export REPO_DIR="${REPO_DIR}"
    "${REPO_DIR}/scripts/sync-portal-data.sh"
    echo -e "${GREEN}✓ Data synced${NC}"
else
    echo -e "${YELLOW}⚠ sync-portal-data.sh not found, skipping${NC}"
fi

echo ""
echo -e "${YELLOW}1. Restarting Portal (Flask)...${NC}"
sudo systemctl restart portal.service
sleep 2
if sudo systemctl is-active --quiet portal.service; then
    echo -e "${GREEN}✓ Portal service running${NC}"
else
    echo -e "${RED}✗ Portal service failed${NC}"
fi

echo ""
echo -e "${YELLOW}2. Restarting Nginx...${NC}"
sudo systemctl restart nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx running${NC}"
else
    echo -e "${RED}✗ Nginx failed${NC}"
fi

echo ""
echo -e "${YELLOW}3. Restarting API service...${NC}"
if systemctl list-unit-files | grep -q informept-api.service; then
    sudo systemctl restart informept-api.service
    sleep 2
    if sudo systemctl is-active --quiet informept-api.service; then
        echo -e "${GREEN}✓ API service running${NC}"
    else
        echo -e "${RED}✗ API service failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ informept-api.service not found${NC}"
fi

echo ""
echo -e "${YELLOW}4. Restarting Streamlit service...${NC}"
if systemctl list-unit-files | grep -q streamlit-informept.service; then
    sudo systemctl restart streamlit-informept.service
    sleep 2
    if sudo systemctl is-active --quiet streamlit-informept.service; then
        echo -e "${GREEN}✓ Streamlit service running${NC}"
    else
        echo -e "${RED}✗ Streamlit service failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ streamlit-informept.service not found${NC}"
fi

echo ""
echo "================================================"
echo "All services restarted."
echo ""
echo "Check status: ./scripts/check-status.sh"
echo "================================================"
