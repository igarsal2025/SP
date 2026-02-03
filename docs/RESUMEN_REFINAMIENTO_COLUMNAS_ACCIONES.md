# Resumen: Refinamiento de Columnas y Acciones por Perfil

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: ✅ Completado

---

## 📋 Resumen

Se ha refinado la visualización de las secciones de **Proyectos**, **Reportes** y **Aprobaciones** para personalizar las columnas y acciones según el rol del usuario, mejorando la experiencia y reduciendo la sobrecarga de información.

---

## 🎯 Cambios Implementados

### 1. Proyectos (`/projects/`)

#### Columnas por Rol

**Admin y PM** (vista completa):
- Nombre
- Estado
- Código
- Progreso (%)
- PM (Project Manager)
- Inicio
- Fin
- Prioridad
- **Acciones**: Ver, Editar

**Supervisor** (vista intermedia):
- Nombre
- Estado
- Progreso (%)
- Inicio
- Fin
- **Acciones**: Ver

**Técnico y Cliente** (vista básica):
- Nombre
- Estado
- Progreso (%)
- **Acciones**: Ver (solo si tiene permiso)

#### Acciones Disponibles

- **Botón "Crear Proyecto"**: Visible solo si tiene permiso `projects.create` (Admin, PM)
- **Botón "Ver"**: Visible si tiene permiso `projects.view`
- **Botón "Editar"**: Visible si tiene permiso `projects.edit` (Admin, PM)

---

### 2. Reportes (`/reports/`)

#### Columnas por Rol

**Admin, PM y Supervisor** (vista completa):
- Proyecto
- Semana
- Estado
- Técnico
- Progreso (%)
- Creado
- **Acciones**: Ver, Aprobar (si está `submitted`)

**Técnico** (vista operativa):
- Proyecto
- Semana
- Estado
- Progreso (%)
- **Acciones**: Ver, Enviar (si está `draft`)

**Cliente** (vista básica):
- Proyecto
- Semana
- Estado
- **Acciones**: Ver (solo lectura)

#### Acciones Disponibles

- **Botón "Nuevo Reporte"**: Visible solo si tiene permiso `reports.create` (técnico, supervisor, PM, admin)
- **Botón "Ver"**: Visible si tiene permiso `reports.view`
- **Botón "Enviar"**: Visible para técnicos si el reporte está en estado `draft` y tiene permiso `wizard.submit`
- **Botón "Aprobar"**: Visible para supervisor/PM/admin si el reporte está en estado `submitted` y tiene permiso `reports.approve`

---

### 3. Aprobaciones (`/reports/approvals/`)

#### Columnas

**Todos los roles con acceso** (Supervisor, PM, Admin):
- Proyecto
- Semana
- Técnico
- Progreso (%)
- Enviado (fecha)
- **Acciones**: Ver, Aprobar, Rechazar

#### Acciones Disponibles

- **Botón "Ver"**: Ver detalle del reporte
- **Botón "Aprobar"**: Aprobar reporte (llama a `/api/reports/reportes/{id}/approve/`)
- **Botón "Rechazar"**: Rechazar reporte (actualiza status a `rejected`)

---

## 🔧 Implementación Técnica

### Templates Actualizados

1. **`projects/list.html`**:
   - Agregado botón "Crear Proyecto" condicional con template tag `has_permission`

2. **`reports/list.html`**:
   - Agregado botón "Nuevo Reporte" condicional con template tag `has_permission`

3. **`reports/approvals.html`**:
   - Sin cambios en template (las acciones se agregan dinámicamente en JS)

### JavaScript Actualizado

1. **`sections-projects.js`**:
   - Función `getColumns()` que adapta columnas según `userContext.profile.role`
   - Columna de acciones con botones "Ver" y "Editar" según permisos
   - Manejo de función `render` para columnas con botones

2. **`sections-reports.js`**:
   - Función `getColumns()` que adapta columnas según rol
   - Columna de acciones con botones "Ver", "Enviar" (técnico), "Aprobar" (supervisor/PM/admin)
   - Integración con endpoint `/api/reports/reportes/{id}/submit/` y `/approve/`

3. **`sections-approvals.js`**:
   - Función `getColumns()` con columnas completas
   - Columna de acciones con botones "Ver", "Aprobar", "Rechazar"
   - Integración con endpoints de aprobación

### Mejoras en Renderizado

Todos los archivos JavaScript ahora manejan correctamente:
- Columnas con función `value` (simple)
- Columnas con función `render` (compleja, con botones)
- Detección automática del tipo de columna

---

## 📊 Matriz de Columnas y Acciones

### Proyectos

| Columna | Admin | PM | Supervisor | Técnico | Cliente |
|---------|-------|----|-----------|---------|---------|
| Nombre | ✅ | ✅ | ✅ | ✅ | ✅ |
| Estado | ✅ | ✅ | ✅ | ✅ | ✅ |
| Código | ✅ | ✅ | ❌ | ❌ | ❌ |
| Progreso | ✅ | ✅ | ✅ | ✅ | ✅ |
| PM | ✅ | ✅ | ❌ | ❌ | ❌ |
| Inicio | ✅ | ✅ | ✅ | ❌ | ❌ |
| Fin | ✅ | ✅ | ✅ | ❌ | ❌ |
| Prioridad | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Acciones** | Ver, Editar | Ver, Editar | Ver | Ver | Ver |

### Reportes

| Columna | Admin | PM | Supervisor | Técnico | Cliente |
|---------|-------|----|-----------|---------|---------|
| Proyecto | ✅ | ✅ | ✅ | ✅ | ✅ |
| Semana | ✅ | ✅ | ✅ | ✅ | ✅ |
| Estado | ✅ | ✅ | ✅ | ✅ | ✅ |
| Técnico | ✅ | ✅ | ✅ | ❌ | ❌ |
| Progreso | ✅ | ✅ | ✅ | ✅ | ❌ |
| Creado | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Acciones** | Ver, Aprobar | Ver, Aprobar | Ver, Aprobar | Ver, Enviar | Ver |

### Aprobaciones

| Columna | Supervisor | PM | Admin |
|---------|-----------|----|----|
| Proyecto | ✅ | ✅ | ✅ |
| Semana | ✅ | ✅ | ✅ |
| Técnico | ✅ | ✅ | ✅ |
| Progreso | ✅ | ✅ | ✅ |
| Enviado | ✅ | ✅ | ✅ |
| **Acciones** | Ver, Aprobar, Rechazar | Ver, Aprobar, Rechazar | Ver, Aprobar, Rechazar |

---

## ✅ Validación

- ✅ Tests de smoke pasando (4 tests)
- ✅ Templates renderizan correctamente
- ✅ JavaScript obtiene contexto del usuario
- ✅ Columnas se adaptan según rol
- ✅ Acciones se muestran según permisos

---

## 🎯 Beneficios

1. **Reducción de sobrecarga cognitiva**: Cada usuario ve solo la información relevante
2. **Mejor UX**: Acciones claras y contextuales
3. **Seguridad**: Los botones solo aparecen si el usuario tiene permisos
4. **Mantenibilidad**: Lógica centralizada en funciones `getColumns()`

---

## 📝 Notas de Implementación

### Pendientes (TODOs en código)

- Navegación a detalle de proyecto/reporte (botones "Ver")
- Navegación a edición de proyecto (botón "Editar")
- Endpoint de rechazo de reportes (actualmente usa PATCH directo)
- Modal o página para creación de proyectos

### Mejoras Futuras

- Agregar tooltips a botones
- Confirmaciones más elegantes (modal en lugar de `confirm()`)
- Paginación en tablas
- Búsqueda y filtros avanzados
- Exportación de datos

---

**Última actualización**: 2026-01-23
