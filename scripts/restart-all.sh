#!/bin/bash
# 重启所有Portal相关服务

echo "================================================"
echo "重启Portal所有服务"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. 重启Nginx...${NC}"
sudo systemctl restart nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx已重启${NC}"
else
    echo -e "${RED}✗ Nginx重启失败${NC}"
fi

echo ""
echo -e "${YELLOW}2. 重启API服务...${NC}"
sudo systemctl restart informept-api.service
sleep 2
if sudo systemctl is-active --quiet informept-api.service; then
    echo -e "${GREEN}✓ API服务已重启${NC}"
else
    echo -e "${RED}✗ API服务重启失败${NC}"
fi

echo ""
echo -e "${YELLOW}3. 重启Streamlit服务...${NC}"
sudo systemctl restart streamlit-informept.service
sleep 2
if sudo systemctl is-active --quiet streamlit-informept.service; then
    echo -e "${GREEN}✓ Streamlit服务已重启${NC}"
else
    echo -e "${RED}✗ Streamlit服务重启失败${NC}"
fi

echo ""
echo "================================================"
echo "所有服务已重启完成"
echo ""
echo "运行以下命令检查状态："
echo "  ./check-status.sh"
echo "================================================"
