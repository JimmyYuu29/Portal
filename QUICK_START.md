# InformePT Portal 快速部署指南

5分钟快速部署Portal到Ubuntu服务器。

---

## 服务器信息

| 项目 | 值 |
|------|-----|
| **服务器IP** | 80.225.186.223 |
| **InformePT位置** | /home/ubuntu/InformePT |
| **Portal位置** | /home/ubuntu/Portal |
| **Streamlit端口** | 8501 |
| **API端口** | 8000 |

---

## 快速部署（5分钟）

### 步骤1：连接服务器

```bash
ssh ubuntu@80.225.186.223
```

### 步骤2：克隆仓库

```bash
cd /home/ubuntu
git clone https://github.com/JimmyYuu29/Portal.git
```

### 步骤3：运行自动部署

```bash
cd /home/ubuntu/Portal/scripts
chmod +x deploy.sh
./deploy.sh
```

**完成！** 脚本会自动完成所有配置。

---

## 访问地址

部署完成后，通过以下地址访问：

| 服务 | URL |
|------|-----|
| **Portal主页** | http://80.225.186.223/ |
| **Streamlit版本** | http://80.225.186.223/app/ |
| **API版本** | http://80.225.186.223/api/ |
| **API文档** | http://80.225.186.223/api/docs |
| **健康检查** | http://80.225.186.223/health |

---

## 管理命令

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

或手动重启：

```bash
sudo systemctl daemon-reload
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

### 备份配置

```bash
cd /home/ubuntu/Portal/scripts
./backup.sh
```

---

## 查看日志

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

---

## 快速故障排查

### 无法访问Portal

```bash
sudo systemctl status nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 应用无响应

```bash
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service
sudo systemctl restart informept-api.service
sudo systemctl restart streamlit-informept.service
```

---

## 更新Portal

```bash
cd /home/ubuntu/Portal
git pull origin main
./scripts/restart-all.sh
```

---

## 相关文档

- **详细部署指南**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **项目说明**: [README.md](README.md)
- **架构标准**: [Standard_v3.1_EN.md](Standard_v3.1_EN.md)

---

**部署时间**: < 5分钟
**难度**: 简单

---

**最后更新**: 2026-01-13
