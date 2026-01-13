# Portal - InformePT统一访问入口

Portal为部署在Ubuntu服务器上的InformePT应用提供统一的访问入口，通过Nginx反向代理实现对API版本和Streamlit版本的路由。

## 🎯 功能特点

- **统一入口**: 单一域名/IP访问多个应用版本
- **端口隐藏**: 隐藏内部端口（8000, 8501），只暴露80端口
- **安全防护**: 防火墙规则阻止直接访问内部端口
- **负载均衡**: Nginx反向代理提供高性能路由
- **易于维护**: 提供自动化部署和管理脚本

## 📋 系统要求

- Ubuntu 18.04+ / Debian 10+
- Nginx 1.18+
- Python 3.8+ (应用需要)
- 至少1GB RAM
- 至少10GB磁盘空间

## 🚀 快速开始

### 方式1: 一键自动部署（推荐）

```bash
# 连接到服务器
ssh ubuntu@80.225.186.223

# 克隆仓库
cd /home/ubuntu
git clone https://github.com/JimmyYuu29/Portal.git

# 运行自动部署
cd Portal/scripts
chmod +x deploy.sh
./deploy.sh
```

### 方式2: 查看快速指南

```bash
cat QUICK_START.md
```

### 方式3: 详细部署步骤

```bash
cat DEPLOYMENT_GUIDE.md
```

## 🌐 访问地址

| 服务 | URL | 端口 |
|------|-----|------|
| Portal主页 | http://80.225.186.223/ | 80 |
| API版本 | http://80.225.186.223/api/ | 80→8000 |
| Streamlit版本 | http://80.225.186.223/app/ | 80→8501 |
| 健康检查 | http://80.225.186.223/health | 80 |

## 🛠️ 管理脚本

Portal提供了一套完整的管理脚本：

| 脚本 | 功能 | 用法 |
|------|------|------|
| `deploy.sh` | 自动部署Portal | `./scripts/deploy.sh` |
| `check-status.sh` | 检查所有服务状态 | `./scripts/check-status.sh` |
| `restart-all.sh` | 重启所有服务 | `./scripts/restart-all.sh` |
| `backup.sh` | 备份配置文件 | `./scripts/backup.sh` |

## 📁 目录结构

```
Portal/
├── README.md                 # 项目说明（本文件）
├── QUICK_START.md            # 快速开始指南
├── DEPLOYMENT_GUIDE.md       # 详细部署指南
├── Standard_v3.1_EN.md       # 平台架构标准
├── scripts/                  # 管理脚本
│   ├── deploy.sh            # 自动部署
│   ├── check-status.sh      # 状态检查
│   ├── restart-all.sh       # 重启服务
│   └── backup.sh            # 配置备份
├── static/                   # Portal静态资源
│   └── index.html           # Portal主页
├── backups/                  # 配置备份目录
└── logs/                     # 日志目录
```

## 🔧 常用命令

### 检查服务状态
```bash
# 使用脚本（推荐）
./scripts/check-status.sh

# 或手动检查
sudo systemctl status nginx
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service
```

### 查看日志
```bash
# Nginx日志
sudo tail -f /var/log/nginx/portal_access.log
sudo tail -f /var/log/nginx/portal_error.log

# 应用日志
sudo journalctl -u informept-api.service -f
sudo journalctl -u streamlit-informept.service -f
```

### 重启服务
```bash
# 使用脚本（推荐）
./scripts/restart-all.sh

# 或手动重启
sudo systemctl restart nginx
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

## 🔒 安全配置

Portal已配置以下安全措施：

1. **防火墙规则**
   - ✅ 允许: 端口22 (SSH), 80 (HTTP), 443 (HTTPS)
   - ❌ 拒绝: 端口8000, 8501 (直接访问)

2. **Nginx反向代理**
   - 隐藏内部端口
   - 添加安全头
   - 请求限流（可选）

3. **服务隔离**
   - 应用服务通过systemd管理
   - 独立的日志和错误处理

## 📊 架构设计

```
Internet
    ↓
80.225.186.223:80 (Nginx)
    ├── / → Portal主页 (静态HTML)
    ├── /api/ → 127.0.0.1:8000 (FastAPI应用)
    ├── /app/ → 127.0.0.1:8501 (Streamlit应用)
    └── /health → 健康检查

防火墙阻止直接访问:
    ❌ 80.225.186.223:8000
    ❌ 80.225.186.223:8501
```

## 📖 文档

- **快速开始**: [QUICK_START.md](QUICK_START.md) - 5分钟快速部署
- **详细指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 完整部署步骤
- **平台标准**: [Standard_v3.1_EN.md](Standard_v3.1_EN.md) - 架构设计标准

## 🐛 故障排查

### 问题1: 无法访问Portal
```bash
# 检查Nginx
sudo systemctl status nginx
sudo nginx -t

# 查看错误日志
sudo tail -50 /var/log/nginx/error.log

# 重启Nginx
sudo systemctl restart nginx
```

### 问题2: 应用无响应
```bash
# 检查应用服务
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service

# 查看日志
sudo journalctl -u informept-api.service -n 50

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 问题3: 502 Bad Gateway
```bash
# 检查后端服务是否运行
sudo netstat -tlnp | grep -E ':(8000|8501)'

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -50 /var/log/nginx/error.log
```

## 🔄 更新Portal

```bash
cd /home/ubuntu/Portal
git pull origin main
./scripts/restart-all.sh
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📝 版本历史

- **v1.0** (2026-01-13)
  - 初始版本
  - Nginx反向代理配置
  - 自动化部署脚本
  - Portal统一入口页面

## 📄 许可证

[MIT License](LICENSE)

## 👥 作者

- JimmyYuu29

## 🆘 支持

如遇问题，请：
1. 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. 运行 `./scripts/check-status.sh` 检查系统状态
3. 查看日志文件
4. 提交Issue到GitHub

---

**服务器信息**
- IP: 80.225.186.223
- 应用目录: /home/ubuntu/InformePT
- Portal目录: /home/ubuntu/Portal

**快速链接**
- 📚 [快速开始](QUICK_START.md)
- 📖 [详细部署指南](DEPLOYMENT_GUIDE.md)
- 🔧 [管理脚本](scripts/)

---

**部署状态**: ⚡ 快速 | 🔒 安全 | 📊 可监控

祝你使用愉快！🚀
