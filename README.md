# Portal Forvis Mazars

Portal de Acceso Unificado para Herramientas de Automatización | Unified Automation Tools Portal

---

## Funcionalidades / Features (v2.0.0)

| Funcionalidad | Descripción |
|---------------|-------------|
| **Login / Registro** | Autenticación con cuenta corporativa, departamento y rol |
| **RBAC** | Control de acceso por departamento y rol (apps filtradas) |
| **Panel de Admin** | Gestión de usuarios (buscar, editar, habilitar/deshabilitar, reset password) |
| **Olvidar Contraseña** | Envío de email vía Power Automate con token de un solo uso (30 min) |
| **Cambiar Contraseña** | Cambio de contraseña desde el dashboard (requiere contraseña actual) |
| **Estadísticas** | Seguimiento de visitas por app (SQLite), visitantes únicos diarios |
| **Apps Redirect** | `/go/<app_id>` con verificación RBAC + registro de acceso |
| **Persistencia Externa** | DATA_DIR para datos fuera del repo (sobrevive git pull) |

### Cuenta de Administrador por Defecto

| Campo | Valor |
|-------|-------|
| **Username** | `Admin` |
| **Password** | `Admin123` |

⚠️ **Cambiar la contraseña del Admin en producción inmediatamente.**

---

## Arquitectura / Architecture

```
Internet (usuario)
        ↓
80.225.186.223:80 (Nginx Reverse Proxy)
        ├── /             → Flask Portal (127.0.0.1:5000) — Login, Dashboard, /go/<id>
        ├── /app/         → Streamlit (127.0.0.1:8501)
        ├── /api/         → FastAPI (127.0.0.1:8000)
        └── /health       → Flask Portal health check
```

### Persistencia de Datos

```
DATA_DIR = /home/rootadmin/data/portal/
├── users.db           # Base de datos SQLite (usuarios, tokens, logs)
└── apps_config.json   # Configuración de apps (source of truth)

Repo (symlinks):
  portal/apps_config.json  →  DATA_DIR/apps_config.json
```

---

## Variables de Entorno / Environment Variables

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Flask (obligatoria en producción) | `cambiar-a-cadena-larga-aleatoria` |
| `DATA_DIR` | Directorio de datos persistentes | `/home/rootadmin/data/portal` |
| `PORTAL_DOMAIN` | Dominio para enlaces de reset | `http://80.225.186.223` |
| `POWER_AUTOMATE_URL` | URL del Flow HTTP Trigger | `https://prod-XX.logic.azure.com/...` |
| `POWER_AUTOMATE_SHARED_SECRET` | Secreto compartido para autenticación | `mi-secreto-largo` |
| `POWER_AUTOMATE_TIMEOUT_SECONDS` | Timeout HTTP (default: 10) | `10` |
| `POWER_AUTOMATE_RETRIES` | Reintentos (default: 3) | `3` |
| `PORTAL_HTTPS` | Activar cookie Secure (si HTTPS) | `true` |

---

## Información del Servidor / Server Information

| Ítem | Valor |
|------|-------|
| **IP Servidor** | 80.225.186.223 |
| **Directorio Portal** | /home/rootadmin/Portal |
| **DATA_DIR** | /home/rootadmin/data/portal |
| **Puerto Portal Flask** | 5000 |
| **Puerto Streamlit** | 8501 |
| **Puerto API** | 8000 |

---

## URLs de Acceso / Access URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Login** | http://80.225.186.223/login | Página de inicio de sesión |
| **Dashboard** | http://80.225.186.223/dashboard | Dashboard con apps filtradas |
| **Streamlit** | http://80.225.186.223/app/ | Aplicación Streamlit |
| **API** | http://80.225.186.223/api/ | API REST |
| **API Docs** | http://80.225.186.223/api/docs | Documentación FastAPI |
| **Health** | http://80.225.186.223/health | Health check |

---

## Inicio Rápido / Quick Start

### 1. Conectar al servidor

```bash
ssh rootadmin@80.225.186.223
```

### 2. Clonar repositorio

```bash
cd /home/rootadmin
git clone https://github.com/JimmyYuu29/Portal.git
```

### 3. Despliegue automático

```bash
cd /home/rootadmin/Portal/scripts
chmod +x deploy.sh
./deploy.sh
```

Guía detallada: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## Estructura de Directorios / Directory Structure

```
Portal/
├── README.md                         # Este archivo
├── DEPLOYMENT_GUIDE.md               # Guía de despliegue completa
├── QUICK_START.md                    # Inicio rápido
├── GUIA_CONFIGURACION.md            # Configuración de apps
├── HOW_TO_ADD_APP.md                # Cómo agregar aplicaciones
├── Standard_v3.1_EN.md              # Estándar arquitectónico
├── Mejora Portal.md                  # Notas de mejora
├── portal.service                    # Unit file de systemd
│
├── portal/                           # Aplicación Flask
│   ├── app.py                       # Aplicación principal (auth, RBAC, admin)
│   ├── models.py                    # Modelos de base de datos
│   ├── power_automate_client.py     # Cliente Power Automate (emails)
│   ├── apps_config.json             # Config de apps (symlink → DATA_DIR)
│   ├── requirements.txt             # Dependencias Python
│   ├── static/css/style.css         # Estilos
│   └── templates/                   # Plantillas HTML
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── admin.html
│       ├── forgot_password.html
│       ├── reset_password.html
│       ├── change_password.html
│       └── error.html
│
├── scripts/                          # Scripts de gestión
│   ├── deploy.sh                    # Despliegue automático
│   ├── sync-portal-data.sh          # Sincronización de datos
│   ├── check-status.sh              # Verificación de estado
│   ├── restart-all.sh               # Reinicio de servicios
│   └── backup.sh                    # Backup de configuración
│
├── docs/                             # Documentación adicional
│   └── POWER_AUTOMATE_EMAIL_SETUP.md # Guía de Power Automate
│
└── static/                           # Página estática legacy
    └── index.html
```

---

## Scripts de Gestión / Management Scripts

| Script | Función | Uso |
|--------|---------|-----|
| `deploy.sh` | Despliegue completo | `./scripts/deploy.sh` |
| `sync-portal-data.sh` | Sincronizar datos DATA_DIR | `./scripts/sync-portal-data.sh` |
| `check-status.sh` | Ver estado de servicios | `./scripts/check-status.sh` |
| `restart-all.sh` | Reiniciar todos los servicios | `./scripts/restart-all.sh` |
| `backup.sh` | Backup de configuración | `./scripts/backup.sh` |

---

## Comandos Comunes / Common Commands

### Verificar estado

```bash
./scripts/check-status.sh

# O manualmente:
sudo systemctl status portal.service
sudo systemctl status nginx
sudo systemctl status informept-api.service
sudo systemctl status streamlit-informept.service
```

### Reiniciar servicios

```bash
./scripts/restart-all.sh

# O manualmente:
sudo systemctl daemon-reload
sudo systemctl restart portal.service
sudo systemctl restart nginx
```

### Ver logs

```bash
# Portal Flask
sudo journalctl -u portal.service -f

# Nginx
sudo tail -f /var/log/nginx/portal_access.log
sudo tail -f /var/log/nginx/portal_error.log

# API / Streamlit
sudo journalctl -u informept-api.service -f
sudo journalctl -u streamlit-informept.service -f
```

---

## Actualizar Portal / Update Portal

```bash
cd /home/rootadmin/Portal
git pull origin main
./scripts/restart-all.sh   # Ejecuta sync-portal-data.sh automáticamente
```

> ⚠️ DATA_DIR nunca se sobrescribe por git pull. El sync script crea symlinks.

---

## Documentos Relacionados / Related Documents

- [Inicio rápido (QUICK_START.md)](QUICK_START.md)
- [Guía de despliegue (DEPLOYMENT_GUIDE.md)](DEPLOYMENT_GUIDE.md)
- [Configuración del portal (GUIA_CONFIGURACION.md)](GUIA_CONFIGURACION.md)
- [Cómo agregar apps (HOW_TO_ADD_APP.md)](HOW_TO_ADD_APP.md)
- [Estándar arquitectónico (Standard_v3.1_EN.md)](Standard_v3.1_EN.md)
- [Guía Power Automate (docs/POWER_AUTOMATE_EMAIL_SETUP.md)](docs/POWER_AUTOMATE_EMAIL_SETUP.md)

---

## Información de Versión / Version

- **Portal Version**: 2.0.0
- **Last Updated**: 2025-02-23
- **Author**: JimmyYuu29

---

## Licencia / License

[MIT License](LICENSE)
