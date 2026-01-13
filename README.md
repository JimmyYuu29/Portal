# Consulting Tools Portal

咨询事务所内部自动化工具统一入口 | Internal Automation Tools Portal

基于 Standard v3.1 Enhanced 规范构建

---

## 目录 / Table of Contents

1. [项目简介 / Overview](#项目简介--overview)
2. [功能特性 / Features](#功能特性--features)
3. [快速开始 / Quick Start](#快速开始--quick-start)
4. [项目结构 / Project Structure](#项目结构--project-structure)
5. [如何添加新APP / How to Add a New APP](#如何添加新app--how-to-add-a-new-app)
6. [配置说明 / Configuration](#配置说明--configuration)
7. [API接口 / API Endpoints](#api接口--api-endpoints)
8. [部署指南 / Deployment Guide](#部署指南--deployment-guide)
9. [Nginx配置示例 / Nginx Configuration](#nginx配置示例--nginx-configuration)

---

## 项目简介 / Overview

Portal是咨询事务所内部自动化工具的统一入口平台，提供：
- 单一入口点访问所有内部工具（税务/审计/ESG等）
- 访问统计与分析功能
- 可扩展的架构支持50+应用
- 符合Standard v3.1规范

Portal is the unified entry point for internal automation tools, providing:
- Single entry point for all internal tools (Tax/Audit/ESG)
- Access statistics and analytics
- Scalable architecture supporting 50+ applications
- Compliant with Standard v3.1 specification

---

## 功能特性 / Features

### 核心功能
- **统一入口**: 所有APP通过Portal访问，隐藏内部端口
- **访问统计**: 自动记录PV（页面访问量）、UV（独立访客数）
- **APP使用追踪**: 记录每个APP的访问次数和最后访问时间
- **分类管理**: APP按类别组织（税务/审计/ESG/数据分析/管理工具）
- **热门排行**: 展示最受欢迎的工具
- **健康检查**: 提供 `/health` 端点用于监控

### 技术特点
- 轻量级Flask应用
- SQLite本地存储统计数据
- JSON配置文件管理APP
- 响应式设计，支持移动端
- RESTful API接口

---

## 快速开始 / Quick Start

### 1. 安装依赖

```bash
cd portal
pip install -r requirements.txt
```

### 2. 启动应用

**开发模式:**
```bash
python app.py
```

**生产模式 (使用Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. 访问Portal

打开浏览器访问: `http://localhost:5000`

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `PORTAL_HOST` | `0.0.0.0` | 监听地址 |
| `PORTAL_PORT` | `5000` | 监听端口 |
| `PORTAL_DEBUG` | `false` | 调试模式 |
| `PORTAL_SECRET_KEY` | `dev-secret-key...` | 应用密钥（生产环境必须修改） |

---

## 项目结构 / Project Structure

```
Portal/
├── README.md                    # 本说明文件
├── Standard_v3.1_EN.md         # 架构规范文档
└── portal/                      # Portal应用目录
    ├── app.py                   # 主应用文件
    ├── apps_config.json         # APP配置文件 ⭐
    ├── requirements.txt         # Python依赖
    ├── data/                    # 数据存储目录
    │   └── portal.db           # SQLite数据库（自动创建）
    ├── static/                  # 静态资源
    │   └── css/
    │       └── style.css       # 样式文件
    └── templates/               # HTML模板
        ├── index.html          # 首页模板
        └── error.html          # 错误页面模板
```

---

## 如何添加新APP / How to Add a New APP

### 方法：编辑 `apps_config.json`

添加新APP只需要编辑 `portal/apps_config.json` 文件，在 `apps` 数组中添加新条目。

### 步骤1: 打开配置文件

```bash
vim portal/apps_config.json
# 或使用任何文本编辑器
```

### 步骤2: 添加新APP条目

在 `apps` 数组中添加新的APP对象：

```json
{
  "apps": [
    // ... 现有APP ...

    {
      "id": "your-app-id",
      "name": "应用名称",
      "name_en": "App Name (English)",
      "description": "应用描述，简要说明功能",
      "category": "tax",
      "url": "/apps/your-app",
      "icon": "file-text",
      "enabled": true,
      "version": "1.0.0",
      "maintainer": "Your Team",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### APP配置字段说明

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `id` | 是 | string | APP唯一标识符，用于URL和统计，建议使用小写字母和连字符 |
| `name` | 是 | string | APP中文名称 |
| `name_en` | 否 | string | APP英文名称 |
| `description` | 是 | string | APP描述，显示在卡片上 |
| `category` | 是 | string | 分类ID，见下方分类列表 |
| `url` | 是 | string | APP的URL地址（可以是相对路径或完整URL） |
| `icon` | 否 | string | 图标名称，使用[Lucide Icons](https://lucide.dev/icons)，默认`box` |
| `enabled` | 否 | boolean | 是否启用，默认`true` |
| `version` | 否 | string | APP版本号 |
| `maintainer` | 否 | string | 维护团队/人员 |
| `tags` | 否 | array | 标签数组，用于展示和搜索 |

### 可用分类 (Categories)

| 分类ID | 名称 | 说明 |
|--------|------|------|
| `tax` | 税务工具 | 税务相关自动化工具 |
| `audit` | 审计工具 | 审计相关自动化工具 |
| `esg` | ESG工具 | 环境、社会和治理相关工具 |
| `data` | 数据分析 | 数据处理和分析工具 |
| `admin` | 管理工具 | 系统管理和配置工具 |
| `other` | 其他 | 不属于上述分类的工具（自动分配） |

### 步骤3: 添加新分类（可选）

如果需要新分类，在 `categories` 数组中添加：

```json
{
  "categories": [
    // ... 现有分类 ...

    {
      "id": "finance",
      "name": "财务工具 / Finance Tools",
      "icon": "dollar-sign",
      "description": "财务相关自动化工具"
    }
  ]
}
```

### 步骤4: 验证配置

重启Portal服务后，新APP将自动显示在首页。

**验证命令:**
```bash
# 检查JSON语法
python -c "import json; json.load(open('portal/apps_config.json'))"

# 重启服务
# 如果使用systemd
sudo systemctl restart portal

# 或直接重启进程
```

### 完整示例

添加一个新的"发票管理系统"APP：

```json
{
  "id": "invoice-manager",
  "name": "发票管理系统",
  "name_en": "Invoice Manager",
  "description": "增值税发票开具、查验和管理",
  "category": "tax",
  "url": "/apps/invoice-manager",
  "icon": "receipt",
  "enabled": true,
  "version": "2.1.0",
  "maintainer": "Tax Tech Team",
  "tags": ["invoice", "vat", "tax"]
}
```

---

## 配置说明 / Configuration

### apps_config.json 完整结构

```json
{
  "portal_name": "Consulting Tools Portal",
  "portal_description": "咨询事务所内部自动化工具统一入口",
  "categories": [
    {
      "id": "category-id",
      "name": "分类名称 / Category Name",
      "icon": "lucide-icon-name",
      "description": "分类描述"
    }
  ],
  "apps": [
    {
      "id": "app-id",
      "name": "APP名称",
      "name_en": "App Name",
      "description": "APP描述",
      "category": "category-id",
      "url": "/path/to/app",
      "icon": "lucide-icon-name",
      "enabled": true,
      "version": "1.0.0",
      "maintainer": "Team Name",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

---

## API接口 / API Endpoints

### 统计数据

**GET /api/stats**

获取Portal统计数据

```json
{
  "today": {
    "page_views": 150,
    "unique_visitors": 45
  },
  "total": {
    "page_views": 12580,
    "unique_visitors": 3200
  },
  "top_apps": [
    {"app_id": "tax-calculator", "total_visits": 580, "last_visit": "2026-01-13T10:30:00"}
  ],
  "weekly_trend": [
    {"date": "2026-01-07", "page_views": 120, "unique_visitors": 35}
  ]
}
```

### APP列表

**GET /api/apps**

获取所有APP配置

### 单个APP统计

**GET /api/apps/{app_id}/stats**

获取指定APP的访问统计

### 健康检查

**GET /health**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-13T10:30:00",
  "version": "1.0.0"
}
```

---

## 部署指南 / Deployment Guide

### 使用Systemd服务

创建服务文件 `/etc/systemd/system/portal.service`:

```ini
[Unit]
Description=Consulting Tools Portal
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Portal/portal
Environment="PORTAL_SECRET_KEY=your-production-secret-key"
Environment="PORTAL_PORT=5000"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable portal
sudo systemctl start portal
```

### 使用Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY portal/ .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行:
```bash
docker build -t consulting-portal .
docker run -d -p 5000:5000 -v portal-data:/app/data consulting-portal
```

---

## Nginx配置示例 / Nginx Configuration

按照Standard v3.1规范，使用Nginx作为反向代理：

```nginx
upstream portal_backend {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name tools.internal-domain.com;

    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Portal入口
    location / {
        proxy_pass http://portal_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
    }

    # APP路由 - 按需添加
    location /apps/tax-calculator/ {
        proxy_pass http://127.0.0.1:5001/;
    }

    location /apps/audit-checklist/ {
        proxy_pass http://127.0.0.1:5002/;
    }

    # 健康检查
    location /health {
        proxy_pass http://portal_backend/health;
    }
}
```

---

## 常见问题 / FAQ

### Q: 添加新APP后没有显示？

A: 请检查：
1. JSON语法是否正确
2. `enabled` 字段是否为 `true`
3. 服务是否已重启

### Q: 如何禁用某个APP？

A: 将该APP的 `enabled` 字段设置为 `false`

### Q: 统计数据存储在哪里？

A: 统计数据存储在 `portal/data/portal.db` SQLite数据库中

### Q: 如何备份数据？

A: 备份 `portal/data/portal.db` 文件和 `apps_config.json` 文件

---

## 版本信息 / Version

- Portal Version: 1.0.0
- Based on: Standard v3.1 Enhanced
- Last Updated: 2026-01-13

---

## 联系方式 / Contact

如有问题，请联系: **Platform Team** (platform@company.com)
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
