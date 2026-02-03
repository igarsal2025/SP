# Arquitectura Frontend - SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📋 Resumen

Este documento describe la arquitectura del frontend del sistema SITEC después del rediseño, incluyendo componentes, navegación, permisos y optimizaciones.

---

## 🏗️ Arquitectura General

### Capas del Sistema

```
┌─────────────────────────────────────┐
│   Templates (Django)                │
│   - Base templates                  │
│   - Templates por rol               │
│   - Template tags                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   JavaScript Modules                │
│   - Lazy loading                    │
│   - Role-based UI                   │
│   - Navigation                      │
│   - Data loading optimizado         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   CSS                                │
│   - Tokens (variables)              │
│   - Components                      │
│   - Animations                      │
│   - Responsive                      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Backend APIs                      │
│   - /api/user/context/              │
│   - /api/projects/                 │
│   - /api/reports/                   │
│   - /api/dashboard/                │
└─────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

### Templates

```
backend/apps/frontend/templates/frontend/
├── base.html                          # Template base
├── dashboard/
│   ├── admin.html                     # Dashboard para admin
│   ├── pm.html                        # Dashboard para PM
│   ├── supervisor.html                # Dashboard para supervisor
│   ├── tecnico.html                   # Dashboard para técnico
│   └── cliente.html                   # Dashboard para cliente
├── wizard/
│   └── wizard_readonly.html            # Wizard readonly para clientes
├── wizard.html                        # Wizard completo
├── projects/
│   └── list.html                      # Lista de proyectos
├── reports/
│   ├── list.html                      # Lista de reportes
│   └── approvals.html                 # Aprobaciones
└── documents/
    └── list.html                      # Lista de documentos
```

### JavaScript

```
backend/static/frontend/js/
├── lazy-loader.js                     # Sistema de carga diferida
├── data-loader.js                     # Optimización de carga de datos
├── loading-states.js                   # Estados de carga y feedback
├── role-based-ui.js                   # Lógica de UI por rol
├── navigation.js                      # Gestión de navegación
├── performance.js                      # Monitoreo de performance
├── pwa.js                             # Funcionalidad PWA
├── sync.js                            # Sincronización offline
├── analytics.js                       # Analytics
├── permissions.js                     # Gestión de permisos
├── components.js                      # Componentes reutilizables
├── wizard.js                          # Lógica del wizard
├── dashboard.js                       # Dashboard completo
├── dashboard-lite.js                  # Dashboard ligero
├── sections-projects.js               # Sección de proyectos
├── sections-reports.js                # Sección de reportes
├── sections-approvals.js              # Sección de aprobaciones
└── sections-documents.js              # Sección de documentos
```

### CSS

```
backend/static/frontend/css/
├── tokens.css                         # Variables CSS
├── components.css                     # Componentes base
├── wizard.css                         # Estilos del wizard
├── animations.css                     # Animaciones y transiciones
└── responsive.css                     # Media queries y responsive
```

---

## 🔄 Flujo de Datos

### 1. Inicialización

```
Usuario accede a página
    ↓
Django renderiza template
    ↓
LazyLoader detecta página actual
    ↓
Carga solo módulos necesarios
    ↓
RoleBasedUI obtiene contexto del usuario
    ↓
Navigation inicializa según permisos
    ↓
Página lista
```

### 2. Carga de Datos

```
Usuario interactúa (click, filtro, etc.)
    ↓
DataLoader verifica caché
    ↓
Si hay caché válido → Retorna inmediatamente
    ↓
Si no hay caché → Fetch a API
    ↓
Guarda en caché
    ↓
Muestra datos con LoadingStates
```

### 3. Navegación

```
Usuario hace click en navegación
    ↓
NavigationManager verifica permisos
    ↓
Si tiene permiso → Navega
    ↓
Si no tiene permiso → Muestra error
```

---

## 🎯 Componentes Principales

### 1. LazyLoader

**Responsabilidad**: Cargar solo los módulos JavaScript necesarios según la página.

**Uso**:
```javascript
// Automático en base.html
// O manual:
await window.lazyLoader.loadModule("/static/frontend/js/mi-modulo.js");
```

### 2. DataLoader

**Responsabilidad**: Optimizar carga de datos con caché, debouncing y batching.

**Uso**:
```javascript
// Fetch con caché
const data = await window.dataLoader.fetchWithCache("/api/projects/", {
  cache: true,
  ttl: 60000
});
```

### 3. LoadingStates

**Responsabilidad**: Proporcionar feedback visual durante operaciones.

**Uso**:
```javascript
window.loadingStates.showSkeleton("#tabla", 5);
// ... carga datos ...
window.loadingStates.hideLoading("#tabla");
```

### 4. RoleBasedUI

**Responsabilidad**: Obtener y gestionar contexto del usuario.

**Uso**:
```javascript
const context = await window.RoleBasedUI.getUserContext();
const canEdit = context.permissions["projects.edit"];
```

### 5. NavigationManager

**Responsabilidad**: Gestionar navegación principal según permisos.

**Uso**:
```javascript
// Automático en base.html
// O manual:
window.NavigationManager.initialize();
```

---

## 🔐 Sistema de Permisos

### Permisos ABAC

Los permisos se evalúan en el backend mediante ABAC y se exponen al frontend a través de:
- `/api/user/context/` - Endpoint de contexto
- `request.user_context` - Middleware inyecta contexto
- Template tags - `{% has_permission %}`
- JavaScript - `window.RoleBasedUI.getUserContext()`

### Permisos Comunes

- `dashboard.view` - Ver dashboard
- `projects.create` - Crear proyectos
- `projects.edit` - Editar proyectos
- `projects.view` - Ver proyectos
- `reports.create` - Crear reportes
- `reports.approve` - Aprobar reportes
- `reports.view` - Ver reportes
- `wizard.save` - Guardar wizard
- `wizard.submit` - Enviar wizard
- `wizard.view` - Ver wizard

---

## 📱 Responsive Design

### Breakpoints

- **Móvil**: < 768px (1 columna)
- **Tablet**: 768px - 1023px (2 columnas)
- **Desktop**: 1024px+ (2-3 columnas)

### Optimizaciones Mobile

- Tamaños mínimos de 44px para touch
- Navegación vertical en móvil
- Tablas con scroll horizontal
- Botones apilados en wizard footer
- Grids adaptativos

---

## ⚡ Optimizaciones de Performance

### Lazy Loading

- Reduce carga inicial en ~40-50%
- Carga solo módulos necesarios por página
- Carga en paralelo cuando es posible

### Caching

- Caché de respuestas API con TTL
- Deduplicación de requests
- Limpieza automática de caché expirado

### Animaciones

- Transiciones suaves (0.2s - 0.3s)
- Respeta `prefers-reduced-motion`
- Animaciones CSS (no JavaScript)

---

## 🧪 Testing

### Tests Implementados

- **Wizard Contextual**: 6 tests
- **Secciones Smoke**: 4 tests
- **User Context**: 9 tests
- **Middleware**: 5 tests
- **Dashboard Templates**: 5 tests

**Total**: 31 tests, todos pasando ✅

---

## 📝 Mejores Prácticas

### JavaScript

1. **Modularidad**: Cada módulo tiene una responsabilidad clara
2. **Fallbacks**: Siempre proporcionar fallbacks si nuevas funcionalidades fallan
3. **Error Handling**: Manejar errores gracefully
4. **Performance**: Usar `dataLoader` para requests repetidos

### CSS

1. **Mobile First**: Diseñar para móvil primero
2. **Variables**: Usar tokens CSS para consistencia
3. **Animaciones**: Mantener animaciones sutiles y rápidas
4. **Accesibilidad**: Respetar `prefers-reduced-motion`

### Templates

1. **Template Tags**: Usar template tags para lógica de presentación
2. **Condicionales**: Mostrar/ocultar según permisos
3. **Semántica**: Usar HTML semántico
4. **Accesibilidad**: Incluir ARIA labels cuando sea necesario

---

## 🔄 Flujo de Desarrollo

### Agregar Nueva Sección

1. Crear template en `templates/frontend/nueva-seccion/`
2. Crear JavaScript en `static/frontend/js/sections-nueva.js`
3. Agregar ruta en `urls.py`
4. Agregar view en `views.py`
5. Actualizar `lazy-loader.js` para cargar el módulo
6. Agregar a navegación en `services.py` (ui_config)
7. Crear tests

### Agregar Nuevo Permiso

1. Definir permiso en `services.py` (get_ui_config_for_role)
2. Agregar evaluación en `evaluate_access_policy`
3. Usar en templates con `{% has_permission %}`
4. Usar en JavaScript con `userContext.permissions`

---

## 📊 Métricas de Performance

### Objetivos

- **FCP (First Contentful Paint)**: < 1000ms
- **TTI (Time to Interactive)**: < 2500ms
- **LCP (Largest Contentful Paint)**: < 2500ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Tamaño JS inicial**: < 100KB

### Monitoreo

- `performance.js` mide métricas en tiempo real
- Envía métricas a `/api/wizard/performance/metrics/`
- Logs en consola del navegador

---

## 🚀 Despliegue

### Checklist Pre-Producción

- [ ] Todos los tests pasando
- [ ] Lazy loading funcionando
- [ ] Caching funcionando
- [ ] Responsive design probado en móvil/tablet
- [ ] Animaciones funcionando
- [ ] Performance dentro de objetivos
- [ ] Documentación actualizada

### Comandos

```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test apps.frontend

# Verificar sintaxis
python manage.py check
```

---

**Última actualización**: 2026-01-23
