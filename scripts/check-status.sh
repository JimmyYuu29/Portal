#!/bin/bash
# Portal状态检查脚本

echo "================================================"
echo "Portal系统状态检查"
echo "================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查Nginx状态
echo "1. Nginx服务状态："
if sudo systemctl is-active --quiet nginx; then
    echo -e "   ${GREEN}✓ 运行中${NC}"
else
    echo -e "   ${RED}✗ 未运行${NC}"
fi

# 检查API服务状态
echo ""
echo "2. API服务状态："
if sudo systemctl is-active --quiet informept-api.service; then
    echo -e "   ${GREEN}✓ 运行中${NC}"
else
    echo -e "   ${RED}✗ 未运行${NC}"
fi

# 检查Streamlit服务状态
echo ""
echo "3. Streamlit服务状态："
if sudo systemctl is-active --quiet streamlit-informept.service; then
    echo -e "   ${GREEN}✓ 运行中${NC}"
else
    echo -e "   ${RED}✗ 未运行${NC}"
fi

# 检查端口监听
echo ""
echo "4. 端口监听状态："
echo "   端口 80 (HTTP):"
if sudo netstat -tlnp 2>/dev/null | grep -q ':80 ' || sudo ss -tlnp 2>/dev/null | grep -q ':80 '; then
    echo -e "      ${GREEN}✓ 监听中${NC}"
else
    echo -e "      ${RED}✗ 未监听${NC}"
fi

echo "   端口 8000 (API):"
if sudo netstat -tlnp 2>/dev/null | grep -q ':8000 ' || sudo ss -tlnp 2>/dev/null | grep -q ':8000 '; then
    echo -e "      ${GREEN}✓ 监听中${NC}"
else
    echo -e "      ${RED}✗ 未监听${NC}"
fi

echo "   端口 8501 (Streamlit):"
if sudo netstat -tlnp 2>/dev/null | grep -q ':8501 ' || sudo ss -tlnp 2>/dev/null | grep -q ':8501 '; then
    echo -e "      ${GREEN}✓ 监听中${NC}"
else
    echo -e "      ${RED}✗ 未监听${NC}"
fi

# 检查防火墙状态
echo ""
echo "5. 防火墙状态："
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo -e "   ${GREEN}✓ 已启用${NC}"
        echo "   允许的端口："
        sudo ufw status | grep ALLOW | grep -E '(22|80|443)' | sed 's/^/      /'
    else
        echo -e "   ${YELLOW}⚠ 未启用${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠ UFW未安装${NC}"
fi

# 测试HTTP访问
echo ""
echo "6. HTTP访问测试："
echo "   Portal主页 (/):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo -e "      ${GREEN}✓ 可访问 (HTTP 200)${NC}"
else
    echo -e "      ${RED}✗ 不可访问${NC}"
fi

echo "   健康检查 (/health):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200"; then
    echo -e "      ${GREEN}✓ 可访问 (HTTP 200)${NC}"
else
    echo -e "      ${RED}✗ 不可访问${NC}"
fi

echo "   API端点 (/api/):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/)
if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "404" ]] || [[ "$HTTP_CODE" == "307" ]]; then
    echo -e "      ${GREEN}✓ 可访问 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "      ${YELLOW}⚠ HTTP $HTTP_CODE${NC}"
fi

echo "   Streamlit端点 (/app/):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/app/)
if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "404" ]] || [[ "$HTTP_CODE" == "307" ]]; then
    echo -e "      ${GREEN}✓ 可访问 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "      ${YELLOW}⚠ HTTP $HTTP_CODE${NC}"
fi

# 磁盘空间检查
echo ""
echo "7. 磁盘空间："
df -h / | tail -1 | awk '{print "   使用: "$3" / "$2" ("$5")"}'

# 内存使用
echo ""
echo "8. 内存使用："
free -h | grep Mem | awk '{print "   使用: "$3" / "$2}'

echo ""
echo "================================================"
echo "详细日志查看命令："
echo "  sudo tail -f /var/log/nginx/portal_access.log"
echo "  sudo tail -f /var/log/nginx/portal_error.log"
echo "  sudo journalctl -u informept-api.service -n 50"
echo "  sudo journalctl -u streamlit-informept.service -n 50"
echo "================================================"
