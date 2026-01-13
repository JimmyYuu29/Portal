# Portal快速部署指南

## 服务器信息
- **IP地址**: 80.225.186.223
- **现有应用**: /home/ubuntu/InformePT (端口8000, 8501)
- **Portal位置**: /home/ubuntu/Portal

---

## 快速部署（推荐）

### 连接服务器并运行自动部署脚本：

```bash
# 1. SSH连接到服务器
ssh ubuntu@80.225.186.223

# 2. 克隆Portal仓库
cd /home/ubuntu
git clone https://github.com/JimmyYuu29/Portal.git

# 3. 运行自动部署脚本
cd Portal/scripts
chmod +x deploy.sh
./deploy.sh
```

**就这么简单！** 脚本会自动完成所有配置。

---

## 手动部署（如果需要）

### 1. 克隆仓库
```bash
ssh ubuntu@80.225.186.223
cd /home/ubuntu
git clone https://github.com/JimmyYuu29/Portal.git
```

### 2. 安装依赖
```bash
sudo apt update
sudo apt install -y nginx
```

### 3. 配置Nginx
```bash
sudo cp /home/ubuntu/Portal/scripts/nginx-portal.conf /etc/nginx/sites-available/portal
sudo ln -s /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 配置防火墙
```bash
sudo ufw allow 80/tcp
sudo ufw deny 8000/tcp
sudo ufw deny 8501/tcp
sudo ufw reload
```

---

## 访问地址

部署完成后，通过以下地址访问：

| 服务 | URL | 说明 |
|------|-----|------|
| **Portal主页** | http://80.225.186.223/ | 统一入口 |
| **API版本** | http://80.225.186.223/api/ | FastAPI接口 |
| **Streamlit版本** | http://80.225.186.223/app/ | Web应用 |
| **健康检查** | http://80.225.186.223/health | 状态监控 |

---

## 常用管理命令

### 检查服务状态
```bash
cd /home/ubuntu/Portal/scripts
./check-status.sh
```

### 重启所有服务
```bash
cd /home/ubuntu/Portal/scripts
./restart-all.sh
```

### 备份配置
```bash
cd /home/ubuntu/Portal/scripts
./backup.sh
```

### 查看日志
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

### 手动重启服务
```bash
# 重启Nginx
sudo systemctl restart nginx

# 重启应用服务
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

---

## 故障排查

### 问题：无法访问Portal

**解决方案：**
```bash
# 1. 检查Nginx状态
sudo systemctl status nginx

# 2. 检查配置
sudo nginx -t

# 3. 查看错误日志
sudo tail -50 /var/log/nginx/error.log

# 4. 重启Nginx
sudo systemctl restart nginx
```

### 问题：应用无响应

**解决方案：**
```bash
# 1. 检查服务状态
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service

# 2. 查看服务日志
sudo journalctl -u informept-api.service -n 50
sudo journalctl -u streamlit-informept.service -n 50

# 3. 重启服务
sudo systemctl daemon-reload
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 问题：端口被占用

**解决方案：**
```bash
# 查看端口占用
sudo netstat -tlnp | grep -E ':(80|8000|8501) '

# 或使用ss命令
sudo ss -tlnp | grep -E ':(80|8000|8501) '

# 杀死占用进程（谨慎！）
sudo kill -9 <PID>
```

---

## 目录结构

```
/home/ubuntu/Portal/
├── DEPLOYMENT_GUIDE.md      # 详细部署指南
├── QUICK_START.md            # 快速开始指南（本文件）
├── Standard_v3.1_EN.md       # 平台标准文档
├── scripts/                  # 实用脚本
│   ├── deploy.sh            # 自动部署脚本
│   ├── check-status.sh      # 状态检查脚本
│   ├── restart-all.sh       # 重启所有服务
│   └── backup.sh            # 备份脚本
├── static/                   # Portal静态文件
│   └── index.html           # Portal主页
├── backups/                  # 配置备份
└── logs/                     # 日志文件
```

---

## 安全建议

1. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **使用SSH密钥认证**（禁用密码登录）

3. **配置fail2ban**防止暴力破解
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   ```

4. **定期备份**
   ```bash
   # 添加到crontab
   0 2 * * * /home/ubuntu/Portal/scripts/backup.sh
   ```

5. **监控日志**
   ```bash
   # 设置日志轮转
   sudo nano /etc/logrotate.d/portal
   ```

---

## 更新Portal

```bash
cd /home/ubuntu/Portal
git pull origin main
./scripts/restart-all.sh
```

---

## 技术支持

- 详细文档: `DEPLOYMENT_GUIDE.md`
- 平台标准: `Standard_v3.1_EN.md`
- 脚本目录: `scripts/`

---

**部署时间**: < 5分钟（使用自动脚本）
**难度**: ⭐☆☆☆☆ 简单

祝你部署顺利！🚀
