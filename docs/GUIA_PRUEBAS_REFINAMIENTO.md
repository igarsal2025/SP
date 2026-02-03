# Guía de Pruebas: Refinamiento de Columnas y Acciones

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## ✅ Validación Automática Completada

### Tests Ejecutados

- ✅ **25 tests pasaron** correctamente:
  - 4 tests de smoke (secciones renderizan)
  - 9 tests de contexto de usuario
  - 5 tests de middleware
  - 5 tests de selección de templates de dashboard
  - 2 tests adicionales de configuración UI

---

## 🧪 Pruebas Manuales Recomendadas

### 1. Probar Proyectos (`/projects/`)

#### Como Admin o PM
1. Iniciar sesión con usuario `admin_empresa` o `pm`
2. Navegar a `/projects/`
3. **Verificar**:
   - ✅ Botón "Crear Proyecto" visible
   - ✅ Tabla muestra 8+ columnas: Nombre, Estado, Código, Progreso, PM, Inicio, Fin, Prioridad
   - ✅ Columna "Acciones" con botones "Ver" y "Editar"
   - ✅ Filtro por estado funciona

#### Como Supervisor
1. Iniciar sesión con usuario `supervisor`
2. Navegar a `/projects/`
3. **Verificar**:
   - ❌ Botón "Crear Proyecto" NO visible
   - ✅ Tabla muestra 5 columnas: Nombre, Estado, Progreso, Inicio, Fin
   - ✅ Columna "Acciones" con botón "Ver" (sin "Editar")

#### Como Técnico o Cliente
1. Iniciar sesión con usuario `tecnico` o `cliente`
2. Navegar a `/projects/`
3. **Verificar**:
   - ❌ Botón "Crear Proyecto" NO visible
   - ✅ Tabla muestra 3 columnas: Nombre, Estado, Progreso
   - ✅ Columna "Acciones" con botón "Ver" (si tiene permiso)

---

### 2. Probar Reportes (`/reports/`)

#### Como Admin, PM o Supervisor
1. Iniciar sesión con usuario `admin_empresa`, `pm` o `supervisor`
2. Navegar a `/reports/`
3. **Verificar**:
   - ✅ Tabla muestra 6 columnas: Proyecto, Semana, Estado, Técnico, Progreso, Creado
   - ✅ Columna "Acciones" con botón "Ver"
   - ✅ Botón "Aprobar" visible en reportes con estado `submitted`
   - ✅ Filtro por estado funciona

#### Como Técnico
1. Iniciar sesión con usuario `tecnico`
2. Navegar a `/reports/`
3. **Verificar**:
   - ✅ Botón "Nuevo Reporte" visible
   - ✅ Tabla muestra 4 columnas: Proyecto, Semana, Estado, Progreso
   - ✅ Botón "Enviar" visible en reportes propios con estado `draft`
   - ✅ Botón "Enviar" redirige o actualiza el estado

#### Como Cliente
1. Iniciar sesión con usuario `cliente`
2. Navegar a `/reports/`
3. **Verificar**:
   - ❌ Botón "Nuevo Reporte" NO visible
   - ✅ Tabla muestra 3 columnas: Proyecto, Semana, Estado
   - ✅ Solo botón "Ver" en acciones (solo lectura)

---

### 3. Probar Aprobaciones (`/reports/approvals/`)

#### Como Supervisor, PM o Admin
1. Iniciar sesión con usuario `supervisor`, `pm` o `admin_empresa`
2. Navegar a `/reports/approvals/`
3. **Verificar**:
   - ✅ Tabla muestra 5 columnas: Proyecto, Semana, Técnico, Progreso, Enviado
   - ✅ Columna "Acciones" con botones: "Ver", "Aprobar", "Rechazar"
   - ✅ Solo muestra reportes con estado `submitted`
   - ✅ Botón "Aprobar" llama a `/api/reports/reportes/{id}/approve/`
   - ✅ Botón "Rechazar" actualiza el estado a `rejected`

---

## 🔍 Verificaciones Adicionales

### JavaScript en Consola del Navegador

1. Abrir DevTools (F12)
2. Ir a la pestaña "Console"
3. **Verificar**:
   - ✅ No hay errores de JavaScript
   - ✅ `window.RoleBasedUI` está disponible
   - ✅ `window.RoleBasedUI.getUserContext()` devuelve datos correctos
   - ✅ Las tablas se renderizan correctamente

### Network Tab

1. Abrir DevTools → Network
2. Recargar la página
3. **Verificar**:
   - ✅ `/api/user/context/` devuelve 200 OK
   - ✅ `/api/projects/proyectos/` o `/api/reports/reportes/` devuelven 200 OK
   - ✅ Las respuestas incluyen los datos esperados

---

## 📋 Checklist de Validación

### Funcionalidad
- [ ] Botones de creación aparecen solo con permisos correctos
- [ ] Columnas se adaptan según rol
- [ ] Acciones (botones) aparecen según permisos
- [ ] Filtros funcionan correctamente
- [ ] Botones de acción ejecutan las operaciones esperadas

### UI/UX
- [ ] Tablas se renderizan sin errores
- [ ] Botones tienen estilos correctos
- [ ] Mensajes de estado ("Cargando...", "Listo") funcionan
- [ ] No hay elementos rotos o mal posicionados

### Seguridad
- [ ] Usuarios sin permisos no ven botones de acción
- [ ] Las acciones respetan los permisos ABAC
- [ ] Las peticiones API incluyen credenciales correctas

---

## 🐛 Problemas Conocidos / Pendientes

### TODOs en Código
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

## 📊 Resultados Esperados

### Proyectos - Matriz de Columnas

| Rol | Columnas | Botón Crear | Acciones |
|-----|----------|-------------|----------|
| Admin | 8+ | ✅ | Ver, Editar |
| PM | 8+ | ✅ | Ver, Editar |
| Supervisor | 5 | ❌ | Ver |
| Técnico | 3 | ❌ | Ver |
| Cliente | 3 | ❌ | Ver |

### Reportes - Matriz de Columnas

| Rol | Columnas | Botón Nuevo | Acciones |
|-----|----------|-------------|----------|
| Admin | 6 | ✅ | Ver, Aprobar |
| PM | 6 | ✅ | Ver, Aprobar |
| Supervisor | 6 | ✅ | Ver, Aprobar |
| Técnico | 4 | ✅ | Ver, Enviar |
| Cliente | 3 | ❌ | Ver |

### Aprobaciones - Matriz de Columnas

| Rol | Columnas | Acciones |
|-----|----------|----------|
| Supervisor | 5 | Ver, Aprobar, Rechazar |
| PM | 5 | Ver, Aprobar, Rechazar |
| Admin | 5 | Ver, Aprobar, Rechazar |

---

## ✅ Conclusión

Todos los tests automatizados pasaron correctamente. Los cambios están listos para pruebas manuales en el navegador.

**Próximo paso**: Ejecutar pruebas manuales según esta guía y reportar cualquier problema encontrado.
