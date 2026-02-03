# Componentes Fase 1: Preparación y Base

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📋 Resumen

Este documento describe los componentes creados en la Fase 1 del rediseño del frontend, incluyendo su uso, API y ejemplos.

---

## 🔧 Componentes Backend

### 1. Endpoint `/api/user/context/`

**Ubicación**: `backend/apps/accounts/views.py`

**Clase**: `UserContextView`

**Uso**:
```python
# En urls.py
path("api/user/context/", UserContextView.as_view(), name="user-context")
```

**Ver**: `docs/API_USER_CONTEXT.md` para documentación completa.

---

### 2. Middleware `UserContextMiddleware`

**Ubicación**: `backend/apps/frontend/middleware.py`

**Funcionalidad**: Agrega `user_context` a cada request para usuarios autenticados.

**Configuración**:
```python
# En settings.py
MIDDLEWARE = [
    # ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.frontend.middleware.UserContextMiddleware",
    # ...
]
```

**Uso en vistas**:
```python
def my_view(request):
    user_context = getattr(request, 'user_context', None)
    if user_context:
        role = user_context['profile']['role']
        permissions = user_context['permissions']
        ui_config = user_context['ui_config']
```

---

### 3. Template Tags

**Ubicación**: `backend/apps/frontend/templatetags/role_tags.py`

#### `show_for_role`
Muestra contenido solo para roles específicos.

```django
{% load role_tags %}

{% show_for_role "pm" "admin_empresa" as can_edit %}
{% if can_edit %}
    <button>Editar</button>
{% endif %}
```

#### `has_permission`
Verifica si el usuario tiene un permiso específico.

```django
{% has_permission "projects.create" as can_create %}
{% if can_create %}
    <button>Crear Proyecto</button>
{% endif %}
```

#### `dashboard_section_visible`
Verifica si una sección de dashboard está visible.

```django
{% dashboard_section_visible "roi" as show_roi %}
{% if show_roi %}
    <div class="panel">
        <!-- Contenido ROI -->
    </div>
{% endif %}
```

#### `user_role`
Obtiene el rol del usuario actual.

```django
{% user_role as role %}
<span>Rol: {{ role }}</span>
```

#### `can_access_navigation`
Verifica acceso a elementos de navegación.

```django
{% can_access_navigation "dashboard" as show_dashboard %}
{% if show_dashboard %}
    <a href="/dashboard">Dashboard</a>
{% endif %}
```

#### `wizard_mode`
Obtiene el modo del wizard.

```django
{% wizard_mode as mode %}
{% if mode == "full" %}
    <button>Guardar</button>
{% endif %}
```

---

## 🎨 Componentes Frontend (JavaScript)

### 1. `role-based-ui.js`

**Ubicación**: `backend/static/frontend/js/role-based-ui.js`

**API Global**: `window.RoleBasedUI`

#### Funciones Disponibles

##### `getUserContext()`
Obtiene el contexto del usuario desde el servidor.

```javascript
const context = await window.RoleBasedUI.getUserContext();
console.log(context.profile.role);
```

##### `showForRole(element, allowedRoles)`
Muestra/oculta elementos según rol.

```javascript
// Por selector
await window.RoleBasedUI.showForRole('#edit-button', ['pm', 'admin_empresa']);

// Por elemento
const button = document.getElementById('edit-button');
await window.RoleBasedUI.showForRole(button, ['pm']);
```

##### `hasPermission(permissionName)`
Verifica si el usuario tiene un permiso.

```javascript
const canCreate = await window.RoleBasedUI.hasPermission('projects.create');
if (canCreate) {
    // Mostrar botón
}
```

##### `isDashboardSectionVisible(sectionName)`
Verifica visibilidad de secciones de dashboard.

```javascript
const showRoi = await window.RoleBasedUI.isDashboardSectionVisible('roi');
if (showRoi) {
    // Mostrar sección ROI
}
```

##### `canAccessNavigation(navItem)`
Verifica acceso a navegación.

```javascript
const canAccess = await window.RoleBasedUI.canAccessNavigation('dashboard');
```

##### `getWizardMode()`
Obtiene el modo del wizard.

```javascript
const mode = await window.RoleBasedUI.getWizardMode();
if (mode === 'full') {
    // Habilitar edición
}
```

##### `initializeRoleBasedUI()`
Inicializa la UI automáticamente según el rol.

```javascript
// Se ejecuta automáticamente al cargar la página
// También se puede llamar manualmente
await window.RoleBasedUI.initializeRoleBasedUI();
```

#### Atributos Data

El módulo respeta atributos `data-*` para control declarativo:

```html
<!-- Ocultar si no tiene permiso -->
<button data-requires-permission="projects.create">Crear</button>

<!-- Ocultar sección si no está permitida -->
<div data-dashboard-section="roi">Contenido ROI</div>

<!-- Ocultar elemento de navegación si no está permitido -->
<a data-nav-item="dashboard" href="/dashboard">Dashboard</a>

<!-- Ocultar en modo readonly -->
<button data-wizard-edit>Editar</button>
```

#### Eventos

##### `roleBasedUIInitialized`
Se dispara cuando la UI está inicializada.

```javascript
document.addEventListener('roleBasedUIInitialized', (e) => {
    console.log('Rol:', e.detail.role);
    console.log('Contexto:', e.detail.context);
});
```

---

### 2. `navigation.js`

**Ubicación**: `backend/static/frontend/js/navigation.js`

**API Global**: `window.navigationManager`

#### Funcionalidad

El sistema de navegación se inicializa automáticamente y:
- Crea navegación si no existe
- Oculta elementos no permitidos
- Detecta sección actual desde URL
- Marca elemento activo

#### Uso Manual

```javascript
// Inicializar manualmente
await window.navigationManager.initialize(userContext);

// Navegar a una sección
window.navigationManager.navigateToSection('dashboard');

// Verificar acceso
const canAccess = window.navigationManager.canAccessSection('dashboard');

// Establecer sección activa
window.navigationManager.setActiveSection('dashboard');
```

#### Eventos

##### `navigationChange`
Dispara navegación desde otros componentes.

```javascript
document.dispatchEvent(new CustomEvent('navigationChange', {
    detail: { section: 'dashboard' }
}));
```

---

## 📦 Integración

### En Templates HTML

```html
{% load static %}
{% load role_tags %}

<!DOCTYPE html>
<html>
<head>
    <title>SITEC</title>
</head>
<body>
    <!-- Navegación con template tags -->
    <nav>
        {% can_access_navigation "dashboard" as show_dashboard %}
        {% if show_dashboard %}
            <a href="/dashboard">Dashboard</a>
        {% endif %}
    </nav>

    <!-- Contenido con permisos -->
    {% has_permission "projects.create" as can_create %}
    {% if can_create %}
        <button>Crear Proyecto</button>
    {% endif %}

    <!-- Scripts -->
    <script src="{% static 'frontend/js/role-based-ui.js' %}"></script>
    <script src="{% static 'frontend/js/navigation.js' %}"></script>
</body>
</html>
```

### En JavaScript

```javascript
// Esperar a que la UI esté inicializada
document.addEventListener('roleBasedUIInitialized', async (e) => {
    const context = e.detail.context;
    
    // Usar contexto para personalizar UI
    if (context.ui_config.wizard_mode === 'readonly') {
        // Deshabilitar edición
    }
    
    // Verificar permisos
    if (await window.RoleBasedUI.hasPermission('projects.create')) {
        // Mostrar botón de crear
    }
});
```

---

## 🧪 Testing

### Tests Backend

```bash
# Tests del endpoint
python manage.py test apps.accounts.tests_context

# Tests del middleware
python manage.py test apps.frontend.tests_middleware
```

### Tests Manuales

1. **Endpoint**:
   ```bash
   curl http://localhost:8000/api/user/context/ \
     -H "Cookie: sessionid=..."
   ```

2. **Template Tags**: Renderizar templates y verificar visibilidad

3. **JavaScript**: Abrir consola del navegador y verificar:
   ```javascript
   window.RoleBasedUI.getUserContext().then(console.log);
   ```

---

## 🔗 Referencias

- `docs/API_USER_CONTEXT.md` - Documentación del endpoint
- `docs/FASE1_IMPLEMENTACION_COMPLETA.md` - Resumen de implementación
- `docs/DIAGNOSTICO_REDISEÑO_FRONTEND.md` - Diagnóstico completo

---

**Última actualización**: 2026-01-23
