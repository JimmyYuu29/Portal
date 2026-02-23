#!/bin/bash
# =============================================================
# Portal Status Check Script
# =============================================================

echo "================================================"
echo "Portal System Status Check"
echo "================================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Portal Flask Service
echo "1. Portal (Flask) Service:"
if sudo systemctl is-active --quiet portal.service 2>/dev/null; then
    echo -e "   ${GREEN}✓ Running${NC}"
else
    echo -e "   ${RED}✗ Not running${NC}"
fi

# 2. Nginx
echo ""
echo "2. Nginx Service:"
if sudo systemctl is-active --quiet nginx; then
    echo -e "   ${GREEN}✓ Running${NC}"
else
    echo -e "   ${RED}✗ Not running${NC}"
fi

# 3. API
echo ""
echo "3. API Service (informept-api):"
if sudo systemctl is-active --quiet informept-api.service 2>/dev/null; then
    echo -e "   ${GREEN}✓ Running${NC}"
else
    echo -e "   ${RED}✗ Not running${NC}"
fi

# 4. Streamlit
echo ""
echo "4. Streamlit Service:"
if sudo systemctl is-active --quiet streamlit-informept.service 2>/dev/null; then
    echo -e "   ${GREEN}✓ Running${NC}"
else
    echo -e "   ${RED}✗ Not running${NC}"
fi

# 5. Ports
echo ""
echo "5. Port Status:"
for PORT_INFO in "80:HTTP/Nginx" "5000:Portal/Flask" "8000:API" "8501:Streamlit"; do
    PORT=$(echo "$PORT_INFO" | cut -d: -f1)
    NAME=$(echo "$PORT_INFO" | cut -d: -f2)
    echo "   Port ${PORT} (${NAME}):"
    if sudo ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
        echo -e "      ${GREEN}✓ Listening${NC}"
    else
        echo -e "      ${RED}✗ Not listening${NC}"
    fi
done

# 6. HTTP Tests
echo ""
echo "6. HTTP Access Tests:"

echo "   Portal Login (/):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "302" ]]; then
    echo -e "      ${GREEN}✓ Accessible (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "      ${RED}✗ HTTP ${HTTP_CODE}${NC}"
fi

echo "   Health Check (/health):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null)
if [[ "$HTTP_CODE" == "200" ]]; then
    echo -e "      ${GREEN}✓ Healthy (HTTP 200)${NC}"
else
    echo -e "      ${RED}✗ HTTP ${HTTP_CODE}${NC}"
fi

echo "   API (/api/):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/ 2>/dev/null)
if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "404" ]] || [[ "$HTTP_CODE" == "307" ]]; then
    echo -e "      ${GREEN}✓ Accessible (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "      ${YELLOW}⚠ HTTP ${HTTP_CODE}${NC}"
fi

# 7. Data Directory
echo ""
echo "7. Data Directory:"
DATA_DIR="${DATA_DIR:-/home/rootadmin/data/portal}"
if [ -d "${DATA_DIR}" ]; then
    echo -e "   ${GREEN}✓ ${DATA_DIR} exists${NC}"
    [ -f "${DATA_DIR}/users.db" ] && echo -e "   ${GREEN}✓ users.db present ($(du -h "${DATA_DIR}/users.db" | cut -f1))${NC}" || echo -e "   ${YELLOW}⚠ users.db not found${NC}"
    [ -f "${DATA_DIR}/apps_config.json" ] && echo -e "   ${GREEN}✓ apps_config.json present${NC}" || echo -e "   ${YELLOW}⚠ apps_config.json not found${NC}"
else
    echo -e "   ${RED}✗ ${DATA_DIR} not found${NC}"
fi

# 8. Disk & Memory
echo ""
echo "8. Disk Usage:"
df -h / | tail -1 | awk '{print "   Used: "$3" / "$2" ("$5")"}'

echo ""
echo "9. Memory Usage:"
free -h | grep Mem | awk '{print "   Used: "$3" / "$2}'

echo ""
echo "================================================"
echo "Logs:"
echo "  sudo journalctl -u portal.service -n 30"
echo "  sudo tail -f /var/log/nginx/portal_access.log"
echo "  sudo journalctl -u informept-api.service -n 30"
echo "================================================"
