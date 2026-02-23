# Guía de Configuración del Portal Forvis Mazars

Esta guía explica cómo modificar la interfaz del portal, agregar categorías de servicios, configurar nuevas aplicaciones y gestionar el control de acceso (RBAC).

---

## Archivo de Configuración Principal

La configuración del portal se gestiona desde un archivo centralizado en el directorio de datos persistente:

```
DATA_DIR/apps_config.json
```

Donde `DATA_DIR` es por defecto `/home/rootadmin/data/portal/`.

> **Nota**: El archivo `portal/apps_config.json` en el repositorio es un **symlink** que apunta a `DATA_DIR/apps_config.json`. Editar cualquiera de los dos edita el mismo archivo.

---

## Estructura del Archivo de Configuración

```json
{
  "portal_name": "Forvis Mazars",
  "portal_description": "Portal de Acceso Unificado para las herramientas de automatización",
  "server_ip": "80.225.186.223",
  "categories": [...],
  "apps": [...]
}
```

---

## 1. Modificar el Branding del Portal

### Cambiar el Título Principal

```json
"portal_name": "Forvis Mazars"
```

### Cambiar la Descripción

```json
"portal_description": "Portal de Acceso Unificado para las herramientas de automatización"
```

---

## 2. Agregar Categorías de Servicios

```json
{
  "id": "precio-transferencia",
  "name": "Precio de transferencia",
  "icon": "calculator",
  "description": "Herramientas de automatización para el área de Precio de Transferencia"
}
```

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `id` | Identificador único (sin espacios, minúsculas) | `"auditoria"` |
| `name` | Nombre visible en la interfaz | `"Auditoría"` |
| `icon` | Nombre del icono de Lucide | `"clipboard-check"` |
| `description` | Descripción de la categoría | `"Herramientas para..."` |

### Categorías Predefinidas

- `precio-transferencia` - Precio de Transferencia
- `auditoria` - Auditoría
- `administracion` - Administración
- `general` - General
- `otros` - Otros

---

## 3. Agregar Servicios/Aplicaciones

```json
{
  "id": "mi-aplicacion",
  "name": "Mi Aplicación",
  "name_en": "My Application",
  "description": "Descripción detallada de la aplicación...",
  "category": "precio-transferencia",
  "url": "/mi-app/",
  "icon": "bar-chart-2",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo de Desarrollo",
  "tags": ["etiqueta1", "etiqueta2"],
  "port": 8080,
  "access": {
    "departments": ["precio_transferencia"],
    "roles": ["senior", "manager", "socio"]
  }
}
```

### Campos de una Aplicación

| Campo | Requerido | Descripción | Ejemplo |
|-------|-----------|-------------|---------|
| `id` | Sí | Identificador único | `"mi-app"` |
| `name` | Sí | Nombre en español | `"Mi Aplicación"` |
| `name_en` | No | Nombre en inglés | `"My Application"` |
| `description` | Sí | Descripción detallada | `"Esta aplicación..."` |
| `category` | Sí | ID de la categoría | `"auditoria"` |
| `url` | Sí | Ruta de acceso | `"/mi-app/"` |
| `icon` | Sí | Nombre del icono de Lucide | `"file-text"` |
| `enabled` | No | Activar/desactivar (default: true) | `true` |
| `version` | No | Versión de la aplicación | `"1.0.0"` |
| `maintainer` | No | Responsable del servicio | `"Equipo X"` |
| `tags` | No | Etiquetas para filtrado | `["api", "web"]` |
| `port` | No | Puerto del servicio | `8080` |
| **`access`** | **No** | **Control de acceso RBAC (nuevo v2.0)** | **Ver abajo** |

---

## 4. Control de Acceso RBAC (Nuevo en v2.0)

### Campo `access`

Cada aplicación puede tener un campo `access` para restringir quién puede verla y usarla:

```json
"access": {
  "departments": ["precio_transferencia", "it"],
  "roles": ["senior", "manager", "socio"]
}
```

**Reglas:**
- Si `departments` está **vacío** o **ausente** → todos los departamentos pueden acceder
- Si `roles` está **vacío** o **ausente** → todos los roles pueden acceder
- Si ambos están presentes → el usuario debe cumplir **ambas** condiciones
- Los **administradores** siempre ven todas las aplicaciones

### Departamentos Internos (IDs)

Estos son los identificadores internos que se usan en el campo `departments[]`:

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

> ⚠️ **Importante**: Usar siempre el ID interno (columna izquierda) en la configuración, no el nombre en pantalla.

### Roles Internos (IDs)

| ID Interno | Nombre en Pantalla |
|------------|-------------------|
| `junior` | Junior |
| `senior` | Senior |
| `manager` | Manager |
| `socio` | Socio |

### Ejemplos de Acceso

#### App solo para Precio de Transferencia (todos los roles)

```json
"access": {
  "departments": ["precio_transferencia"],
  "roles": []
}
```

#### App para seniors y superiores de IT y Auditoría

```json
"access": {
  "departments": ["it", "auditoria"],
  "roles": ["senior", "manager", "socio"]
}
```

#### App para todos (sin restricción)

```json
"access": {
  "departments": [],
  "roles": []
}
```

O simplemente omitir el campo `access`.

---

## 5. Compatibilidad hacia Atrás

Las aplicaciones que **no tengan** el campo `access` seguirán siendo visibles para todos los usuarios. Esto asegura compatibilidad con configuraciones anteriores a v2.0.

---

## 6. Iconos Disponibles (Lucide Icons)

El portal utiliza la biblioteca **Lucide Icons**: [https://lucide.dev/icons/](https://lucide.dev/icons/)

| Departamento | Iconos Sugeridos |
|--------------|------------------|
| Precio de Transferencia | `calculator`, `file-spreadsheet`, `trending-up` |
| Auditoría | `clipboard-check`, `file-search`, `shield-check` |
| Administración | `building-2`, `briefcase`, `settings` |
| General | `briefcase`, `layout-dashboard`, `grid` |

---

## 7. Aplicar Cambios

Después de modificar `apps_config.json`:

```bash
# Reiniciar el servicio del Portal
sudo systemctl restart portal.service

# O reiniciar todo
./scripts/restart-all.sh
```

> Como `apps_config.json` está en DATA_DIR (a través de symlink), los cambios sobreviven `git pull`.

---

## 8. Validación

```bash
# Verificar JSON válido
python3 -m json.tool /home/rootadmin/data/portal/apps_config.json

# Verificar symlink activo
ls -la /home/rootadmin/Portal/portal/apps_config.json
```

---

## 9. Notas Importantes

1. **Las categorías vacías** (sin apps asignadas) no se muestran en la interfaz.
2. **IDs únicos**: Tanto categorías como aplicaciones deben tener `id` únicos.
3. **IDs de departamento**: Usar siempre los IDs internos (sin espacios, sin tildes).
4. **Control de acceso retroactivo**: Al agregar `access` a una app existente, solo los usuarios con el departamento/rol correcto podrán verla.
5. **Admins**: Los usuarios con `is_admin=1` ven todas las apps independientemente de `access`.

---

## 10. Soporte

Para consultas adicionales o soporte técnico, contacta al equipo de desarrollo.

---

**Versión del documento**: 2.0.0
**Última actualización**: 2025-02-23
