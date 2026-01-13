# InformePT Portal

InformePT应用统一访问入口 | Unified Access Portal for InformePT Application

---

## 概述 / Overview

Portal是InformePT应用的统一访问入口，通过Nginx反向代理将外部请求路由到内部的Streamlit版本（端口8501）和API版本（端口8000）。

Portal provides a unified access point for InformePT application, routing external requests via Nginx reverse proxy to the internal Streamlit version (port 8501) and API version (port 8000).

---

## 服务器信息 / Server Information

| 项目 | 值 |
|------|-----|
| **服务器IP** | 80.225.186.223 |
| **InformePT应用目录** | /home/ubuntu/InformePT |
| **Portal目录** | /home/ubuntu/Portal |
| **Streamlit服务** | streamlit-informept.service (端口 8501) |
| **API服务** | informept-api.service (端口 8000) |

---

## 访问地址 / Access URLs

| 服务 | URL | 说明 |
|------|-----|------|
| **Portal主页** | http://80.225.186.223/ | 统一入口页面 |
| **Streamlit版本** | http://80.225.186.223/app/ | 交互式Web应用 |
| **API版本** | http://80.225.186.223/api/ | RESTful API接口 |
| **API文档** | http://80.225.186.223/api/docs | FastAPI自动生成的文档 |
| **健康检查** | http://80.225.186.223/health | 系统状态检查 |

---

## 快速开始 / Quick Start

### 1. 连接服务器

```bash
ssh ubuntu@80.225.186.223
```

### 2. 克隆Portal仓库

```bash
cd /home/ubuntu
git clone https://github.com/JimmyYuu29/Portal.git
```

### 3. 运行自动部署（推荐）

```bash
cd /home/ubuntu/Portal/scripts
chmod +x deploy.sh
./deploy.sh
```

详细部署步骤请查看：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 目录结构 / Directory Structure

```
Portal/
├── README.md                    # 项目说明（本文件）
├── DEPLOYMENT_GUIDE.md          # 详细部署指南
├── QUICK_START.md               # 快速开始指南
├── Standard_v3.1_EN.md          # 架构标准文档
│
├── portal/                      # Portal Flask应用（可选高级功能）
│   ├── app.py                  # Flask主应用（统计功能）
│   ├── apps_config.json        # 应用配置文件
│   ├── requirements.txt        # Python依赖
│   ├── data/                   # 数据目录
│   ├── static/css/             # 样式文件
│   └── templates/              # HTML模板
│
└── scripts/                     # 管理脚本
    ├── deploy.sh               # 自动部署脚本
    ├── check-status.sh         # 状态检查脚本
    ├── restart-all.sh          # 重启服务脚本
    └── backup.sh               # 配置备份脚本
```

---

## 管理脚本 / Management Scripts

| 脚本 | 功能 | 使用方法 |
|------|------|----------|
| `deploy.sh` | 一键自动部署Portal | `./scripts/deploy.sh` |
| `check-status.sh` | 检查所有服务状态 | `./scripts/check-status.sh` |
| `restart-all.sh` | 重启所有服务 | `./scripts/restart-all.sh` |
| `backup.sh` | 备份配置文件 | `./scripts/backup.sh` |

---

## 常用命令 / Common Commands

### 检查服务状态

```bash
# 使用脚本
./scripts/check-status.sh

# 或手动检查
sudo systemctl status nginx
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service
```

### 重启服务

```bash
# 使用脚本
./scripts/restart-all.sh

# 或手动重启
sudo systemctl daemon-reload
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 查看日志

```bash
# Nginx日志
sudo tail -f /var/log/nginx/portal_access.log
sudo tail -f /var/log/nginx/portal_error.log

# 应用服务日志
sudo journalctl -u informept-api.service -f
sudo journalctl -u streamlit-informept.service -f
```

---

## 架构设计 / Architecture

```
Internet (用户访问)
        ↓
80.225.186.223:80 (Nginx反向代理)
        ├── /          → Portal主页 (静态HTML)
        ├── /app/      → 127.0.0.1:8501 (Streamlit)
        ├── /api/      → 127.0.0.1:8000 (FastAPI)
        └── /health    → 健康检查

防火墙规则 (UFW):
    ✓ 允许: 22 (SSH), 80 (HTTP), 443 (HTTPS)
    ✗ 拒绝: 8000, 8501 (阻止直接访问内部端口)
```

---

## 故障排查 / Troubleshooting

### 无法访问Portal

```bash
# 1. 检查Nginx状态
sudo systemctl status nginx
sudo nginx -t

# 2. 查看错误日志
sudo tail -50 /var/log/nginx/error.log

# 3. 重启Nginx
sudo systemctl restart nginx
```

### 应用无响应

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

### 502 Bad Gateway

```bash
# 检查后端服务是否运行
sudo netstat -tlnp | grep -E ':(8000|8501)'

# 或
sudo ss -tlnp | grep -E ':(8000|8501)'
```

---

## 更新Portal / Update Portal

```bash
cd /home/ubuntu/Portal
git pull origin main
./scripts/restart-all.sh
```

---

## 相关文档 / Related Documents

- [快速开始指南 (QUICK_START.md)](QUICK_START.md) - 5分钟快速部署
- [详细部署指南 (DEPLOYMENT_GUIDE.md)](DEPLOYMENT_GUIDE.md) - 完整的从零开始部署步骤
- [架构标准 (Standard_v3.1_EN.md)](Standard_v3.1_EN.md) - 平台架构设计标准

---

## 版本信息 / Version

- **Portal Version**: 1.0.0
- **Last Updated**: 2026-01-13
- **Author**: JimmyYuu29

---

## 许可证 / License

[MIT License](LICENSE)
