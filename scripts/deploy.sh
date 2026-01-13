#!/bin/bash
# Portal自动部署脚本
# 用途: 在Ubuntu服务器上一键部署Portal

set -e  # 遇到错误立即退出

echo "================================================"
echo "Portal部署脚本 - 80.225.186.223"
echo "================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_IP="80.225.186.223"
PORTAL_DIR="/home/ubuntu/Portal"
APP_DIR="/home/ubuntu/InformePT"

echo -e "${YELLOW}步骤 1/8: 检查系统环境...${NC}"
# 检查是否为root或有sudo权限
if [[ $EUID -ne 0 ]]; then
   if ! sudo -v; then
       echo -e "${RED}错误: 需要sudo权限${NC}"
       exit 1
   fi
fi
echo -e "${GREEN}✓ 权限检查通过${NC}"

echo ""
echo -e "${YELLOW}步骤 2/8: 更新系统包...${NC}"
sudo apt update
echo -e "${GREEN}✓ 系统包已更新${NC}"

echo ""
echo -e "${YELLOW}步骤 3/8: 安装必要依赖...${NC}"
sudo apt install -y git nginx curl net-tools
echo -e "${GREEN}✓ 依赖已安装${NC}"

echo ""
echo -e "${YELLOW}步骤 4/8: 创建Portal目录结构...${NC}"
mkdir -p $PORTAL_DIR/static
mkdir -p $PORTAL_DIR/backups
mkdir -p $PORTAL_DIR/logs
echo -e "${GREEN}✓ 目录结构已创建${NC}"

echo ""
echo -e "${YELLOW}步骤 5/8: 创建Portal主页...${NC}"
cat > $PORTAL_DIR/static/index.html <<'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InformePT Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 60px;
            max-width: 800px;
            width: 100%;
        }

        h1 {
            color: #333;
            margin-bottom: 15px;
            font-size: 2.5em;
            text-align: center;
        }

        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 50px;
            font-size: 1.1em;
        }

        .apps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }

        .app-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 30px;
            text-decoration: none;
            color: white;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .app-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }

        .app-card h2 {
            margin-bottom: 15px;
            font-size: 1.8em;
        }

        .app-card p {
            font-size: 1em;
            line-height: 1.6;
            opacity: 0.9;
        }

        .badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 15px;
        }

        .status {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 InformePT Portal</h1>
        <p class="subtitle">选择您需要的应用版本</p>

        <div class="apps">
            <a href="/app/" class="app-card">
                <h2>📊 Streamlit版本</h2>
                <p>交互式Web应用，提供可视化界面和实时数据分析功能。适合数据探索和演示。</p>
                <span class="badge">端口: 8501</span>
            </a>

            <a href="/api/docs" class="app-card">
                <h2>⚡ API版本</h2>
                <p>RESTful API接口，提供高性能的程序化访问。适合系统集成和自动化调用。</p>
                <span class="badge">端口: 8000</span>
            </a>
        </div>

        <div class="status">
            <span class="status-indicator"></span>
            <strong>系统状态:</strong> 所有服务运行正常
        </div>
    </div>
</body>
</html>
HTMLEOF

chmod 644 $PORTAL_DIR/static/index.html
echo -e "${GREEN}✓ Portal主页已创建${NC}"

echo ""
echo -e "${YELLOW}步骤 6/8: 配置Nginx反向代理...${NC}"
sudo tee /etc/nginx/sites-available/portal > /dev/null <<'NGINXEOF'
# Portal统一入口配置
server {
    listen 80;
    server_name 80.225.186.223;

    # 日志配置
    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    # Portal主页
    location / {
        root /home/ubuntu/Portal/static;
        index index.html index.htm;
        try_files $uri $uri/ =404;
    }

    # API版本 - 路由到8000端口
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

        # 超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit版本 - 路由到8501端口
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

        # Streamlit WebSocket支持
        proxy_buffering off;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # WebSocket支持（Streamlit需要）
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # 健康检查端点
    location /health {
        access_log off;
        return 200 "Portal OK\n";
        add_header Content-Type text/plain;
    }
}
NGINXEOF

# 启用站点配置
sudo ln -sf /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx配置有效${NC}"
else
    echo -e "${RED}✗ Nginx配置错误${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}步骤 7/8: 配置防火墙...${NC}"
# 检查UFW是否安装
if ! command -v ufw &> /dev/null; then
    sudo apt install -y ufw
fi

# 配置防火墙规则
sudo ufw --force enable
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw deny 8000/tcp comment 'Block direct API access'
sudo ufw deny 8501/tcp comment 'Block direct Streamlit access'
sudo ufw reload

echo -e "${GREEN}✓ 防火墙已配置${NC}"

echo ""
echo -e "${YELLOW}步骤 8/8: 启动服务...${NC}"
# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# 检查应用服务
if sudo systemctl is-active --quiet informept-api.service; then
    sudo systemctl restart informept-api.service
    echo -e "${GREEN}✓ API服务已重启${NC}"
else
    echo -e "${YELLOW}⚠ API服务未运行，请手动启动${NC}"
fi

if sudo systemctl is-active --quiet streamlit-informept.service; then
    sudo systemctl restart streamlit-informept.service
    echo -e "${GREEN}✓ Streamlit服务已重启${NC}"
else
    echo -e "${YELLOW}⚠ Streamlit服务未运行，请手动启动${NC}"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✓ Portal部署完成!${NC}"
echo "================================================"
echo ""
echo "访问地址："
echo "  • Portal主页: http://$SERVER_IP/"
echo "  • API版本: http://$SERVER_IP/api/"
echo "  • Streamlit版本: http://$SERVER_IP/app/"
echo "  • 健康检查: http://$SERVER_IP/health"
echo ""
echo "服务状态检查："
echo "  sudo systemctl status nginx"
echo "  sudo systemctl status informept-api.service"
echo "  sudo systemctl status streamlit-informept.service"
echo ""
echo "日志查看："
echo "  sudo tail -f /var/log/nginx/portal_access.log"
echo "  sudo journalctl -u informept-api.service -f"
echo "  sudo journalctl -u streamlit-informept.service -f"
echo ""
echo "================================================"
