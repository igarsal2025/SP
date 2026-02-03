# Estado Actual del Frontend SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Propósito**: Documentar el estado actual antes del rediseño

---

## 📋 Resumen

Este documento captura el estado actual del frontend de SITEC antes de iniciar el rediseño. Sirve como referencia para:
- Comparar antes/después
- Identificar funcionalidad que debe preservarse
- Documentar decisiones de diseño actuales
- Referencia para rollback si es necesario

---

## 🏗️ Estructura Actual

### Templates Existentes

#### `base.html`
- **Ubicación**: `backend/apps/frontend/templates/frontend/base.html`
- **Contenido**:
  - Header con brand "SITEC"
  - Indicador de estado de sincronización
  - Indicador de último guardado
  - Scripts comunes (performance, PWA, sync, analytics, permissions, components, wizard)
- **Sin navegación principal**: No hay menú de navegación entre secciones

#### `dashboard.html`
- **Ubicación**: `backend/apps/frontend/templates/frontend/dashboard.html`
- **Contenido**: 9 paneles en una sola vista:
  1. **KPIs principales**: Con filtros (proyecto, fechas)
  2. **Alertas**: Eventos que requieren atención
  3. **Comparativos**: Variaciones respecto a semana anterior
  4. **Tendencias Históricas**: Con selector de tipo (mensual/semanal) y períodos
  5. **Histórico de snapshots**: Tabla con últimos cortes por período
  6. **Histórico agregado mensual**: Tabla consolidada por mes
  7. **KPIs ROI**: Con selector de período y exportación CSV
  8. **Proyectos recientes**: Tabla con filtro de estado y paginación
  9. **Reportes recientes**: Tabla con filtro de estado y paginación
- **Problema**: Todos los paneles visibles para todos los usuarios, sin filtrado por rol

#### `wizard.html`
- **Ubicación**: `backend/apps/frontend/templates/frontend/wizard.html`
- **Contenido**:
  - Formulario de login (si no autenticado)
  - Wizard principal con:
    - Header con paso actual y ETA
    - Barra de progreso
    - Estado y validaciones
    - Componentes avanzados (risk-matrix, gantt-lite, kanban)
    - Chatbot IA
    - Generación de PDF
    - Botones de navegación (Anterior, Siguiente, Guardar, Modo Campo)
  - FAB (Floating Action Button) con acciones rápidas
- **Problema**: Todos los componentes visibles para todos, sin considerar permisos

#### `offline.html`
- **Ubicación**: `backend/apps/frontend/templates/frontend/offline.html`
- **Propósito**: Página mostrada cuando no hay conexión
- **Estado**: Funcional, no requiere cambios

---

## 📜 JavaScript Actual

### `dashboard.js`
- **Ubicación**: `backend/static/frontend/js/dashboard.js`
- **Funcionalidad**:
  - Carga de KPIs principales
  - Renderizado de alertas
  - Renderizado de comparativos
  - Carga de tendencias históricas (con gráficos SVG)
  - Renderizado de tablas (histórico, agregado, ROI, proyectos, reportes)
  - Filtros avanzados (proyecto, fechas)
  - Exportación CSV de ROI
  - Paginación de proyectos y reportes
- **Tamaño**: ~1046 líneas
- **Dependencias**: Ninguna específica, usa fetch API

### `wizard.js`
- **Ubicación**: `backend/static/frontend/js/wizard.js`
- **Funcionalidad**:
  - Renderizado dinámico de pasos del wizard
  - Validación local y del servidor
  - Sincronización offline
  - Modo campo (geolocalización)
  - Generación de PDF
  - Chatbot IA
  - Guardado de borradores
- **Tamaño**: ~1600+ líneas
- **Dependencias**: `sync.js`, `analytics.js`, `permissions.js`

### Otros Scripts
- `sync.js`: Sincronización offline
- `analytics.js`: Analytics y tracking
- `permissions.js`: Lógica de permisos (básica)
- `performance.js`: Métricas de rendimiento
- `pwa.js`: Funcionalidad PWA
- `components.js`: Componentes reutilizables

---

## 🎨 Estilos Actuales

### Archivos CSS
- `tokens.css`: Variables CSS (colores, tipografía, espaciado)
- `components.css`: Estilos de componentes reutilizables
- `wizard.css`: Estilos específicos del wizard

### Sistema de Diseño
- **Colores**: Basados en tokens CSS
- **Tipografía**: Sistema de fuentes definido en tokens
- **Componentes**: Cards, botones, inputs, tablas, badges
- **Layout**: Grid system básico

---

## 🔌 Endpoints API Actuales

### Dashboard
- `GET /api/dashboard/kpi/`: KPIs principales
- `GET /api/dashboard/trends/`: Tendencias históricas
- `GET /api/dashboard/alerts/`: Alertas
- `GET /api/dashboard/comparatives/`: Comparativos
- `GET /api/dashboard/history/`: Histórico de snapshots
- `GET /api/dashboard/aggregate/`: Histórico agregado

### Wizard
- `GET /api/wizard/profile/`: Perfil del usuario actual
- `POST /api/wizard/validate/`: Validar paso
- `POST /api/wizard/sync/`: Sincronizar datos
- `GET /api/wizard/steps/`: Obtener pasos

### Proyectos
- `GET /api/projects/`: Lista de proyectos
- `GET /api/projects/<id>/`: Detalle de proyecto

### Reportes
- `GET /api/reports/`: Lista de reportes
- `GET /api/reports/<id>/`: Detalle de reporte

---

## 👥 Perfiles de Usuario Actuales

### Roles Definidos
1. **`admin_empresa`**: Administrador de empresa
2. **`pm`**: Project Manager
3. **`supervisor`**: Supervisor
4. **`tecnico`**: Técnico
5. **`cliente`**: Cliente

### Permisos ABAC (Backend)
- Definidos en `backend/apps/accounts/models.py` (AccessPolicy)
- Evaluados en `backend/apps/accounts/services.py` (evaluate_access_policy)
- Aplicados en `backend/apps/accounts/permissions.py` (AccessPolicyPermission)

### Problema Actual
- **Backend respeta permisos**: Las APIs devuelven 403 si no hay permisos
- **Frontend no respeta permisos**: Muestra todas las opciones a todos
- **Resultado**: Usuarios ven opciones que no pueden usar

---

## 🐛 Problemas Identificados

### 1. Sobrecarga de Información
- **Problema**: 9 paneles en dashboard, todos visibles simultáneamente
- **Impacto**: Usuarios deben hacer scroll extenso, información irrelevante visible
- **Solución propuesta**: Dashboards personalizados por perfil

### 2. Falta de Personalización
- **Problema**: Mismo contenido para todos los perfiles
- **Impacto**: Confusión, opciones no utilizables visibles
- **Solución propuesta**: Contenido filtrado por rol

### 3. Navegación Limitada
- **Problema**: No hay sistema de navegación principal
- **Impacto**: Difícil moverse entre secciones
- **Solución propuesta**: Barra de navegación con secciones por rol

### 4. Wizard No Contextual
- **Problema**: Todos los componentes visibles para todos
- **Impacto**: Clientes ven opciones de edición, técnicos ven opciones innecesarias
- **Solución propuesta**: Wizard contextual según permisos

### 5. Falta de Feedback Visual
- **Problema**: No hay indicación clara de qué puede hacer cada usuario
- **Impacto**: Usuarios intentan usar funcionalidad no permitida
- **Solución propuesta**: UI que refleja permisos del usuario

---

## ✅ Funcionalidad que Debe Preservarse

### Dashboard
- ✅ Carga de KPIs principales
- ✅ Filtros avanzados (proyecto, fechas)
- ✅ Tendencias históricas con gráficos
- ✅ Comparativos mes-a-mes y año-a-año
- ✅ Exportación CSV de ROI
- ✅ Paginación de proyectos y reportes
- ✅ Tablas de histórico y agregado

### Wizard
- ✅ Renderizado dinámico de pasos
- ✅ Validación local y del servidor
- ✅ Sincronización offline
- ✅ Modo campo (geolocalización)
- ✅ Generación de PDF
- ✅ Chatbot IA
- ✅ Guardado de borradores

### General
- ✅ Funcionalidad PWA
- ✅ Sincronización offline
- ✅ Analytics y tracking
- ✅ Métricas de rendimiento

---

## 📊 Métricas Actuales

### Performance
- **Tiempo de carga dashboard**: ~2-3s (depende de datos)
- **Tamaño JS total**: ~116 KB (comprimido)
- **Requests iniciales**: ~10-15 requests

### Usabilidad
- **Scroll necesario**: Alto (9 paneles en una vista)
- **Navegación**: Limitada (solo dentro de cada página)
- **Feedback visual**: Básico

---

## 🔄 Cambios Propuestos (Resumen)

1. **Sistema de navegación principal**: Barra de navegación con secciones por rol
2. **Dashboards personalizados**: Un dashboard por perfil con contenido relevante
3. **Wizard contextual**: Componentes visibles según permisos
4. **Estructura modular**: Componentes reutilizables y organizados
5. **Mejor UX**: Reducción de carga cognitiva, mejor organización

---

## 📝 Notas para Implementación

### Compatibilidad
- Mantener URLs actuales funcionando
- No romper funcionalidad existente
- Feature flags para activar/desactivar nuevo sistema

### Migración
- Migración gradual, no big bang
- Mantener código antiguo como fallback
- Tests exhaustivos antes de reemplazar

### Documentación
- Documentar cambios en cada fase
- Crear guías de usuario por perfil
- Mantener changelog actualizado

---

## 🔗 Referencias

- **Diagnóstico**: `docs/DIAGNOSTICO_REDISEÑO_FRONTEND.md`
- **Plan de acción**: `docs/PLAN_ACCION_REDISEÑO_FRONTEND.md`
- **Referencia rápida**: `docs/REFERENCIA_RAPIDA_REDISEÑO.md`
- **Permisos ABAC**: `docs/GUIA_CONFIGURACION_ABAC.md`

---

**Última actualización**: 2026-01-23  
**Estado**: 📸 Captura antes del rediseño
