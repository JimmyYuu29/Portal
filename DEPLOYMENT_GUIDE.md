# Portal部署到Ubuntu服务器完整指南

**服务器信息：**
- 公网IP: 80.225.186.223
- 现有应用位置: /home/ubuntu/InformePT
- Portal部署位置: /home/ubuntu/Portal
- 现有服务端口:
  - 8501: Streamlit版本 (streamlit-informept.service)
  - 8000: API版本 (informept-api.service)

---

## 第一部分：服务器准备和Portal仓库导入

### 1. 连接到服务器
```bash
ssh ubuntu@80.225.186.223
```

### 2. 更新系统和安装必要依赖
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git nginx python3 python3-pip python3-venv curl
```

### 3. 克隆Portal仓库到服务器
```bash
cd /home/ubuntu

# 克隆Portal仓库（使用HTTPS或SSH）
# 方式1: HTTPS（推荐，如果是公开仓库）
git clone https://github.com/JimmyYuu29/Portal.git

# 方式2: SSH（如果配置了SSH密钥）
# git clone git@github.com:JimmyYuu29/Portal.git

# 验证克隆成功
ls -la /home/ubuntu/Portal
```

### 4. 设置目录权限
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/Portal
chmod 755 /home/ubuntu/Portal
```

---

## 第二部分：配置Nginx反向代理（统一入口）

### 5. 创建Portal的Nginx配置
```bash
sudo nano /etc/nginx/sites-available/portal
```

**配置内容：**
```nginx
# Portal统一入口配置
server {
    listen 80;
    server_name 80.225.186.223;

    # 日志配置
    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    # Portal主页（如果有静态页面）
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
```

### 6. 启用Nginx配置
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

---

## 第三部分：创建Portal静态页面（可选）

### 7. 创建Portal主页
```bash
mkdir -p /home/ubuntu/Portal/static
nano /home/ubuntu/Portal/static/index.html
```

**主页内容：**
```html
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
```

### 8. 设置静态文件权限
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/Portal/static
chmod -R 755 /home/ubuntu/Portal/static
```

---

## 第四部分：配置防火墙（重要）

### 9. 配置UFW防火墙
```bash
# 检查防火墙状态
sudo ufw status

# 如果未启用，先启用
sudo ufw enable

# 允许SSH（重要！防止被锁定）
sudo ufw allow 22/tcp

# 允许HTTP
sudo ufw allow 80/tcp

# 允许HTTPS（如果需要）
sudo ufw allow 443/tcp

# 拒绝直接访问应用端口（安全性）
sudo ufw deny 8000/tcp
sudo ufw deny 8501/tcp

# 重新加载防火墙
sudo ufw reload

# 查看规则
sudo ufw status numbered
```

---

## 第五部分：SSL证书配置（可选但推荐）

### 10. 安装Certbot并配置SSL
```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 如果有域名，可以获取免费SSL证书
# sudo certbot --nginx -d your-domain.com

# 如果只有IP，可以使用自签名证书（仅用于测试）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/portal-selfsigned.key \
  -out /etc/ssl/certs/portal-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=80.225.186.223"
```

**更新Nginx配置以支持HTTPS（如果使用SSL）：**
```bash
sudo nano /etc/nginx/sites-available/portal
```

添加HTTPS服务器块：
```nginx
server {
    listen 443 ssl http2;
    server_name 80.225.186.223;

    ssl_certificate /etc/ssl/certs/portal-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/portal-selfsigned.key;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其余配置同HTTP版本
    # ... (复制上面的location配置)
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name 80.225.186.223;
    return 301 https://$server_name$request_uri;
}
```

---

## 第六部分：验证和测试

### 11. 验证服务状态
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查应用服务状态
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service

# 查看端口监听情况
sudo netstat -tlnp | grep -E ':(80|8000|8501) '

# 或使用ss命令
sudo ss -tlnp | grep -E ':(80|8000|8501) '
```

### 12. 测试访问
```bash
# 从服务器本地测试
curl http://localhost/health
curl http://localhost/api/
curl http://localhost/app/

# 从外部测试（在你的本地电脑运行）
curl http://80.225.186.223/health
curl http://80.225.186.223/api/
```

**浏览器测试：**
- Portal主页: `http://80.225.186.223/`
- API版本: `http://80.225.186.223/api/`
- Streamlit版本: `http://80.225.186.223/app/`
- 健康检查: `http://80.225.186.223/health`

---

## 第七部分：日志和监控

### 13. 配置日志管理
```bash
# 创建日志目录
sudo mkdir -p /var/log/portal

# 查看Nginx日志
sudo tail -f /var/log/nginx/portal_access.log
sudo tail -f /var/log/nginx/portal_error.log

# 查看应用日志
sudo journalctl -u informept-api.service -f
sudo journalctl -u streamlit-informept.service -f
```

### 14. 设置日志轮转
```bash
sudo nano /etc/logrotate.d/portal
```

**配置内容：**
```
/var/log/nginx/portal_*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## 第八部分：开机自启动配置

### 15. 确保所有服务开机自启
```bash
# 启用Nginx开机自启
sudo systemctl enable nginx

# 确认应用服务已启用
sudo systemctl is-enabled informept-api.service
sudo systemctl is-enabled streamlit-informept.service

# 如果未启用，执行：
sudo systemctl enable informept-api.service
sudo systemctl enable streamlit-informept.service
```

---

## 第九部分：备份和文档

### 16. 创建配置备份
```bash
# 创建备份目录
mkdir -p /home/ubuntu/Portal/backups

# 备份Nginx配置
sudo cp /etc/nginx/sites-available/portal /home/ubuntu/Portal/backups/nginx-portal-$(date +%Y%m%d).conf

# 备份服务配置
sudo cp /etc/systemd/system/informept-api.service /home/ubuntu/Portal/backups/
sudo cp /etc/systemd/system/streamlit-informept.service /home/ubuntu/Portal/backups/

# 创建部署信息文件
cat > /home/ubuntu/Portal/DEPLOYMENT_INFO.txt <<EOF
部署日期: $(date)
服务器IP: 80.225.186.223
Portal位置: /home/ubuntu/Portal
应用位置: /home/ubuntu/InformePT
Nginx配置: /etc/nginx/sites-available/portal
服务:
  - informept-api.service (端口8000)
  - streamlit-informept.service (端口8501)
访问地址:
  - Portal: http://80.225.186.223/
  - API: http://80.225.186.223/api/
  - Streamlit: http://80.225.186.223/app/
EOF
```

---

## 第十部分：故障排查

### 17. 常见问题和解决方案

#### 问题1: 无法访问Portal
```bash
# 检查Nginx是否运行
sudo systemctl status nginx

# 检查防火墙
sudo ufw status

# 检查Nginx配置
sudo nginx -t

# 查看错误日志
sudo tail -50 /var/log/nginx/error.log
```

#### 问题2: 应用服务无响应
```bash
# 重启应用服务
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service

# 查看服务日志
sudo journalctl -u informept-api.service -n 100
sudo journalctl -u streamlit-informept.service -n 100
```

#### 问题3: 端口冲突
```bash
# 查看端口占用
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :8501

# 杀死占用进程（谨慎使用）
sudo kill -9 <PID>
```

---

## 维护命令速查表

```bash
# 重启所有服务
sudo systemctl restart nginx
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service

# 查看所有服务状态
sudo systemctl status nginx informept-api.service streamlit-informept.service

# 重新加载Nginx配置（不中断服务）
sudo nginx -t && sudo systemctl reload nginx

# 查看实时日志
sudo tail -f /var/log/nginx/portal_access.log

# 更新Portal代码
cd /home/ubuntu/Portal
git pull origin main
sudo systemctl reload nginx
```

---

## 安全加固建议

1. **定期更新系统**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **配置fail2ban防止暴力破解**
```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

3. **限制SSH访问（修改SSH端口）**
```bash
sudo nano /etc/ssh/sshd_config
# 修改 Port 22 为其他端口
sudo systemctl restart sshd
```

4. **使用强密码和SSH密钥认证**

5. **定期备份数据**
```bash
# 创建自动备份脚本
/home/ubuntu/Portal/scripts/backup.sh
```

---

## 部署完成检查清单

- [ ] Portal仓库已克隆到 `/home/ubuntu/Portal`
- [ ] Nginx已安装并配置
- [ ] 防火墙规则已设置
- [ ] 静态Portal页面已创建
- [ ] 所有服务可以通过Portal访问
- [ ] 日志系统已配置
- [ ] 开机自启动已设置
- [ ] 备份已创建
- [ ] 文档已保存
- [ ] 访问测试已通过

---

**部署完成后的访问地址：**

- **Portal主页**: http://80.225.186.223/
- **API文档**: http://80.225.186.223/api/docs
- **Streamlit应用**: http://80.225.186.223/app/
- **健康检查**: http://80.225.186.223/health

**联系信息：**
如有问题，请检查日志文件或联系系统管理员。
