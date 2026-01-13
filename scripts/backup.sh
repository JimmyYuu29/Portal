#!/bin/bash
# Portal配置备份脚本

BACKUP_DIR="/home/ubuntu/Portal/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="portal_backup_${DATE}.tar.gz"

echo "================================================"
echo "Portal配置备份"
echo "================================================"
echo ""

# 创建备份目录
mkdir -p $BACKUP_DIR

# 临时目录
TEMP_DIR="/tmp/portal_backup_${DATE}"
mkdir -p $TEMP_DIR

echo "正在备份配置文件..."

# 备份Nginx配置
if [ -f /etc/nginx/sites-available/portal ]; then
    cp /etc/nginx/sites-available/portal $TEMP_DIR/nginx-portal.conf
    echo "✓ Nginx配置已备份"
fi

# 备份服务配置
if [ -f /etc/systemd/system/informept-api.service ]; then
    cp /etc/systemd/system/informept-api.service $TEMP_DIR/
    echo "✓ API服务配置已备份"
fi

if [ -f /etc/systemd/system/streamlit-informept.service ]; then
    cp /etc/systemd/system/streamlit-informept.service $TEMP_DIR/
    echo "✓ Streamlit服务配置已备份"
fi

# 备份Portal静态文件
if [ -d /home/ubuntu/Portal/static ]; then
    cp -r /home/ubuntu/Portal/static $TEMP_DIR/
    echo "✓ Portal静态文件已备份"
fi

# 备份防火墙规则
sudo ufw status numbered > $TEMP_DIR/ufw-rules.txt 2>/dev/null
echo "✓ 防火墙规则已备份"

# 创建备份信息文件
cat > $TEMP_DIR/backup_info.txt <<EOF
备份日期: $(date)
备份包含:
  - Nginx配置
  - Systemd服务配置
  - Portal静态文件
  - 防火墙规则

系统信息:
  主机名: $(hostname)
  内核: $(uname -r)
  IP地址: $(hostname -I)
EOF

# 打包备份
cd /tmp
tar -czf $BACKUP_DIR/$BACKUP_FILE portal_backup_${DATE}/
rm -rf $TEMP_DIR

echo ""
echo "================================================"
echo "备份完成!"
echo "备份文件: $BACKUP_DIR/$BACKUP_FILE"
echo "备份大小: $(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)"
echo ""
echo "恢复备份："
echo "  tar -xzf $BACKUP_DIR/$BACKUP_FILE -C /tmp"
echo "================================================"
