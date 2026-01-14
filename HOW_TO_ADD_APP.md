# Portal 添加应用指南

本文档详细介绍如何向 Portal 添加新的应用程序。

---

## 目录

1. [概述](#概述)
2. [添加应用的步骤](#添加应用的步骤)
3. [配置文件详解](#配置文件详解)
4. [添加分类](#添加分类)
5. [Nginx 配置（可选）](#nginx-配置可选)
6. [完整示例](#完整示例)
7. [常见问题](#常见问题)

---

## 概述

Portal 使用 JSON 配置文件来管理应用列表。添加新应用主要涉及修改 `portal/apps_config.json` 文件。

### 架构说明

```
用户浏览器
    │
    ▼
Portal (Flask 5000端口 或 Nginx 80端口)
    │
    ├── /go/<app_id>  →  记录访问统计  →  重定向到应用URL
    │
    ▼
应用服务 (如 Streamlit:8501, FastAPI:8000, 等)
```

---

## 添加应用的步骤

### 步骤 1：编辑配置文件

打开配置文件：

```bash
nano /home/user/Portal/portal/apps_config.json
```

### 步骤 2：在 `apps` 数组中添加新应用

```json
{
  "apps": [
    // ... 现有应用 ...
    {
      "id": "your-app-id",
      "name": "应用名称",
      "name_en": "Application Name (English)",
      "description": "应用描述，将显示在卡片上",
      "category": "分类ID",
      "url": "/your-app-path/",
      "icon": "icon-name",
      "enabled": true,
      "version": "1.0.0",
      "maintainer": "维护者信息",
      "tags": ["tag1", "tag2"],
      "port": 8XXX
    }
  ]
}
```

### 步骤 3：重启 Portal 服务

```bash
# 如果使用 gunicorn
sudo systemctl restart portal

# 如果直接运行 Flask
# 重新启动 python portal/app.py
```

---

## 配置文件详解

### 应用配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 应用唯一标识符，用于URL路由（如 `/go/your-app-id`） |
| `name` | string | 是 | 应用显示名称 |
| `name_en` | string | 否 | 英文名称（可选） |
| `description` | string | 是 | 应用描述文字 |
| `category` | string | 是 | 所属分类ID，必须匹配 `categories` 中的 `id` |
| `url` | string | 是 | 跳转URL（相对路径或完整URL） |
| `icon` | string | 否 | Lucide 图标名称，默认为 `box` |
| `enabled` | boolean | 否 | 是否启用，默认为 `true` |
| `version` | string | 否 | 版本号 |
| `maintainer` | string | 否 | 维护者信息 |
| `tags` | array | 否 | 标签数组，用于显示和搜索 |
| `port` | number | 是 | 服务端口号（用于智能路由） |

### URL 配置说明

URL 可以是以下几种形式：

1. **相对路径**（推荐用于同服务器应用）:
   ```json
   "url": "/app/"
   ```
   - 通过 Nginx 访问时，直接使用相对路径
   - 直接访问 Flask Portal 时，自动转换为 `http://server_ip:port/`

2. **完整 URL**（用于外部服务）:
   ```json
   "url": "https://external-service.com/app"
   ```

3. **带端口的 URL**:
   ```json
   "url": "http://192.168.1.100:3000/"
   ```

### 可用图标

Portal 使用 [Lucide Icons](https://lucide.dev/icons/)，常用图标包括：

| 图标名称 | 用途 |
|----------|------|
| `bar-chart-2` | 数据分析、图表应用 |
| `zap` | API、高性能应用 |
| `database` | 数据库相关 |
| `file-text` | 文档处理 |
| `settings` | 设置工具 |
| `terminal` | 命令行工具 |
| `globe` | Web 应用 |
| `cpu` | 系统监控 |
| `shield` | 安全工具 |
| `code` | 开发工具 |

---

## 添加分类

如果需要新的应用分类，在 `categories` 数组中添加：

```json
{
  "categories": [
    // ... 现有分类 ...
    {
      "id": "new-category",
      "name": "新分类名称",
      "icon": "folder",
      "description": "分类描述"
    }
  ]
}
```

---

## Nginx 配置（可选）

如果新应用需要通过 Nginx 反向代理，需要添加 Nginx location 配置：

### 1. 编辑 Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/portal
```

### 2. 添加 location 块

```nginx
# 新应用路由
location /your-app-path/ {
    proxy_pass http://127.0.0.1:8XXX/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 超时设置
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
}
```

### 3. 测试并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 完整示例

### 示例：添加一个 Jupyter Notebook 应用

#### 1. 修改 apps_config.json

```json
{
  "portal_name": "Portal InformePT",
  "portal_description": "Portal de Acceso Unificado para InformePT",
  "server_ip": "80.225.186.223",
  "categories": [
    {
      "id": "informept",
      "name": "Aplicaciones InformePT",
      "icon": "layout-dashboard",
      "description": "Aplicaciones principales"
    },
    {
      "id": "analytics",
      "name": "Herramientas de Análisis",
      "icon": "bar-chart-3",
      "description": "Herramientas de análisis de datos"
    }
  ],
  "apps": [
    {
      "id": "informept-streamlit",
      "name": "InformePT Streamlit",
      "name_en": "InformePT Streamlit",
      "description": "Aplicación web interactiva con interfaz visual...",
      "category": "informept",
      "url": "/app/",
      "icon": "bar-chart-2",
      "enabled": true,
      "version": "1.0.0",
      "maintainer": "InformePT Team",
      "tags": ["streamlit", "web", "interactive"],
      "port": 8501
    },
    {
      "id": "jupyter-notebook",
      "name": "Jupyter Notebook",
      "name_en": "Jupyter Notebook",
      "description": "Entorno interactivo para análisis de datos y desarrollo de código Python.",
      "category": "analytics",
      "url": "/jupyter/",
      "icon": "code",
      "enabled": true,
      "version": "7.0.0",
      "maintainer": "Data Team",
      "tags": ["jupyter", "python", "notebook", "data-science"],
      "port": 8888
    }
  ]
}
```

#### 2. 添加 Nginx 配置（如果需要）

```nginx
# Jupyter Notebook
location /jupyter/ {
    proxy_pass http://127.0.0.1:8888/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_buffering off;
}

# Jupyter WebSocket
location /jupyter/api/kernels/ {
    proxy_pass http://127.0.0.1:8888/api/kernels/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 常见问题

### Q1: 添加应用后页面没有显示

**检查项：**
1. 确认 `enabled` 设置为 `true`
2. 确认 `category` ID 在 `categories` 中存在
3. 检查 JSON 格式是否正确（可用 `python3 -m json.tool apps_config.json` 验证）

### Q2: 点击应用显示 "Página no encontrada"

**原因：** 应用 ID 不匹配或应用被禁用

**解决方案：**
```bash
# 检查配置文件中的应用ID
grep '"id"' /home/user/Portal/portal/apps_config.json
```

### Q3: 点击后无法访问应用服务

**检查项：**
1. 确认目标服务正在运行：
   ```bash
   sudo netstat -tlnp | grep :8XXX
   ```
2. 确认 `port` 字段设置正确
3. 确认 `server_ip` 配置正确
4. 如果通过 Nginx 访问，确认 Nginx location 配置正确

### Q4: 如何禁用某个应用？

将 `enabled` 设置为 `false`：

```json
{
  "id": "app-to-disable",
  "enabled": false,
  // ... 其他配置
}
```

### Q5: 如何验证 JSON 配置格式？

```bash
python3 -m json.tool /home/user/Portal/portal/apps_config.json
```

如果输出格式化后的 JSON，说明格式正确。如果报错，则需要修复语法错误。

---

## 配置文件模板

以下是一个空白的配置模板，可用于快速添加新应用：

```json
{
  "id": "",
  "name": "",
  "name_en": "",
  "description": "",
  "category": "",
  "url": "/",
  "icon": "box",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "",
  "tags": [],
  "port": 0
}
```

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-14
