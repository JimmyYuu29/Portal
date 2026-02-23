# Portal - Guía para Agregar Aplicaciones

Guía detallada sobre cómo agregar nuevas aplicaciones al Portal.

---

## Índice

1. [Visión General](#visión-general)
2. [Pasos para Agregar una App](#pasos-para-agregar-una-app)
3. [Campos de Configuración](#campos-de-configuración)
4. [Configurar Control de Acceso (RBAC)](#configurar-control-de-acceso-rbac)
5. [Verificar Permisos](#verificar-permisos)
6. [Agregar Categorías](#agregar-categorías)
7. [Nginx (Opcional)](#nginx-opcional)
8. [Ejemplo Completo](#ejemplo-completo)
9. [FAQ](#faq)

---

## Visión General

### Arquitectura

```
Usuario → Login → Dashboard (muestra solo apps con permiso)
                      │
                      ▼
               /go/<app_id> → Verificación RBAC → Registro de acceso → Redirect
                      │
                      ▼
               Aplicación (Streamlit:8501, FastAPI:8000, etc.)
```

### Archivo de configuración

```
DATA_DIR/apps_config.json
```

> `DATA_DIR` es por defecto `/home/rootadmin/data/portal/`
> El archivo `portal/apps_config.json` en el repo es un symlink a DATA_DIR.

---

## Pasos para Agregar una App

### Paso 1: Editar el archivo de configuración

```bash
nano /home/rootadmin/data/portal/apps_config.json
```

### Paso 2: Agregar la app en el array `apps`

```json
{
  "id": "nueva-app",
  "name": "Nueva Aplicación",
  "name_en": "New Application",
  "description": "Descripción de la aplicación...",
  "category": "auditoria",
  "url": "/nueva-app/",
  "icon": "file-text",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo Responsable",
  "tags": ["tag1", "tag2"],
  "port": 8502,
  "access": {
    "departments": ["auditoria"],
    "roles": []
  }
}
```

### Paso 3: Reiniciar el Portal

```bash
sudo systemctl restart portal.service
```

### Paso 4: Verificar

1. Iniciar sesión con un usuario del departamento `auditoria`
2. La app debería aparecer en el dashboard
3. Hacer clic → debe redirigir correctamente

---

## Campos de Configuración

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | Sí | ID único, usado en `/go/<id>` |
| `name` | string | Sí | Nombre de la app |
| `name_en` | string | No | Nombre en inglés |
| `description` | string | Sí | Descripción visible |
| `category` | string | Sí | ID de categoría |
| `url` | string | Sí | URL de destino |
| `icon` | string | No | Icono Lucide (default: `box`) |
| `enabled` | bool | No | Activar/desactivar (default: `true`) |
| `version` | string | No | Versión |
| `maintainer` | string | No | Responsable |
| `tags` | array | No | Etiquetas |
| `port` | int | No | Puerto del servicio |
| **`access`** | **object** | **No** | **Control de acceso RBAC** |

### URL de la App

| Tipo | Ejemplo | Uso |
|------|---------|-----|
| Ruta relativa | `/app/` | Apps del mismo servidor (via Nginx) |
| URL completa | `https://external.com/app` | Apps externas |
| URL con IP+puerto | `http://10.0.0.1:3000/` | Apps en otros servidores |

---

## Configurar Control de Acceso (RBAC)

### Estructura del campo `access`

```json
"access": {
  "departments": ["departamento1", "departamento2"],
  "roles": ["rol1", "rol2"]
}
```

### Reglas de acceso

| `departments` | `roles` | Quién ve la app |
|---------------|---------|-----------------|
| `[]` o ausente | `[]` o ausente | **Todos** los usuarios |
| `["auditoria"]` | `[]` | Todos del depto. Auditoría |
| `[]` | `["manager", "socio"]` | Managers y Socios de cualquier depto. |
| `["it"]` | `["senior"]` | Seniors del depto. IT |

> Los **administradores** siempre ven todas las apps.

### IDs de Departamento

| ID Interno | Nombre en Pantalla |
|------------|-------------------|
| `auditoria` | Auditoría |
| `precio_transferencia` | Precio de Transferencia |
| `tax` | Tax |
| `legal` | Legal |
| `administracion_finanza` | Administración y Finanza |
| `it` | IT |
| `quality_risk` | Quality & Risk Management |
| `aos` | AOS |
| `otros` | Otros |

### IDs de Rol

| ID Interno | Nombre en Pantalla |
|------------|-------------------|
| `junior` | Junior |
| `senior` | Senior |
| `manager` | Manager |
| `socio` | Socio |

---

## Verificar Permisos

### Método 1: Desde el navegador

1. Iniciar sesión con un usuario del departamento/rol esperado
2. Verificar que la app aparece en el dashboard
3. Hacer clic en la app → debe redirigir correctamente

4. Iniciar sesión con un usuario de **otro** departamento
5. Verificar que la app **NO** aparece en su dashboard
6. Acceder directamente a `/go/<app_id>` → debe mostrar error 403

### Método 2: Desde curl (requiere sesión)

```bash
# Intentar acceso directo sin login → debe redirigir a /login
curl -s -o /dev/null -w "%{http_code}" http://80.225.186.223/go/nueva-app
# Esperado: 302 (redirect to login)
```

### Método 3: Desde Admin Panel

1. Login como Admin
2. Ir a `/admin`
3. Verificar que el usuario tiene el departamento correcto
4. Editar departamento si es necesario
5. El usuario verá las apps al re-iniciar sesión

---

## Agregar Categorías

```json
{
  "id": "nueva-categoria",
  "name": "Nueva Categoría",
  "icon": "folder",
  "description": "Descripción de la categoría"
}
```

Las categorías sin apps asignadas no se muestran.

---

## Nginx (Opcional)

Si la nueva app necesita proxy Nginx:

```bash
sudo nano /etc/nginx/sites-available/portal
```

Agregar bloque:

```nginx
location /nueva-app/ {
    proxy_pass http://127.0.0.1:8502/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Ejemplo Completo

### App con restricción de departamento

```json
{
  "id": "informe-auditoria",
  "name": "Informe de Auditoría",
  "name_en": "Audit Report",
  "description": "Generación automática de informes de auditoría.",
  "category": "auditoria",
  "url": "/auditoria-report/",
  "icon": "clipboard-check",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo de Auditoría",
  "tags": ["auditoria", "informe", "automatización"],
  "port": 8502,
  "access": {
    "departments": ["auditoria"],
    "roles": []
  }
}
```

### App con restricción de rol

```json
{
  "id": "panel-direccion",
  "name": "Panel de Dirección",
  "name_en": "Executive Dashboard",
  "description": "Panel de control para socios y managers con KPIs estratégicos.",
  "category": "general",
  "url": "/panel-exec/",
  "icon": "bar-chart-3",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo IT",
  "tags": ["dashboard", "kpi", "ejecutivo"],
  "port": 8503,
  "access": {
    "departments": [],
    "roles": ["manager", "socio"]
  }
}
```

### App sin restricción (todos)

```json
{
  "id": "wiki-interna",
  "name": "Wiki Interna",
  "description": "Base de conocimientos de la organización.",
  "category": "general",
  "url": "https://wiki.internal.com/",
  "icon": "book-open",
  "enabled": true,
  "access": {}
}
```

---

## FAQ

### Q1: La app no aparece en el dashboard

1. Verificar `enabled: true`
2. Verificar que la `category` existe en `categories[]`
3. Verificar que el usuario tiene el departamento/rol correcto
4. Validar JSON: `python3 -m json.tool apps_config.json`

### Q2: Error 403 al acceder a la app

El usuario no tiene permiso. Verificar:
- El departamento del usuario (en Admin panel)
- La configuración `access.departments` de la app
- El rol del usuario vs `access.roles`

### Q3: ¿Cómo desactivar el control de acceso?

Establecer `access` vacío o eliminar el campo:
```json
"access": {}
```

### Q4: ¿Los cambios en DATA_DIR se pierden con git pull?

No. `DATA_DIR` está fuera del repositorio. Los symlinks se recrean con `sync-portal-data.sh`.

---

**Versión del documento**: 2.0.0
**Última actualización**: 2025-02-23
