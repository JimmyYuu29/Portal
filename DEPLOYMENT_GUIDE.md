# Portal Forvis Mazars - Guía de Despliegue Completa

Guía completa desde cero para desplegar el Portal en un servidor Ubuntu.

---

## Índice

1. [Información del Servidor](#información-del-servidor)
2. [Requisitos Previos](#requisitos-previos)
3. [Paso 1: Conectar al Servidor](#paso-1-conectar-al-servidor)
4. [Paso 2: Preparar el Sistema](#paso-2-preparar-el-sistema)
5. [Paso 3: Clonar el Repositorio](#paso-3-clonar-el-repositorio)
6. [Paso 4: Crear DATA_DIR y Sincronizar](#paso-4-crear-data_dir-y-sincronizar)
7. [Paso 5: Instalar Dependencias Python](#paso-5-instalar-dependencias-python)
8. [Paso 6: Configurar Nginx](#paso-6-configurar-nginx)
9. [Paso 7: Configurar systemd](#paso-7-configurar-systemd)
10. [Paso 8: Configurar Variables de Entorno](#paso-8-configurar-variables-de-entorno)
11. [Paso 9: Iniciar Servicios](#paso-9-iniciar-servicios)
12. [Paso 10: Verificar Despliegue](#paso-10-verificar-despliegue)
13. [Paso 11: Configurar Firewall](#paso-11-configurar-firewall)
14. [SSL (Opcional)](#ssl-opcional)
15. [Gestión de Logs](#gestión-de-logs)
16. [Estrategia de Backup](#estrategia-de-backup)
17. [Actualización del Portal](#actualización-del-portal)
18. [Rollback](#rollback)
19. [Solución de Problemas](#solución-de-problemas)
20. [Referencia Rápida de Comandos](#referencia-rápida-de-comandos)

---

## Información del Servidor

| Ítem | Valor |
|------|-------|
| **IP Pública** | 80.225.186.223 |
| **Sistema Operativo** | Ubuntu 18.04+ |
| **Directorio Portal** | /home/rootadmin/Portal |
| **DATA_DIR** | /home/rootadmin/data/portal |
| **Puerto Portal Flask** | 5000 (gunicorn) |
| **Puerto Streamlit** | 8501 |
| **Puerto API** | 8000 |
| **Nginx** | Puerto 80 (HTTP), 443 (HTTPS) |

---

## Requisitos Previos

1. **Acceso SSH** al servidor como `rootadmin`
2. **Git** instalado
3. **Python 3.8+** instalado
4. **InformePT** desplegado y funcionando (opcional, para /app/ y /api/)

---

## Paso 1: Conectar al Servidor

```bash
ssh rootadmin@80.225.186.223
```

---

## Paso 2: Preparar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git nginx curl net-tools python3 python3-pip python3-venv ufw
```

---

## Paso 3: Clonar el Repositorio

```bash
cd /home/rootadmin
git clone https://github.com/JimmyYuu29/Portal.git
cd Portal
chmod +x scripts/*.sh
```

---

## Paso 4: Crear DATA_DIR y Sincronizar

El script `sync-portal-data.sh` gestiona la persistencia de datos:

```bash
export DATA_DIR=/home/rootadmin/data/portal
export REPO_DIR=/home/rootadmin/Portal
./scripts/sync-portal-data.sh
```

**Lo que hace:**
1. Crea `DATA_DIR` si no existe
2. Copia `apps_config.json` por defecto a DATA_DIR (primera vez)
3. Crea symlinks:
   - `portal/apps_config.json` → `DATA_DIR/apps_config.json`
4. Establece permisos

---

## Paso 5: Instalar Dependencias Python

```bash
cd /home/rootadmin/Portal/portal
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Dependencias clave:
- `Flask` - Framework web
- `Flask-Login` - Autenticación de sesiones
- `Flask-WTF` - Protección CSRF
- `gunicorn` - Servidor WSGI de producción
- `requests` - Cliente HTTP (Power Automate)

---

## Paso 6: Configurar Nginx

### 6.1 Crear configuración

```bash
sudo nano /etc/nginx/sites-available/portal
```

### 6.2 Contenido de la configuración

```nginx
server {
    listen 80;
    server_name 80.225.186.223;

    access_log /var/log/nginx/portal_access.log;
    error_log /var/log/nginx/portal_error.log;

    # Portal Flask backend (login, dashboard, /go/<app_id>)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30;
        proxy_send_timeout 60;
        proxy_read_timeout 60;
    }

    # API (FastAPI)
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
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit
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
        proxy_buffering off;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Streamlit WebSocket
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
```

### 6.3 Activar la configuración

```bash
sudo ln -sf /etc/nginx/sites-available/portal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

> **Cambio vs v1.0**: `location /` ahora hace proxy a Flask:5000 en vez de servir archivos estáticos. Los bloques `/api/` y `/app/` se mantienen sin cambios.

---

## Paso 7: Configurar systemd

```bash
sudo cp /home/rootadmin/Portal/portal.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable portal.service
```

El archivo `portal.service` usa gunicorn con 2 workers en el puerto 5000.

---

## Paso 8: Configurar Variables de Entorno

### Método recomendado: systemd override

```bash
sudo systemctl edit portal.service
```

Agregar las variables secretas:

```ini
[Service]
Environment="SECRET_KEY=GENERA-UNA-CLAVE-SECRETA-LARGA-AQUI"
Environment="POWER_AUTOMATE_URL=https://prod-XX.westeurope.logic.azure.com:443/workflows/..."
Environment="POWER_AUTOMATE_SHARED_SECRET=tu-secreto-compartido-aqui"
```

```bash
sudo systemctl daemon-reload
```

### Variables disponibles

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `SECRET_KEY` | ✅ Sí | Clave secreta Flask |
| `DATA_DIR` | No (default: /home/rootadmin/data/portal) | Directorio de datos |
| `PORTAL_DOMAIN` | No (default: http://80.225.186.223) | Dominio para reset links |
| `POWER_AUTOMATE_URL` | Para email | URL del Flow HTTP Trigger |
| `POWER_AUTOMATE_SHARED_SECRET` | Para email | Secreto compartido |
| `POWER_AUTOMATE_TIMEOUT_SECONDS` | No (default: 10) | Timeout HTTP |
| `POWER_AUTOMATE_RETRIES` | No (default: 3) | Reintentos |
| `PORTAL_HTTPS` | No | Activar cookie Secure |

---

## Paso 9: Iniciar Servicios

```bash
sudo systemctl start portal.service
sudo systemctl restart nginx

# Verificar
sudo systemctl status portal.service
sudo systemctl status nginx
```

---

## Paso 10: Verificar Despliegue

### Desde el servidor

```bash
# Health check
curl -s http://localhost/health | python3 -m json.tool

# Login page (debe retornar 200)
curl -s -o /dev/null -w "%{http_code}" http://localhost/login

# Health check completo
./scripts/check-status.sh
```

### Desde el navegador

| URL | Resultado Esperado |
|-----|-------------------|
| http://80.225.186.223/ | Redirige a /login |
| http://80.225.186.223/login | Página de login |
| http://80.225.186.223/health | JSON `{"status": "healthy"}` |
| http://80.225.186.223/app/ | Streamlit |
| http://80.225.186.223/api/docs | Documentación API |

### Primer login

1. Abrir http://80.225.186.223/login
2. Username: `Admin` / Password: `Admin123`
3. Dashboard muestra todas las apps
4. Ir a Admin panel → verificar usuarios

---

## Paso 11: Configurar Firewall

```bash
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw deny 5000/tcp comment 'Block direct Flask'
sudo ufw deny 8000/tcp comment 'Block direct API'
sudo ufw deny 8501/tcp comment 'Block direct Streamlit'
sudo ufw enable
sudo ufw reload
```

---

## SSL (Opcional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
sudo certbot renew --dry-run
```

Después de activar HTTPS, establecer `PORTAL_HTTPS=true` en el servicio.

---

## Gestión de Logs

| Log | Ubicación |
|-----|-----------|
| Portal Flask | `sudo journalctl -u portal.service` |
| Nginx Access | `/var/log/nginx/portal_access.log` |
| Nginx Error | `/var/log/nginx/portal_error.log` |
| API | `sudo journalctl -u informept-api.service` |
| Streamlit | `sudo journalctl -u streamlit-informept.service` |

```bash
# Ver logs en tiempo real
sudo journalctl -u portal.service -f
sudo tail -f /var/log/nginx/portal_access.log
```

---

## Estrategia de Backup

### Datos críticos (DATA_DIR)

```bash
# Backup manual
cp -r /home/rootadmin/data/portal /home/rootadmin/data/portal-backup-$(date +%Y%m%d)

# Backup automático (crontab)
crontab -e
# Agregar:
0 2 * * * tar czf /home/rootadmin/backups/portal-$(date +\%Y\%m\%d).tar.gz /home/rootadmin/data/portal
```

### Archivos del backup

- `users.db` — Base de datos de usuarios, tokens, estadísticas
- `apps_config.json` — Configuración de aplicaciones

---

## Actualización del Portal

### Flujo estándar

```bash
cd /home/rootadmin/Portal
git pull origin main
./scripts/restart-all.sh   # Ejecuta sync + restart
```

### Actualización manual paso a paso

```bash
cd /home/rootadmin/Portal
git pull origin main

# Actualizar dependencias (si cambiaron)
source portal/venv/bin/activate
pip install -r portal/requirements.txt
deactivate

# Sincronizar datos
./scripts/sync-portal-data.sh

# Reiniciar
sudo systemctl restart portal.service
sudo systemctl restart nginx
```

---

## Rollback

### Rollback por git

```bash
cd /home/rootadmin/Portal
git log --oneline -5  # Ver commits recientes
git checkout <commit_hash>
sudo systemctl restart portal.service
```

### Rollback de datos

```bash
# Restaurar desde backup
cp /home/rootadmin/data/portal-backup-YYYYMMDD/users.db /home/rootadmin/data/portal/
cp /home/rootadmin/data/portal-backup-YYYYMMDD/apps_config.json /home/rootadmin/data/portal/
sudo systemctl restart portal.service
```

> ⚠️ DATA_DIR siempre se preserva a través de actualizaciones git. Los datos nunca se pierden por `git pull`.

---

## Solución de Problemas

### Portal no carga (502 Bad Gateway)

```bash
# 1. Verificar que portal.service está corriendo
sudo systemctl status portal.service
sudo journalctl -u portal.service -n 50

# 2. Verificar puerto 5000
sudo ss -tlnp | grep :5000

# 3. Reiniciar
sudo systemctl restart portal.service
```

### Login no funciona

```bash
# Verificar DB existe
ls -la /home/rootadmin/data/portal/users.db

# Verificar logs
sudo journalctl -u portal.service -n 30 | grep -i error
```

### Apps no se muestran en dashboard

```bash
# Verificar symlink
ls -la /home/rootadmin/Portal/portal/apps_config.json
# Debe apuntar a DATA_DIR

# Verificar JSON válido
python3 -m json.tool /home/rootadmin/data/portal/apps_config.json

# Verificar que el usuario tiene el departamento correcto
# (Desde admin panel o directamente en DB)
```

### Power Automate email no funciona

```bash
# Verificar variables de entorno
sudo systemctl show portal.service | grep -i power

# Verificar logs de intentos
sudo journalctl -u portal.service | grep -i "power\|automate\|email"

# Probar con curl (ver docs/POWER_AUTOMATE_EMAIL_SETUP.md)
```

---

## Referencia Rápida de Comandos

```bash
# Estado completo
./scripts/check-status.sh

# Reiniciar todo (con sincronización)
./scripts/restart-all.sh

# Sincronizar datos solamente
./scripts/sync-portal-data.sh

# Despliegue completo
./scripts/deploy.sh

# Ver logs del Portal
sudo journalctl -u portal.service -f

# Entrar al virtualenv
source /home/rootadmin/Portal/portal/venv/bin/activate
```

---

**Versión del documento**: 2.0.0
**Última actualización**: 2025-02-23
