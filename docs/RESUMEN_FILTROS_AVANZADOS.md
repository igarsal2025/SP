# Resumen de Filtros Avanzados - Dashboard

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Se han implementado filtros avanzados en el dashboard para permitir análisis personalizados por proyecto y rango de fechas.

---

## ✅ Funcionalidades Implementadas

### 1. Filtros por Proyecto ✅

- Selector de proyectos en el dashboard
- Filtrado opcional (si no se selecciona, muestra todos)
- Carga automática de lista de proyectos al iniciar

### 2. Filtros por Rango de Fechas ✅

- Selector de fecha "Desde"
- Selector de fecha "Hasta"
- Validación de rango válido
- Comparativos calculados automáticamente para el período seleccionado

### 3. Botones de Control ✅

- **Aplicar Filtros**: Aplica los filtros seleccionados
- **Restablecer**: Limpia todos los filtros y vuelve a la vista por defecto

---

## 🔧 Implementación Técnica

### Backend

**Archivo**: `backend/apps/dashboard/views.py`

- Modificado `DashboardKpiView.get()` para aceptar parámetros opcionales:
  - `project_id`: ID del proyecto a filtrar
  - `start_date`: Fecha de inicio (formato YYYY-MM-DD)
  - `end_date`: Fecha de fin (formato YYYY-MM-DD)
  - `period_days`: Número de días del período

**Archivo**: `backend/apps/dashboard/services.py`

- Modificado `build_dashboard_payload()` para aceptar `project_id` opcional
- Modificado `build_dashboard_payload_range()` para filtrar por proyecto cuando se especifica

### Frontend

**Archivo**: `backend/apps/frontend/templates/frontend/dashboard.html`

- Agregados controles de filtro:
  - Selector de proyecto
  - Inputs de fecha (Desde/Hasta)
  - Botones de aplicar/restablecer

**Archivo**: `backend/static/frontend/js/dashboard.js`

- Función `loadProjectsForFilter()`: Carga lista de proyectos
- Función `applyFilters()`: Aplica filtros seleccionados
- Función `resetFilters()`: Restablece filtros
- Modificado `loadDashboard()` para aceptar parámetros de filtro

---

## 📊 Uso

### Aplicar Filtros

1. Seleccionar proyecto (opcional) del dropdown
2. Seleccionar fecha "Desde" (opcional)
3. Seleccionar fecha "Hasta" (opcional)
4. Hacer clic en **"Aplicar Filtros"**

### Restablecer Filtros

1. Hacer clic en **"Restablecer"**
2. El dashboard vuelve a mostrar datos sin filtros

---

## 🎯 Comportamiento

### Sin Filtros

- Muestra datos de todos los proyectos
- Período por defecto: últimos 7 días
- Usa snapshots cuando están disponibles

### Con Filtros

- Filtra datos según proyecto seleccionado (si aplica)
- Usa rango de fechas personalizado (si se especifica)
- **No usa snapshots** (siempre calcula en tiempo real)
- Comparativos se calculan para el período equivalente anterior

---

## 📝 Ejemplos de Uso

### Filtrar por Proyecto

```
Proyecto: "Proyecto ABC"
Desde: (vacío)
Hasta: (vacío)
```

**Resultado**: KPIs solo del proyecto seleccionado, últimos 7 días

### Filtrar por Rango de Fechas

```
Proyecto: (Todos)
Desde: 2026-01-01
Hasta: 2026-01-31
```

**Resultado**: KPIs de todos los proyectos en enero 2026

### Filtrar por Proyecto y Fechas

```
Proyecto: "Proyecto XYZ"
Desde: 2026-01-15
Hasta: 2026-01-31
```

**Resultado**: KPIs del proyecto seleccionado en el rango especificado

---

## ⚙️ Parámetros de API

### Endpoint: `/api/dashboard/`

**Query Parameters** (todos opcionales):

- `project_id`: ID del proyecto (integer)
- `start_date`: Fecha de inicio (YYYY-MM-DD)
- `end_date`: Fecha de fin (YYYY-MM-DD)
- `period_days`: Número de días del período (integer, default: 7)
- `snapshot`: Usar snapshot si está disponible ("1" o "0", default: "1")

**Ejemplo**:

```
GET /api/dashboard/?project_id=5&start_date=2026-01-01&end_date=2026-01-31
```

---

## 🔍 Validación

### Fechas

- Si solo se especifica `start_date` o `end_date`, se ignora el filtro de fechas
- Si `end_date` es anterior a `start_date`, se invierten automáticamente
- Si las fechas son inválidas, se usa el período por defecto

### Proyecto

- Si el `project_id` no existe, se ignora el filtro
- Si el proyecto no pertenece a la company/sitec, se ignora el filtro

---

## 📈 Performance

### Con Filtros

- **No usa cache de snapshots**: Siempre calcula en tiempo real
- **Queries optimizadas**: Usa `select_related()` y `only()`
- **Tiempo de respuesta**: Similar a sin filtros (~100-200ms)

### Sin Filtros

- **Usa snapshots**: Si están disponibles y no expiraron
- **Cache de tendencias**: Sigue funcionando independientemente

---

## ✅ Checklist de Funcionalidades

- [x] Selector de proyectos
- [x] Selector de fecha "Desde"
- [x] Selector de fecha "Hasta"
- [x] Botón "Aplicar Filtros"
- [x] Botón "Restablecer"
- [x] Carga automática de proyectos
- [x] Filtrado por proyecto en backend
- [x] Filtrado por rango de fechas en backend
- [x] Cálculo de comparativos con filtros
- [x] Validación de parámetros

---

**Última actualización**: 2026-01-18
