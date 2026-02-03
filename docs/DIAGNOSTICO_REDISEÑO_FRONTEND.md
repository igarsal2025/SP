# Diagnóstico y Planeación: Rediseño Frontend SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: 📋 Diagnóstico y Planeación

---

## 📋 Resumen Ejecutivo

El frontend actual de SITEC presenta un problema crítico de **usabilidad y organización**: todos los componentes y funcionalidades se muestran en una sola pantalla sin diferenciación por perfil de usuario, lo que genera:

- **Sobrecarga cognitiva**: Demasiada información visible simultáneamente
- **Confusión de roles**: Todos los usuarios ven las mismas opciones
- **Falta de personalización**: No se adapta a las necesidades específicas de cada perfil
- **Mala experiencia de usuario**: Navegación poco intuitiva y desorganizada

Este documento presenta un diagnóstico completo y una propuesta de rediseño estructurada por fases.

---

## 🔍 Diagnóstico del Problema Actual

### 1. Estado Actual del Frontend

#### Dashboard (`dashboard.html`)
**Problema**: Muestra **8 paneles diferentes** en una sola vista, sin filtrado por perfil:

1. KPIs principales (con filtros avanzados)
2. Alertas
3. Comparativos
4. Tendencias Históricas
5. Histórico de snapshots
6. Histórico agregado (mensual)
7. KPIs ROI
8. Proyectos recientes
9. Reportes recientes

**Impacto**:
- ❌ Un técnico ve información de ROI y gestión que no le corresponde
- ❌ Un cliente ve opciones de edición y gestión que no puede usar
- ❌ Un PM ve información técnica operativa que no necesita en su vista principal
- ❌ Todos los usuarios deben hacer scroll extenso para encontrar lo relevante

#### Wizard (`wizard.html`)
**Problema**: Muestra todos los componentes avanzados y opciones sin considerar el perfil:

- Chatbot IA (visible para todos)
- Componentes avanzados (risk-matrix, gantt-lite, kanban)
- Generación de PDF (visible para todos)
- Modo campo (visible para todos)

**Impacto**:
- ❌ Un cliente no debería ver opciones de edición
- ❌ Un técnico no necesita ver todos los componentes avanzados simultáneamente
- ❌ Falta diferenciación visual entre roles

### 2. Perfiles de Usuario y Necesidades

#### `admin_empresa` (Administrador de Empresa)
**Necesidades**:
- ✅ Acceso completo a todas las funcionalidades
- ✅ Dashboard gerencial completo (KPIs, ROI, tendencias)
- ✅ Gestión de proyectos y reportes
- ✅ Configuración y administración
- ✅ Vista consolidada de toda la empresa

**No necesita ver**:
- N/A (acceso completo)

#### `pm` (Project Manager)
**Necesidades**:
- ✅ Dashboard gerencial (KPIs, ROI, comparativos, tendencias)
- ✅ Gestión de proyectos (crear, editar, asignar)
- ✅ Aprobación de reportes
- ✅ Análisis de ROI y métricas de negocio
- ✅ Vista de proyectos asignados y estado general

**No necesita ver**:
- ❌ Detalles técnicos operativos del wizard
- ❌ Componentes avanzados de validación técnica
- ❌ Modo campo (es para técnicos en sitio)

#### `supervisor` (Supervisor)
**Necesidades**:
- ✅ Aprobación de reportes y documentos
- ✅ Supervisión de proyectos asignados
- ✅ Vista de reportes pendientes de aprobación
- ✅ Alertas y notificaciones
- ✅ Dashboard básico (solo proyectos supervisados)

**No necesita ver**:
- ❌ KPIs ROI avanzados
- ❌ Tendencias históricas completas
- ❌ Gestión completa de proyectos
- ❌ Componentes técnicos del wizard

#### `tecnico` (Técnico)
**Necesidades**:
- ✅ Wizard completo para reportes
- ✅ Modo campo (para trabajo en sitio)
- ✅ Creación y edición de reportes
- ✅ Vista de proyectos asignados
- ✅ Dashboard básico (solo sus proyectos)

**No necesita ver**:
- ❌ KPIs ROI gerenciales
- ❌ Tendencias históricas completas
- ❌ Gestión de proyectos (solo lectura de asignados)
- ❌ Aprobaciones (solo puede enviar)

#### `cliente` (Cliente)
**Necesidades**:
- ✅ Vista de proyectos (solo lectura)
- ✅ Descarga de documentos y reportes aprobados
- ✅ Dashboard básico (solo sus proyectos)
- ✅ Estado de proyectos y reportes

**No necesita ver**:
- ❌ Opciones de edición
- ❌ Wizard completo (solo puede ver reportes finales)
- ❌ KPIs internos
- ❌ Gestión de proyectos
- ❌ Aprobaciones

### 3. Análisis de Permisos ABAC Actuales

Según `seed_sitec.py` y `GUIA_CONFIGURACION_ABAC.md`:

| Acción | admin_empresa | pm | supervisor | tecnico | cliente |
|--------|---------------|----|-----------|---------|---------|
| `dashboard.*` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `wizard.*` | ✅ | ✅ | ✅ | ✅ | ✅ (solo GET) |
| `wizard.save` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `wizard.submit` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `reports.*` | ✅ | ✅ | ✅ | ✅ | ✅ (solo GET) |
| `reports.approve` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `projects.*` | ✅ | ✅ | ✅ | ✅ (solo GET) | ✅ (solo GET) |
| `projects.create` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `roi.*` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `documents.download` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Problema identificado**: Los permisos ABAC están bien definidos en el backend, pero **el frontend no los respeta** y muestra todo a todos.

---

## 🎯 Propuesta de Rediseño

### Objetivos Principales

1. **Personalización por perfil**: Cada usuario ve solo lo que necesita
2. **Navegación intuitiva**: Sistema de pestañas/secciones organizadas
3. **Mejor UX**: Reducción de carga cognitiva y mejora de usabilidad
4. **Modularidad**: Componentes reutilizables y configurables
5. **Responsive**: Adaptable a diferentes tamaños de pantalla

### Arquitectura Propuesta

#### 1. Sistema de Navegación Principal

```
┌─────────────────────────────────────────┐
│  SITEC  [Perfil: PM]  [Sync: Online]   │  ← Header
├─────────────────────────────────────────┤
│  [Dashboard] [Proyectos] [Reportes]    │  ← Navegación principal
│  [Documentos] [Configuración]           │     (visible según perfil)
├─────────────────────────────────────────┤
│                                         │
│         Contenido dinámico              │
│         (según sección seleccionada)    │
│                                         │
└─────────────────────────────────────────┘
```

#### 2. Estructura de Vistas por Perfil

##### `admin_empresa` - Vista Completa
```
Navegación: [Dashboard] [Proyectos] [Reportes] [Documentos] [Configuración] [Usuarios]
```

##### `pm` - Vista Gerencial
```
Navegación: [Dashboard] [Proyectos] [Reportes] [Documentos]
```

##### `supervisor` - Vista Supervisión
```
Navegación: [Dashboard] [Proyectos] [Reportes] [Aprobaciones]
```

##### `tecnico` - Vista Operativa
```
Navegación: [Wizard] [Mis Proyectos] [Mis Reportes] [Documentos]
```

##### `cliente` - Vista Lectura
```
Navegación: [Mis Proyectos] [Documentos]
```

### 3. Componentes Modulares Propuestos

#### Dashboard Personalizado
- **admin_empresa/pm**: Dashboard completo (KPIs, ROI, tendencias, comparativos)
- **supervisor**: Dashboard básico (proyectos supervisados, alertas, reportes pendientes)
- **tecnico**: Dashboard operativo (proyectos asignados, reportes recientes, tareas)
- **cliente**: Dashboard cliente (estado de proyectos, documentos disponibles)

#### Wizard Contextual
- **tecnico/supervisor/pm**: Wizard completo con todas las opciones
- **cliente**: Vista de solo lectura del wizard (sin opciones de edición)

#### Gestión de Proyectos
- **admin_empresa/pm**: CRUD completo
- **supervisor**: Vista y edición limitada
- **tecnico/cliente**: Solo lectura

---

## 📐 Diseño Técnico

### 1. Estructura de Archivos Propuesta

```
backend/apps/frontend/
├── templates/frontend/
│   ├── base.html                    # Base común
│   ├── dashboard/
│   │   ├── admin.html               # Dashboard admin
│   │   ├── pm.html                  # Dashboard PM
│   │   ├── supervisor.html          # Dashboard supervisor
│   │   ├── tecnico.html             # Dashboard técnico
│   │   └── cliente.html             # Dashboard cliente
│   ├── wizard/
│   │   ├── wizard_full.html         # Wizard completo
│   │   └── wizard_readonly.html      # Wizard solo lectura
│   ├── projects/
│   │   ├── list.html                # Lista de proyectos
│   │   ├── detail.html              # Detalle de proyecto
│   │   └── create.html              # Crear proyecto (solo PM/admin)
│   ├── reports/
│   │   ├── list.html                # Lista de reportes
│   │   ├── detail.html              # Detalle de reporte
│   │   └── approvals.html           # Aprobaciones (supervisor/pm)
│   └── documents/
│       └── list.html                # Lista de documentos
├── views.py                          # Vistas principales
└── utils.py                          # Utilidades (get_user_dashboard, etc.)

backend/static/frontend/js/
├── navigation.js                     # Sistema de navegación
├── role-based-ui.js                  # Lógica de UI por rol
├── dashboard/
│   ├── dashboard-admin.js
│   ├── dashboard-pm.js
│   ├── dashboard-supervisor.js
│   ├── dashboard-tecnico.js
│   └── dashboard-cliente.js
└── components/
    └── role-aware-component.js      # Componente base con lógica de roles
```

### 2. API de Contexto de Usuario

**Nuevo endpoint**: `/api/user/context/`

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

### 3. Middleware de Contexto Frontend

```python
# backend/apps/frontend/middleware.py
def user_context_middleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            profile = UserProfile.objects.select_related('company').get(user=request.user)
            request.user_context = {
                'role': profile.role,
                'permissions': get_user_permissions(request),
                'ui_config': get_ui_config(profile.role)
            }
        return get_response(request)
    return middleware
```

### 4. Template Tags Personalizados

```python
# backend/apps/frontend/templatetags/role_tags.py
@register.simple_tag
def show_for_role(user_role, allowed_roles):
    return user_role in allowed_roles.split(',')

@register.inclusion_tag('frontend/components/dashboard_section.html')
def dashboard_section(section_name, user_role):
    return {
        'section_name': section_name,
        'visible': is_section_visible(section_name, user_role)
    }
```

---

## 🗺️ Plan de Implementación

### Fase 1: Preparación y Base (Semana 1)

**Objetivo**: Establecer la infraestructura base sin romper funcionalidad existente.

#### Tareas:
1. ✅ Crear endpoint `/api/user/context/` para obtener contexto del usuario
2. ✅ Crear middleware de contexto frontend
3. ✅ Crear template tags para condicionales por rol
4. ✅ Crear archivo `role-based-ui.js` base
5. ✅ Crear sistema de navegación básico (`navigation.js`)
6. ✅ Tests unitarios para contexto de usuario

**Criterios de éxito**:
- Endpoint devuelve contexto correcto por rol
- Template tags funcionan correctamente
- No se rompe funcionalidad existente

**Riesgos**:
- ⚠️ Cambios en `base.html` pueden afectar todas las vistas
- ⚠️ Necesidad de mantener compatibilidad con código existente

**Mitigación**:
- Implementar cambios de forma incremental
- Mantener vistas antiguas funcionando en paralelo
- Feature flags para activar/desactivar nuevo sistema

### Fase 2: Dashboard Personalizado (Semana 2)

**Objetivo**: Implementar dashboards específicos por perfil.

#### Tareas:
1. Crear templates de dashboard por rol:
   - `dashboard/admin.html` (completo)
   - `dashboard/pm.html` (gerencial)
   - `dashboard/supervisor.html` (supervisión)
   - `dashboard/tecnico.html` (operativo)
   - `dashboard/cliente.html` (lectura)
2. Crear JavaScript específico por dashboard
3. Implementar lógica de redirección según rol
4. Migrar componentes existentes a nuevos templates
5. Tests de integración para cada dashboard

**Criterios de éxito**:
- Cada perfil ve solo sus secciones relevantes
- KPIs y métricas se filtran correctamente
- No hay regresiones en funcionalidad

**Riesgos**:
- ⚠️ Duplicación de código entre dashboards
- ⚠️ Mantenimiento de múltiples versiones

**Mitigación**:
- Usar componentes reutilizables
- Extraer lógica común a funciones compartidas
- Documentar diferencias entre dashboards

### Fase 3: Navegación y Estructura (Semana 3)

**Objetivo**: Implementar sistema de navegación principal y estructura modular.

#### Tareas:
1. Actualizar `base.html` con navegación principal
2. Implementar sistema de rutas frontend
3. Crear vistas para cada sección (Proyectos, Reportes, Documentos)
4. Implementar lógica de visibilidad de navegación por rol
5. Migrar contenido de `dashboard.html` actual a estructura modular
6. Tests E2E para flujos de navegación

**Criterios de éxito**:
- Navegación funciona correctamente
- Cada rol ve solo sus secciones
- Transiciones entre secciones son fluidas

**Riesgos**:
- ⚠️ Cambios en URLs pueden romper bookmarks
- ⚠️ Navegación puede ser confusa si no está bien diseñada

**Mitigación**:
- Mantener URLs antiguas con redirects
- Realizar pruebas de usabilidad
- Documentar nueva estructura de navegación

### Fase 4: Wizard Contextual (Semana 4)

**Objetivo**: Adaptar wizard según perfil de usuario.

#### Tareas:
1. Crear `wizard/wizard_readonly.html` para clientes
2. Implementar lógica de visibilidad de componentes en wizard
3. Adaptar `wizard.js` para respetar permisos
4. Ocultar/mostrar componentes según rol (chatbot, modo campo, etc.)
5. Tests para wizard por rol

**Criterios de éxito**:
- Clientes ven wizard en modo solo lectura
- Técnicos ven todas las opciones operativas
- No se muestran opciones sin permisos

**Riesgos**:
- ⚠️ Wizard es complejo y tiene muchas dependencias
- ⚠️ Cambios pueden afectar flujo de trabajo existente

**Mitigación**:
- Implementar cambios de forma conservadora
- Mantener funcionalidad existente como fallback
- Pruebas exhaustivas con usuarios reales

### Fase 5: Optimización y Refinamiento (Semana 5)

**Objetivo**: Pulir detalles, optimizar rendimiento y documentar.

#### Tareas:
1. Optimizar carga de componentes (lazy loading)
2. Mejorar responsive design
3. Agregar animaciones y transiciones suaves
4. Documentar nueva estructura
5. Crear guía de usuario por perfil
6. Tests de rendimiento
7. Validación final con usuarios

**Criterios de éxito**:
- Rendimiento igual o mejor que antes
- Documentación completa
- Usuarios validan positivamente

**Riesgos**:
- ⚠️ Optimizaciones pueden introducir bugs
- ⚠️ Cambios de último minuto pueden desestabilizar

**Mitigación**:
- Optimizaciones incrementales
- Freeze de features antes de release
- Plan de rollback

---

## 🧪 Estrategia de Testing

### Tests Unitarios
- Contexto de usuario por rol
- Template tags
- Funciones de visibilidad de UI
- Lógica de navegación

### Tests de Integración
- Renderizado de dashboards por rol
- Navegación entre secciones
- Filtrado de contenido por permisos

### Tests E2E
- Flujo completo por perfil:
  - Admin: Dashboard → Proyectos → Reportes → Configuración
  - PM: Dashboard → Proyectos → Reportes
  - Supervisor: Dashboard → Aprobaciones
  - Técnico: Wizard → Mis Proyectos → Mis Reportes
  - Cliente: Mis Proyectos → Documentos

### Tests de Usabilidad
- Sesiones con usuarios reales de cada perfil
- Feedback sobre navegación y organización
- Ajustes basados en feedback

---

## 📊 Métricas de Éxito

### Métricas Cuantitativas
- **Reducción de tiempo de carga**: < 2s para dashboard
- **Reducción de scroll**: 70% menos scroll necesario
- **Tasa de error**: < 1% de errores relacionados con permisos
- **Cobertura de tests**: > 80%

### Métricas Cualitativas
- **Satisfacción de usuario**: Encuesta post-implementación
- **Facilidad de uso**: Reducción de tickets de soporte
- **Adopción**: % de usuarios que usan nuevas funcionalidades

---

## ⚠️ Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper funcionalidad existente | Media | Alto | Implementación incremental, feature flags, tests exhaustivos |
| Duplicación de código | Alta | Medio | Componentes reutilizables, extracción de lógica común |
| Confusión de usuarios | Media | Medio | Documentación, guías, sesiones de entrenamiento |
| Performance degradado | Baja | Alto | Optimizaciones, lazy loading, caching |
| Cambios en URLs rompen bookmarks | Media | Bajo | Redirects, mantener URLs antiguas temporalmente |

---

## 📚 Documentación Requerida

1. **Guía de Usuario por Perfil**
   - `docs/GUIA_USUARIO_ADMIN.md`
   - `docs/GUIA_USUARIO_PM.md`
   - `docs/GUIA_USUARIO_SUPERVISOR.md`
   - `docs/GUIA_USUARIO_TECNICO.md`
   - `docs/GUIA_USUARIO_CLIENTE.md`

2. **Documentación Técnica**
   - `docs/ARQUITECTURA_FRONTEND.md`
   - `docs/COMPONENTES_REUTILIZABLES.md`
   - `docs/NAVEGACION_ROLES.md`

3. **Changelog**
   - `docs/CHANGELOG_REDISEÑO_FRONTEND.md`

---

## ✅ Checklist de Validación

### Pre-Implementación
- [ ] Revisión y aprobación del diseño
- [ ] Validación de permisos ABAC
- [ ] Definición de componentes reutilizables
- [ ] Plan de migración de datos (si aplica)

### Durante Implementación
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Tests E2E pasando
- [ ] Code review completado
- [ ] Documentación actualizada

### Post-Implementación
- [ ] Validación con usuarios reales
- [ ] Performance validado
- [ ] Documentación de usuario completa
- [ ] Plan de rollback probado
- [ ] Monitoreo de errores configurado

---

## 🎯 Próximos Pasos Inmediatos

1. **Revisar y aprobar este documento** con el equipo
2. **Priorizar fases** según necesidades del negocio
3. **Asignar recursos** para implementación
4. **Crear issues/tickets** en sistema de gestión de proyectos
5. **Iniciar Fase 1** (Preparación y Base)

---

**Última actualización**: 2026-01-23  
**Autor**: Sistema de Diagnóstico SITEC  
**Estado**: 📋 Pendiente de Aprobación
