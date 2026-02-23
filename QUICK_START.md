# Portal Forvis Mazars - Guía de Inicio Rápido

Despliegue del Portal en menos de 10 minutos.

---

## Información del Servidor

| Ítem | Valor |
|------|-------|
| **IP Servidor** | 10.32.1.150 |
| **Portal** | /home/rootadmin/Portal |
| **DATA_DIR** | /home/rootadmin/data/portal |
| **Puerto Portal** | 5000 (Flask/gunicorn) |
| **Puerto Streamlit** | 8501 |
| **Puerto API** | 8000 |

---

## Despliegue Rápido

### Paso 1: Conectar al servidor

```bash
ssh rootadmin@10.32.1.150
```

### Paso 2: Clonar el repositorio

```bash
cd /home/rootadmin
git clone https://github.com/JimmyYuu29/Portal.git
```

### Paso 3: Ejecutar el script de despliegue

```bash
cd /home/rootadmin/Portal/scripts
chmod +x deploy.sh sync-portal-data.sh
./deploy.sh
```

El script automáticamente:
1. Instala dependencias del sistema
2. Crea virtual environment Python
3. Instala paquetes Python (Flask, Flask-Login, Flask-WTF, etc.)
4. Ejecuta `sync-portal-data.sh` (crea DATA_DIR + symlinks)
5. Configura Nginx (proxy / → Flask:5000)
6. Instala el servicio systemd `portal.service`
7. Arranca todos los servicios

### Paso 4: Configurar secretos (IMPORTANTE)

```bash
# Editar los secretos del servicio
sudo systemctl edit portal.service
```

Agregar:
```ini
[Service]
Environment="SECRET_KEY=tu-clave-secreta-larga-aleatoria"
Environment="POWER_AUTOMATE_URL=https://prod-XX.logic.azure.com/workflows/..."
Environment="POWER_AUTOMATE_SHARED_SECRET=tu-secreto-compartido"
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl restart portal.service
```

### Paso 5: Iniciar sesión como Admin

1. Abrir: http://10.32.1.150/login
2. **Username**: `Admin`
3. **Password**: `Admin123`
4. ⚠️ Cambiar la contraseña inmediatamente desde el dashboard

---

## Inicialización de Datos (Automática)

Al primer arranque, el Portal:
- Crea `DATA_DIR` si no existe
- Inicializa `users.db` con el usuario Admin
- Copia `apps_config.json` a DATA_DIR (si no existe)
- Crea symlinks desde el repo a DATA_DIR

---

## URLs de Acceso

| Servicio | URL |
|----------|-----|
| **Login** | http://10.32.1.150/login |
| **Dashboard** | http://10.32.1.150/dashboard |
| **Admin Panel** | http://10.32.1.150/admin |
| **Streamlit** | http://10.32.1.150/app/ |
| **API** | http://10.32.1.150/api/ |
| **API Docs** | http://10.32.1.150/api/docs |
| **Health** | http://10.32.1.150/health |

---

## Comandos de Gestión

### Verificar estado

```bash
cd /home/rootadmin/Portal
./scripts/check-status.sh
```

### Reiniciar servicios

```bash
./scripts/restart-all.sh
```

Esto ejecuta automáticamente `sync-portal-data.sh` antes de reiniciar.

### Actualizar Portal

```bash
cd /home/rootadmin/Portal
git pull origin main
./scripts/restart-all.sh
```

> DATA_DIR no se sobrescribe por git pull.

---

## Ver Logs

```bash
# Portal Flask
sudo journalctl -u portal.service -f

# Nginx
sudo tail -f /var/log/nginx/portal_access.log
sudo tail -f /var/log/nginx/portal_error.log

# API
sudo journalctl -u informept-api.service -f

# Streamlit
sudo journalctl -u streamlit-informept.service -f
```

---

## Solución Rápida de Problemas

### No se puede acceder al Portal

```bash
sudo systemctl status portal.service
sudo systemctl status nginx
sudo nginx -t
sudo systemctl restart portal.service
sudo systemctl restart nginx
```

### Login no funciona

```bash
# Verificar que portal.service está corriendo
sudo journalctl -u portal.service -n 30

# Verificar que DATA_DIR existe y tiene permisos
ls -la /home/rootadmin/data/portal/
```

---

## Documentos Relacionados

- **Guía de despliegue completa**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **README principal**: [README.md](README.md)
- **Configuración de apps**: [GUIA_CONFIGURACION.md](GUIA_CONFIGURACION.md)
- **Guía Power Automate**: [docs/POWER_AUTOMATE_EMAIL_SETUP.md](docs/POWER_AUTOMATE_EMAIL_SETUP.md)
- **Estándar arquitectónico**: [Standard_v3.1_EN.md](Standard_v3.1_EN.md)

---

**Tiempo estimado**: < 10 minutos
**Dificultad**: Sencillo
**Última actualización**: 2025-02-23
