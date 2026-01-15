# Guia de Configuracion del Portal Forvis Mazars

Esta guia explica como modificar la interfaz del portal, agregar categorias de servicios y configurar nuevas aplicaciones.

## Archivo de Configuracion Principal

Toda la configuracion del portal se encuentra en un unico archivo:

```
portal/apps_config.json
```

## Estructura del Archivo de Configuracion

```json
{
  "portal_name": "Forvis Mazars",
  "portal_description": "Portal de Acceso Unificado para las herramientas de automatizacion",
  "server_ip": "80.225.186.223",
  "categories": [...],
  "apps": [...]
}
```

---

## 1. Modificar el Branding del Portal

### Cambiar el Titulo Principal

Edita el campo `portal_name`:

```json
"portal_name": "Forvis Mazars"
```

### Cambiar la Descripcion/Subtitulo

Edita el campo `portal_description`:

```json
"portal_description": "Portal de Acceso Unificado para las herramientas de automatizacion"
```

---

## 2. Agregar Categorias de Servicios

Las categorias agrupan las aplicaciones por departamento o funcion. Cada categoria tiene la siguiente estructura:

```json
{
  "id": "precio-transferencia",
  "name": "Precio de transferencia",
  "icon": "calculator",
  "description": "Herramientas de automatizacion para el area de Precio de Transferencia"
}
```

### Campos de una Categoria

| Campo | Descripcion | Ejemplo |
|-------|-------------|---------|
| `id` | Identificador unico (sin espacios, minusculas) | `"auditoria"` |
| `name` | Nombre visible en la interfaz | `"Auditoria"` |
| `icon` | Nombre del icono de Lucide | `"clipboard-check"` |
| `description` | Descripcion de la categoria | `"Herramientas para..."` |

### Ejemplo: Agregar una Nueva Categoria

Para agregar la categoria "Recursos Humanos", anade este objeto al array `categories`:

```json
{
  "id": "recursos-humanos",
  "name": "Recursos Humanos",
  "icon": "users",
  "description": "Herramientas de automatizacion para el area de Recursos Humanos"
}
```

### Categorias Predefinidas

El portal incluye las siguientes categorias:

- `precio-transferencia` - Precio de transferencia
- `auditoria` - Auditoria
- `administracion` - Administracion
- `general` - General
- `otros` - Otros

---

## 3. Agregar Servicios/Aplicaciones

Cada aplicacion se define en el array `apps` con la siguiente estructura:

```json
{
  "id": "mi-aplicacion",
  "name": "Mi Aplicacion",
  "name_en": "My Application",
  "description": "Descripcion detallada de la aplicacion...",
  "category": "precio-transferencia",
  "url": "/mi-app/",
  "icon": "bar-chart-2",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo de Desarrollo",
  "tags": ["etiqueta1", "etiqueta2"],
  "port": 8080
}
```

### Campos de una Aplicacion

| Campo | Requerido | Descripcion | Ejemplo |
|-------|-----------|-------------|---------|
| `id` | Si | Identificador unico | `"mi-app"` |
| `name` | Si | Nombre en espanol | `"Mi Aplicacion"` |
| `name_en` | No | Nombre en ingles | `"My Application"` |
| `description` | Si | Descripcion detallada | `"Esta aplicacion..."` |
| `category` | Si | ID de la categoria | `"auditoria"` |
| `url` | Si | Ruta de acceso | `"/mi-app/"` |
| `icon` | Si | Nombre del icono de Lucide | `"file-text"` |
| `enabled` | No | Activar/desactivar (default: true) | `true` |
| `version` | No | Version de la aplicacion | `"1.0.0"` |
| `maintainer` | No | Responsable del servicio | `"Equipo X"` |
| `tags` | No | Etiquetas para filtrado | `["api", "web"]` |
| `port` | No | Puerto del servicio | `8080` |

### Ejemplo: Agregar una Nueva Aplicacion

Para agregar una aplicacion de auditoria:

```json
{
  "id": "auditoria-automatizada",
  "name": "Auditoria Automatizada",
  "name_en": "Automated Audit",
  "description": "Sistema de auditoria automatizada para revision de documentos y cumplimiento normativo.",
  "category": "auditoria",
  "url": "/auditoria/",
  "icon": "clipboard-check",
  "enabled": true,
  "version": "1.0.0",
  "maintainer": "Equipo de Auditoria",
  "tags": ["auditoria", "cumplimiento", "automatizacion"],
  "port": 8502
}
```

---

## 4. Iconos Disponibles (Lucide Icons)

El portal utiliza la biblioteca **Lucide Icons**. A continuacion se presenta una lista de iconos recomendados organizados por categoria:

### Iconos de Graficos y Analisis

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `bar-chart` | Grafico de barras |
| `bar-chart-2` | Grafico de barras horizontal |
| `bar-chart-3` | Grafico de barras con linea |
| `bar-chart-4` | Grafico de barras vertical |
| `line-chart` | Grafico de lineas |
| `pie-chart` | Grafico circular |
| `area-chart` | Grafico de area |
| `trending-up` | Tendencia al alza |
| `trending-down` | Tendencia a la baja |
| `activity` | Actividad/pulso |

### Iconos de Documentos y Archivos

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `file` | Archivo generico |
| `file-text` | Documento de texto |
| `file-spreadsheet` | Hoja de calculo |
| `file-chart` | Archivo con grafico |
| `file-check` | Archivo verificado |
| `file-search` | Busqueda de archivo |
| `files` | Multiples archivos |
| `folder` | Carpeta |
| `folder-open` | Carpeta abierta |
| `clipboard` | Portapapeles |
| `clipboard-check` | Portapapeles verificado |
| `clipboard-list` | Lista de tareas |

### Iconos de Finanzas y Negocios

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `calculator` | Calculadora |
| `coins` | Monedas |
| `credit-card` | Tarjeta de credito |
| `dollar-sign` | Signo de dolar |
| `euro` | Euro |
| `wallet` | Cartera |
| `receipt` | Recibo |
| `banknote` | Billete |
| `piggy-bank` | Alcancia |
| `landmark` | Banco/edificio financiero |
| `briefcase` | Maletin |
| `building` | Edificio |
| `building-2` | Edificio alternativo |

### Iconos de Usuarios y Personas

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `user` | Usuario individual |
| `users` | Grupo de usuarios |
| `user-check` | Usuario verificado |
| `user-plus` | Agregar usuario |
| `user-cog` | Configuracion de usuario |
| `contact` | Contacto |
| `contact-2` | Contacto alternativo |

### Iconos de Tecnologia y Desarrollo

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `code` | Codigo |
| `code-2` | Codigo alternativo |
| `terminal` | Terminal |
| `database` | Base de datos |
| `server` | Servidor |
| `cloud` | Nube |
| `cpu` | Procesador |
| `hard-drive` | Disco duro |
| `wifi` | Conexion wifi |
| `globe` | Globo/internet |
| `api` | API (no disponible, usar `zap`) |
| `zap` | Rayo/velocidad (recomendado para APIs) |

### Iconos de Interfaz y Navegacion

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `layout-dashboard` | Panel de control |
| `layout-grid` | Cuadricula |
| `layout-list` | Lista |
| `menu` | Menu |
| `home` | Inicio |
| `settings` | Configuracion |
| `settings-2` | Configuracion alternativa |
| `sliders` | Controles deslizantes |
| `search` | Busqueda |
| `filter` | Filtro |

### Iconos de Estado y Acciones

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `check` | Verificado |
| `check-circle` | Circulo verificado |
| `check-square` | Cuadrado verificado |
| `x` | Cerrar/cancelar |
| `x-circle` | Circulo con X |
| `alert-circle` | Alerta circular |
| `alert-triangle` | Alerta triangular |
| `info` | Informacion |
| `help-circle` | Ayuda |
| `shield` | Escudo |
| `shield-check` | Escudo verificado |
| `lock` | Candado |
| `unlock` | Candado abierto |

### Iconos de Comunicacion

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `mail` | Correo |
| `message-square` | Mensaje |
| `message-circle` | Mensaje circular |
| `phone` | Telefono |
| `send` | Enviar |
| `share` | Compartir |
| `share-2` | Compartir alternativo |
| `link` | Enlace |
| `external-link` | Enlace externo |

### Iconos de Tiempo y Calendario

| Nombre del Icono | Descripcion |
|------------------|-------------|
| `calendar` | Calendario |
| `calendar-check` | Calendario con marca |
| `calendar-days` | Dias del calendario |
| `clock` | Reloj |
| `timer` | Temporizador |
| `history` | Historial |
| `refresh-cw` | Actualizar |

### Iconos Recomendados por Departamento

| Departamento | Iconos Sugeridos |
|--------------|------------------|
| Precio de Transferencia | `calculator`, `file-spreadsheet`, `trending-up` |
| Auditoria | `clipboard-check`, `file-search`, `shield-check` |
| Administracion | `building-2`, `briefcase`, `settings` |
| Recursos Humanos | `users`, `user-check`, `contact` |
| Tecnologia | `server`, `database`, `code` |
| Finanzas | `coins`, `banknote`, `landmark` |
| Legal | `scale`, `file-text`, `shield` |
| General | `briefcase`, `layout-dashboard`, `grid` |

---

## 5. Referencia Completa de Iconos

Para ver la lista completa de iconos disponibles, visita:

**https://lucide.dev/icons/**

En esta pagina puedes:
- Buscar iconos por nombre
- Ver la vista previa de cada icono
- Copiar el nombre del icono directamente

---

## 6. Ejemplo de Configuracion Completa

```json
{
  "portal_name": "Forvis Mazars",
  "portal_description": "Portal de Acceso Unificado para las herramientas de automatizacion",
  "server_ip": "80.225.186.223",
  "categories": [
    {
      "id": "precio-transferencia",
      "name": "Precio de transferencia",
      "icon": "calculator",
      "description": "Herramientas para el area de Precio de Transferencia"
    },
    {
      "id": "auditoria",
      "name": "Auditoria",
      "icon": "clipboard-check",
      "description": "Herramientas para el area de Auditoria"
    }
  ],
  "apps": [
    {
      "id": "informept-streamlit",
      "name": "InformePT Streamlit",
      "description": "Aplicacion web interactiva...",
      "category": "precio-transferencia",
      "url": "/app/",
      "icon": "bar-chart-2",
      "enabled": true,
      "tags": ["streamlit", "web"]
    },
    {
      "id": "auditoria-app",
      "name": "Auditoria App",
      "description": "Sistema de auditoria...",
      "category": "auditoria",
      "url": "/auditoria/",
      "icon": "clipboard-check",
      "enabled": true,
      "tags": ["auditoria"]
    }
  ]
}
```

---

## 7. Notas Importantes

1. **Reinicio del Servicio**: Despues de modificar `apps_config.json`, es necesario reiniciar el servicio del portal para que los cambios surtan efecto.

2. **Validacion JSON**: Asegurate de que el archivo JSON sea valido. Puedes usar herramientas como [JSONLint](https://jsonlint.com/) para validar la sintaxis.

3. **IDs Unicos**: Los campos `id` tanto de categorias como de aplicaciones deben ser unicos y no contener espacios ni caracteres especiales.

4. **Categorias Vacias**: Las categorias sin aplicaciones asignadas no se mostraran en la interfaz automaticamente.

5. **Pagina de Respaldo**: Si necesitas modificar la pagina estatica de respaldo, edita tambien el archivo `static/index.html`.

---

## 8. Soporte

Para consultas adicionales o soporte tecnico, contacta al equipo de desarrollo.
