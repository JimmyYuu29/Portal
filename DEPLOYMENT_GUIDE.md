# InformePT Portal 完整部署指南

本文档提供从零开始在Ubuntu服务器上部署Portal的完整步骤。

---

## 目录

1. [服务器信息](#服务器信息)
2. [前提条件](#前提条件)
3. [第一步：连接服务器](#第一步连接服务器)
4. [第二步：系统准备](#第二步系统准备)
5. [第三步：克隆Portal仓库](#第三步克隆portal仓库)
6. [第四步：配置Nginx反向代理](#第四步配置nginx反向代理)
7. [第五步：创建Portal主页](#第五步创建portal主页)
8. [第六步：配置防火墙](#第六步配置防火墙)
9. [第七步：验证部署](#第七步验证部署)
10. [第八步：配置开机自启](#第八步配置开机自启)
11. [可选：SSL证书配置](#可选ssl证书配置)
12. [日志管理](#日志管理)
13. [备份策略](#备份策略)
14. [故障排查](#故障排查)
15. [维护命令速查表](#维护命令速查表)

---

## 服务器信息

| 项目 | 值 |
|------|-----|
| **服务器公网IP** | 80.225.186.223 |
| **操作系统** | Ubuntu 18.04+ |
| **InformePT应用目录** | /home/ubuntu/InformePT |
| **Portal部署目录** | /home/ubuntu/Portal |
| **Streamlit服务端口** | 8501 |
| **API服务端口** | 8000 |
| **Nginx监听端口** | 80 (HTTP), 443 (HTTPS) |

---

## 前提条件

在开始之前，请确保：

1. **InformePT应用已部署并运行**
   - 位置：/home/ubuntu/InformePT
   - API服务：informept-api.service（端口8000）
   - Streamlit服务：streamlit-informept.service（端口8501）

2. **服务已启动**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart informept-api.service
   sudo systemctl restart streamlit-informept.service
   ```

3. **有服务器SSH访问权限**

---

## 第一步：连接服务器

使用SSH连接到服务器：

```bash
ssh ubuntu@80.225.186.223
```

如果使用密钥认证：

```bash
ssh -i ~/.ssh/your_key.pem ubuntu@80.225.186.223
```

---

## 第二步：系统准备

### 2.1 更新系统包

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.2 安装必要依赖

```bash
sudo apt install -y git nginx curl net-tools ufw
```

### 2.3 验证安装

```bash
# 检查Nginx版本
nginx -v

# 检查Git版本
git --version
```

---

## 第三步：克隆Portal仓库

### 3.1 进入部署目录

```bash
cd /home/ubuntu
```

### 3.2 克隆仓库

**方式1：HTTPS（推荐，如果是公开仓库）**
```bash
git clone https://github.com/JimmyYuu29/Portal.git
```

**方式2：SSH（如果配置了SSH密钥）**
```bash
git clone git@github.com:JimmyYuu29/Portal.git
```

### 3.3 验证克隆成功

```bash
ls -la /home/ubuntu/Portal
```

应该看到以下目录结构：
```
Portal/
├── README.md
├── DEPLOYMENT_GUIDE.md
├── QUICK_START.md
├── Standard_v3.1_EN.md
├── portal/
└── scripts/
```

### 3.4 设置目录权限

```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/Portal
chmod 755 /home/ubuntu/Portal
chmod +x /home/ubuntu/Portal/scripts/*.sh
```

---

## 第四步：配置Nginx反向代理

### 4.1 创建Nginx配置文件

```bash
sudo nano /etc/nginx/sites-available/portal
```

### 4.2 添加以下配置内容

```nginx
# InformePT Portal Nginx配置
# 服务器: 80.225.186.223

server {
    listen 80;
    server_name 80.225.186.223;

    # 日志配置
    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    # Portal主页（静态文件）
    location / {
        root /home/ubuntu/Portal/static;
        index index.html index.htm;
        try_files $uri $uri/ =404;
    }

    # API版本 - 路由到端口8000
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

        # 超时设置（长请求支持）
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit版本 - 路由到端口8501
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

        # Streamlit特定配置
        proxy_buffering off;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit WebSocket支持
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Streamlit静态资源
    location /static/ {
        proxy_pass http://127.0.0.1:8501/static/;
    }

    # 健康检查端点
    location /health {
        access_log off;
        return 200 "Portal OK\n";
        add_header Content-Type text/plain;
    }
}
```

### 4.3 启用配置

```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置语法
sudo nginx -t
```

如果测试成功，会显示：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4.4 重新加载Nginx

```bash
sudo systemctl reload nginx
```

---

## 第五步：创建Portal主页

### 5.1 创建静态文件目录

```bash
mkdir -p /home/ubuntu/Portal/static
```

### 5.2 创建Portal主页

```bash
nano /home/ubuntu/Portal/static/index.html
```

添加以下内容：

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
            max-width: 900px;
            width: 100%;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }

        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 50px;
            font-size: 1.1em;
        }

        .server-info {
            background: #f0f4f8;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 40px;
            text-align: center;
            font-family: monospace;
            color: #555;
        }

        .apps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .app-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 35px;
            text-decoration: none;
            color: white;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .app-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }

        .app-card h2 {
            margin-bottom: 15px;
            font-size: 1.6em;
        }

        .app-card p {
            font-size: 1em;
            line-height: 1.7;
            opacity: 0.9;
            margin-bottom: 15px;
        }

        .badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
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
            width: 12px;
            height: 12px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.95); }
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: #999;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px;
            }
            h1 {
                font-size: 1.8em;
            }
            .apps {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>InformePT Portal</h1>
        <p class="subtitle">统一应用入口 | Unified Application Portal</p>

        <div class="server-info">
            Server: 80.225.186.223
        </div>

        <div class="apps">
            <a href="/app/" class="app-card">
                <h2>Streamlit版本</h2>
                <p>交互式Web应用，提供可视化界面和实时数据分析功能。适合数据探索、报告生成和演示。</p>
                <span class="badge">端口: 8501 | 路径: /app/</span>
            </a>

            <a href="/api/docs" class="app-card">
                <h2>API版本</h2>
                <p>RESTful API接口，提供高性能的程序化访问。适合系统集成、自动化调用和批量处理。</p>
                <span class="badge">端口: 8000 | 路径: /api/</span>
            </a>
        </div>

        <div class="status">
            <span class="status-indicator"></span>
            <strong>系统状态:</strong> 所有服务运行正常
        </div>

        <div class="footer">
            <p>InformePT Portal v1.0 | Powered by Nginx</p>
        </div>
    </div>
</body>
</html>
```

### 5.3 设置文件权限

```bash
chmod 644 /home/ubuntu/Portal/static/index.html
```

---

## 第六步：配置防火墙

### 6.1 启用UFW防火墙

```bash
# 启用UFW（如果尚未启用）
sudo ufw enable
```

### 6.2 配置防火墙规则

```bash
# 允许SSH（重要！防止被锁定）
sudo ufw allow 22/tcp comment 'SSH'

# 允许HTTP
sudo ufw allow 80/tcp comment 'HTTP'

# 允许HTTPS（可选，如果配置SSL）
sudo ufw allow 443/tcp comment 'HTTPS'

# 拒绝直接访问内部端口（安全措施）
sudo ufw deny 8000/tcp comment 'Block direct API access'
sudo ufw deny 8501/tcp comment 'Block direct Streamlit access'
```

### 6.3 重新加载防火墙

```bash
sudo ufw reload
```

### 6.4 验证防火墙规则

```bash
sudo ufw status numbered
```

应显示：
```
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere                   # SSH
[ 2] 80/tcp                     ALLOW IN    Anywhere                   # HTTP
[ 3] 443/tcp                    ALLOW IN    Anywhere                   # HTTPS
[ 4] 8000/tcp                   DENY IN     Anywhere                   # Block direct API access
[ 5] 8501/tcp                   DENY IN     Anywhere                   # Block direct Streamlit access
```

---

## 第七步：验证部署

### 7.1 检查服务状态

```bash
# 检查Nginx
sudo systemctl status nginx

# 检查InformePT服务
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service
```

### 7.2 检查端口监听

```bash
sudo netstat -tlnp | grep -E ':(80|8000|8501) '
```

或：

```bash
sudo ss -tlnp | grep -E ':(80|8000|8501) '
```

应显示：
```
tcp   LISTEN 0  511  0.0.0.0:80     0.0.0.0:*   users:(("nginx",...))
tcp   LISTEN 0  ...  127.0.0.1:8000 0.0.0.0:*   users:(("uvicorn",...))
tcp   LISTEN 0  ...  127.0.0.1:8501 0.0.0.0:*   users:(("streamlit",...))
```

### 7.3 从服务器本地测试

```bash
# 测试Portal主页
curl http://localhost/

# 测试健康检查
curl http://localhost/health

# 测试API
curl http://localhost/api/

# 测试Streamlit（会返回HTML）
curl http://localhost/app/ | head -20
```

### 7.4 从外部测试

在浏览器中访问：

| URL | 预期结果 |
|-----|----------|
| http://80.225.186.223/ | Portal主页 |
| http://80.225.186.223/app/ | Streamlit应用 |
| http://80.225.186.223/api/docs | API文档 |
| http://80.225.186.223/health | "Portal OK" |

---

## 第八步：配置开机自启

### 8.1 启用Nginx开机自启

```bash
sudo systemctl enable nginx
```

### 8.2 确认InformePT服务开机自启

```bash
sudo systemctl is-enabled informept-api.service
sudo systemctl is-enabled streamlit-informept.service
```

如果显示 `disabled`，启用它们：

```bash
sudo systemctl enable informept-api.service
sudo systemctl enable streamlit-informept.service
```

---

## 可选：SSL证书配置

### 使用Let's Encrypt（需要域名）

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书（替换为您的域名）
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 使用自签名证书（仅用于测试）

```bash
# 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/portal-selfsigned.key \
  -out /etc/ssl/certs/portal-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=80.225.186.223"
```

然后更新Nginx配置添加HTTPS支持。

---

## 日志管理

### 日志位置

| 日志类型 | 位置 |
|----------|------|
| Nginx访问日志 | /var/log/nginx/portal_access.log |
| Nginx错误日志 | /var/log/nginx/portal_error.log |
| API服务日志 | `journalctl -u informept-api.service` |
| Streamlit服务日志 | `journalctl -u streamlit-informept.service` |

### 查看实时日志

```bash
# Nginx访问日志
sudo tail -f /var/log/nginx/portal_access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/portal_error.log

# API服务日志
sudo journalctl -u informept-api.service -f

# Streamlit服务日志
sudo journalctl -u streamlit-informept.service -f
```

### 配置日志轮转

```bash
sudo nano /etc/logrotate.d/portal
```

添加：

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

## 备份策略

### 手动备份

使用提供的备份脚本：

```bash
cd /home/ubuntu/Portal/scripts
./backup.sh
```

### 自动备份

添加到crontab：

```bash
crontab -e
```

添加（每天凌晨2点备份）：

```
0 2 * * * /home/ubuntu/Portal/scripts/backup.sh
```

### 备份内容

- Nginx配置文件
- 服务配置文件
- Portal静态文件
- 应用数据（如果有）

---

## 故障排查

### 问题1：无法访问Portal

**排查步骤：**

```bash
# 1. 检查Nginx是否运行
sudo systemctl status nginx

# 2. 测试Nginx配置
sudo nginx -t

# 3. 检查端口80是否监听
sudo netstat -tlnp | grep :80

# 4. 检查防火墙
sudo ufw status

# 5. 查看Nginx错误日志
sudo tail -50 /var/log/nginx/error.log
```

**解决方案：**

```bash
# 重启Nginx
sudo systemctl restart nginx
```

### 问题2：应用无响应（502 Bad Gateway）

**排查步骤：**

```bash
# 1. 检查后端服务是否运行
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service

# 2. 检查端口是否监听
sudo netstat -tlnp | grep -E ':(8000|8501)'

# 3. 查看服务日志
sudo journalctl -u informept-api.service -n 50
sudo journalctl -u streamlit-informept.service -n 50
```

**解决方案：**

```bash
# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 问题3：端口冲突

**排查步骤：**

```bash
# 查看端口占用
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :8501
```

**解决方案：**

```bash
# 终止占用进程（谨慎使用）
sudo kill -9 <PID>

# 重启服务
sudo systemctl restart nginx
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 问题4：权限问题

**排查步骤：**

```bash
# 检查文件权限
ls -la /home/ubuntu/Portal/static/
ls -la /etc/nginx/sites-available/portal
```

**解决方案：**

```bash
# 修复权限
sudo chown -R ubuntu:ubuntu /home/ubuntu/Portal
chmod 755 /home/ubuntu/Portal
chmod 644 /home/ubuntu/Portal/static/index.html
```

---

## 维护命令速查表

### 服务管理

| 操作 | 命令 |
|------|------|
| 重启所有服务 | `./scripts/restart-all.sh` |
| 检查所有服务状态 | `./scripts/check-status.sh` |
| 重启Nginx | `sudo systemctl restart nginx` |
| 重启API服务 | `sudo systemctl restart informept-api.service` |
| 重启Streamlit服务 | `sudo systemctl restart streamlit-informept.service` |
| 重新加载Nginx配置 | `sudo nginx -t && sudo systemctl reload nginx` |

### 日志查看

| 操作 | 命令 |
|------|------|
| Nginx访问日志 | `sudo tail -f /var/log/nginx/portal_access.log` |
| Nginx错误日志 | `sudo tail -f /var/log/nginx/portal_error.log` |
| API服务日志 | `sudo journalctl -u informept-api.service -f` |
| Streamlit服务日志 | `sudo journalctl -u streamlit-informept.service -f` |

### 配置管理

| 操作 | 命令 |
|------|------|
| 编辑Nginx配置 | `sudo nano /etc/nginx/sites-available/portal` |
| 测试Nginx配置 | `sudo nginx -t` |
| 备份配置 | `./scripts/backup.sh` |
| 更新Portal | `git pull origin main && ./scripts/restart-all.sh` |

---

## 部署完成检查清单

- [ ] SSH连接到服务器成功
- [ ] 系统包已更新
- [ ] 依赖已安装（git, nginx, curl, net-tools, ufw）
- [ ] Portal仓库已克隆到 `/home/ubuntu/Portal`
- [ ] Nginx配置已创建并启用
- [ ] Portal静态页面已创建
- [ ] 防火墙规则已配置
- [ ] 所有服务正在运行
- [ ] 从外部可以访问Portal主页
- [ ] Streamlit版本可以访问
- [ ] API版本可以访问
- [ ] 健康检查端点正常
- [ ] 开机自启已配置
- [ ] 日志系统正常
- [ ] 备份策略已设置

---

## 部署完成后的访问地址

| 服务 | URL |
|------|-----|
| Portal主页 | http://80.225.186.223/ |
| Streamlit版本 | http://80.225.186.223/app/ |
| API版本 | http://80.225.186.223/api/ |
| API文档 | http://80.225.186.223/api/docs |
| 健康检查 | http://80.225.186.223/health |

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-13
**作者**: JimmyYuu29
