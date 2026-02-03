# API: User Context

**Endpoint**: `/api/user/context/`  
**Método**: `GET`  
**Autenticación**: Requerida

---

## 📋 Descripción

Este endpoint devuelve el contexto completo del usuario para el frontend, incluyendo información del usuario, permisos evaluados mediante ABAC y configuración de UI según el rol.

---

## 🔌 Request

### Headers
```
Authorization: Session (cookie-based)
Accept: application/json
```

### Ejemplo
```bash
curl -X GET http://localhost:8000/api/user/context/ \
  -H "Accept: application/json" \
  --cookie "sessionid=..."
```

---

## 📤 Response

### Estructura
```json
{
  "user": {
    "username": "pm",
    "email": "pm@example.com",
    "first_name": "Project",
    "last_name": "Manager"
  },
  "profile": {
    "role": "pm",
    "department": "IT",
    "location": "Ciudad de México",
    "company": {
      "id": "uuid-del-company",
      "name": "Mi Empresa"
    }
  },
  "permissions": {
    "dashboard.view": true,
    "dashboard.trends.view": true,
    "dashboard.export": true,
    "projects.create": true,
    "projects.edit": true,
    "projects.view": true,
    "reports.create": true,
    "reports.approve": true,
    "reports.view": true,
    "wizard.save": true,
    "wizard.submit": true,
    "wizard.view": true,
    "documents.generate": true,
    "documents.download": true,
    "roi.view": true,
    "roi.export": true
  },
  "ui_config": {
    "navigation": ["dashboard", "projects", "reports", "documents"],
    "dashboard_sections": [
      "kpis",
      "alerts",
      "comparatives",
      "trends",
      "roi",
      "projects",
      "reports"
    ],
    "wizard_mode": "full",
    "can_create_projects": true,
    "can_approve_reports": true,
    "can_edit_projects": true,
    "can_use_field_mode": false,
    "can_use_ai_chat": true,
    "can_generate_pdf": true
  }
}
```

---

## 📝 Campos

### `user`
Información básica del usuario autenticado.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `username` | string | Nombre de usuario |
| `email` | string | Email del usuario |
| `first_name` | string | Nombre |
| `last_name` | string | Apellido |

### `profile`
Información del perfil del usuario.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `role` | string | Rol del usuario (`admin_empresa`, `pm`, `supervisor`, `tecnico`, `cliente`) |
| `department` | string | Departamento |
| `location` | string | Ubicación |
| `company` | object\|null | Información de la compañía |

### `permissions`
Permisos del usuario evaluados mediante ABAC.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `dashboard.view` | boolean | Puede ver dashboard |
| `dashboard.trends.view` | boolean | Puede ver tendencias |
| `dashboard.export` | boolean | Puede exportar datos |
| `projects.create` | boolean | Puede crear proyectos |
| `projects.edit` | boolean | Puede editar proyectos |
| `projects.view` | boolean | Puede ver proyectos |
| `reports.create` | boolean | Puede crear reportes |
| `reports.approve` | boolean | Puede aprobar reportes |
| `reports.view` | boolean | Puede ver reportes |
| `wizard.save` | boolean | Puede guardar wizard |
| `wizard.submit` | boolean | Puede enviar wizard |
| `wizard.view` | boolean | Puede ver wizard |
| `documents.generate` | boolean | Puede generar documentos |
| `documents.download` | boolean | Puede descargar documentos |
| `roi.view` | boolean | Puede ver ROI |
| `roi.export` | boolean | Puede exportar ROI |

### `ui_config`
Configuración de UI según el rol del usuario.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `navigation` | array | Elementos de navegación permitidos |
| `dashboard_sections` | array | Secciones de dashboard visibles |
| `wizard_mode` | string | Modo del wizard (`full` o `readonly`) |
| `can_create_projects` | boolean | Puede crear proyectos |
| `can_approve_reports` | boolean | Puede aprobar reportes |
| `can_edit_projects` | boolean | Puede editar proyectos |
| `can_use_field_mode` | boolean | Puede usar modo campo |
| `can_use_ai_chat` | boolean | Puede usar chatbot IA |
| `can_generate_pdf` | boolean | Puede generar PDFs |

---

## 🔄 Códigos de Estado

| Código | Descripción |
|--------|-------------|
| `200` | OK - Contexto devuelto correctamente |
| `401` | Unauthorized - Usuario no autenticado |
| `404` | Not Found - Usuario sin perfil |

---

## 💡 Ejemplos de Uso

### JavaScript
```javascript
// Obtener contexto del usuario
const response = await fetch('/api/user/context/', {
  credentials: 'include'
});
const context = await response.json();

// Verificar permiso
if (context.permissions['projects.create']) {
  // Mostrar botón de crear proyecto
}

// Verificar sección de dashboard
if (context.ui_config.dashboard_sections.includes('roi')) {
  // Mostrar sección ROI
}
```

### Python (Django Template)
```python
# El contexto está disponible en request.user_context
# gracias al middleware UserContextMiddleware
```

---

## 🔗 Relacionado

- `docs/FASE1_IMPLEMENTACION_COMPLETA.md` - Documentación de implementación
- `backend/apps/accounts/views.py` - Código fuente del endpoint
- `backend/apps/accounts/services.py` - Lógica de permisos y UI config

---

**Última actualización**: 2026-01-23
