# Referencia Rápida: Rediseño Frontend SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 🎯 Mapa de Navegación por Perfil

### `admin_empresa` (Administrador)
```
[Dashboard] [Proyectos] [Reportes] [Documentos] [Configuración] [Usuarios]
     ↓           ↓          ↓           ↓              ↓            ↓
  Completo    CRUD      Todos      Todos         Admin        Gestión
```

### `pm` (Project Manager)
```
[Dashboard] [Proyectos] [Reportes] [Documentos]
     ↓           ↓          ↓           ↓
  Gerencial    CRUD      Aprobación  Descarga
```

### `supervisor` (Supervisor)
```
[Dashboard] [Proyectos] [Reportes] [Aprobaciones]
     ↓           ↓          ↓            ↓
   Básico     Vista      Vista      Pendientes
```

### `tecnico` (Técnico)
```
[Wizard] [Mis Proyectos] [Mis Reportes] [Documentos]
   ↓           ↓              ↓             ↓
 Completo    Asignados    Recientes     Descarga
```

### `cliente` (Cliente)
```
[Mis Proyectos] [Documentos]
       ↓             ↓
    Solo Lectura  Descarga
```

---

## 📋 Contenido de Dashboard por Perfil

### `admin_empresa` - Dashboard Completo
- ✅ KPIs principales (todos)
- ✅ Alertas (todas)
- ✅ Comparativos (completos)
- ✅ Tendencias históricas (completas)
- ✅ Histórico de snapshots
- ✅ Histórico agregado mensual
- ✅ KPIs ROI (completos)
- ✅ Proyectos recientes (todos)
- ✅ Reportes recientes (todos)
- ✅ Configuración y administración

### `pm` - Dashboard Gerencial
- ✅ KPIs principales (filtrados por proyectos asignados)
- ✅ Alertas (relevantes)
- ✅ Comparativos (completos)
- ✅ Tendencias históricas (completas)
- ✅ KPIs ROI (completos)
- ✅ Proyectos recientes (asignados)
- ✅ Reportes recientes (asignados)
- ❌ Configuración de sistema

### `supervisor` - Dashboard Supervisión
- ✅ Proyectos supervisados (lista)
- ✅ Alertas (proyectos supervisados)
- ✅ Reportes pendientes de aprobación
- ✅ Estado de proyectos
- ❌ KPIs ROI
- ❌ Tendencias históricas completas

### `tecnico` - Dashboard Operativo
- ✅ Proyectos asignados (lista)
- ✅ Tareas pendientes
- ✅ Reportes recientes (propios)
- ✅ Estado de proyectos asignados
- ❌ KPIs ROI
- ❌ Tendencias históricas
- ❌ Comparativos gerenciales

### `cliente` - Dashboard Cliente
- ✅ Estado de proyectos (solo lectura)
- ✅ Documentos disponibles (descarga)
- ✅ Reportes aprobados (vista)
- ❌ Todas las demás secciones

---

## 🔐 Matriz de Permisos Frontend

| Funcionalidad | admin | pm | supervisor | tecnico | cliente |
|---------------|-------|----|-----------|---------|---------|
| **Dashboard Completo** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Dashboard Básico** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **KPIs ROI** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Tendencias Históricas** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Crear Proyectos** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Editar Proyectos** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Ver Proyectos** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Wizard Completo** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Wizard Solo Lectura** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Guardar Wizard** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Enviar Wizard** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Aprobar Reportes** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Modo Campo** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Chatbot IA** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Generar PDF** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Descargar Documentos** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Configuración** | ✅ | ❌ | ❌ | ❌ | ❌ |

**Leyenda**:
- ✅ Permitido
- ❌ No permitido
- ⚠️ Limitado (solo proyectos supervisados)

---

## 📁 Estructura de Archivos Propuesta

```
backend/apps/frontend/
├── templates/frontend/
│   ├── base.html
│   ├── dashboard/
│   │   ├── admin.html
│   │   ├── pm.html
│   │   ├── supervisor.html
│   │   ├── tecnico.html
│   │   └── cliente.html
│   ├── wizard/
│   │   ├── wizard_full.html
│   │   └── wizard_readonly.html
│   ├── projects/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── create.html
│   ├── reports/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── approvals.html
│   └── documents/
│       └── list.html
├── templatetags/
│   └── role_tags.py
├── middleware.py
└── views.py

backend/static/frontend/js/
├── role-based-ui.js
├── navigation.js
├── routing.js (opcional)
├── dashboard/
│   ├── dashboard-admin.js
│   ├── dashboard-pm.js
│   ├── dashboard-supervisor.js
│   ├── dashboard-tecnico.js
│   └── dashboard-cliente.js
└── components/
    └── role-aware-component.js
```

---

## 🔌 API Endpoints Necesarios

### Nuevo Endpoint: `/api/user/context/`
**Método**: `GET`  
**Autenticación**: Requerida  
**Respuesta**:
```json
{
  "user": {
    "username": "pm",
    "role": "pm",
    "company": "Company Name"
  },
  "permissions": {
    "dashboard.view": true,
    "dashboard.trends.view": true,
    "projects.create": true,
    "reports.approve": true,
    "wizard.save": true
  },
  "ui_config": {
    "navigation": ["dashboard", "projects", "reports", "documents"],
    "dashboard_sections": ["kpis", "roi", "trends", "comparatives"],
    "wizard_mode": "full"
  }
}
```

---

## 🎨 Template Tags Disponibles

### `show_for_role`
```django
{% show_for_role user.profile.role "pm,admin_empresa" %}
  <!-- Contenido visible solo para PM y Admin -->
{% endshow_for_role %}
```

### `dashboard_section`
```django
{% dashboard_section "roi" user.profile.role %}
  <!-- Sección ROI solo si está permitida -->
{% enddashboard_section %}
```

### `has_permission`
```django
{% has_permission "projects.create" %}
  <button>Crear Proyecto</button>
{% endhas_permission %}
```

---

## 🚀 Orden de Implementación Recomendado

1. **Fase 1**: Infraestructura (endpoint, middleware, template tags)
2. **Fase 2**: Dashboards personalizados
3. **Fase 3**: Navegación y estructura
4. **Fase 4**: Wizard contextual
5. **Fase 5**: Optimización y refinamiento

---

## ⚠️ Puntos de Atención

### Compatibilidad
- Mantener URLs antiguas funcionando
- No romper funcionalidad existente
- Feature flags para activar/desactivar

### Performance
- Lazy loading de componentes pesados
- Caching de contexto de usuario
- Minimizar requests al servidor

### Testing
- Tests unitarios para cada componente
- Tests de integración por perfil
- Tests E2E para flujos completos

---

## 📞 Referencias Rápidas

- **Diagnóstico completo**: `docs/DIAGNOSTICO_REDISEÑO_FRONTEND.md`
- **Plan de acción**: `docs/PLAN_ACCION_REDISEÑO_FRONTEND.md`
- **Permisos ABAC**: `docs/GUIA_CONFIGURACION_ABAC.md`
- **Roles y perfiles**: `backend/apps/accounts/models.py`

---

**Última actualización**: 2026-01-23
