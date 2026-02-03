# Resumen de Mejoras Sync Avanzado - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Se han implementado mejoras avanzadas en el módulo de sincronización (Módulo 2), incluyendo diffs visuales para resolución de conflictos y resolución granular por campo.

---

## ✅ Funcionalidades Implementadas

### 1. Diffs Visuales de Conflictos ✅

**Descripción**: Visualización de diferencias entre datos del servidor y cliente.

**Endpoint**: `/api/sync/sessions/<session_id>/conflicts/<item_id>/diff/`

**Funcionalidades**:
- Comparación lado a lado de datos
- Identificación de campos modificados
- Identificación de campos agregados/removidos
- Visualización clara de diferencias

**Uso**:
```javascript
const resolver = new ConflictResolver(sessionId);
const diff = await resolver.getDiff(itemId, clientData);
resolver.renderDiff(container, diff);
```

---

### 2. Resolución Granular por Campo ✅

**Descripción**: Resolver conflictos seleccionando qué versión usar para cada campo.

**Endpoint**: `/api/sync/sessions/<session_id>/conflicts/<item_id>/resolve/`

**Funcionalidades**:
- Resolución por campo individual
- Opción de usar servidor, cliente o merge
- Merge automático para objetos y arrays
- Resolución completa del conflicto

**Uso**:
```javascript
const resolution = {
  "project_name": "server",  // Usar versión del servidor
  "progress_pct": "client",  // Usar versión del cliente
  "materials_list": "merge"  // Combinar ambas versiones
};

const result = await resolver.resolveConflict(itemId, resolution, clientData);
```

---

### 3. Cliente JavaScript para Conflictos ✅

**Archivo**: `backend/static/frontend/js/sync_conflicts.js`

**Clase**: `ConflictResolver`

**Métodos**:
- `getDiff(itemId, clientData)`: Obtener diff visual
- `resolveConflict(itemId, resolution, clientData)`: Resolver conflicto
- `renderDiff(container, diffData)`: Renderizar diff en DOM

**Características**:
- Renderizado automático de diffs
- Interfaz visual para selección
- Soporte para merge automático
- Eventos personalizados

---

## 📁 Archivos Creados/Modificados

### Backend

1. **`backend/apps/sync/views_conflicts.py`** (nuevo)
   - `ConflictDiffView`: Endpoint para obtener diffs
   - `ConflictResolutionView`: Endpoint para resolver conflictos

2. **`backend/apps/sync/urls.py`** (modificado)
   - Agregadas rutas para conflictos avanzados

### Frontend

3. **`backend/static/frontend/js/sync_conflicts.js`** (nuevo)
   - Clase `ConflictResolver` para manejo de conflictos

---

## 🎨 Interfaz Visual

### Componentes de UI

1. **Header de Conflicto**
   - Tipo de entidad
   - ID de entidad
   - Instrucciones

2. **Secciones de Diff**
   - Campos Modificados
   - Campos Agregados
   - Campos Removidos

3. **Versiones Lado a Lado**
   - Versión Servidor (con botón "Usar esta")
   - Versión Cliente (con botón "Usar esta")
   - Opción de Merge (si aplica)

4. **Radio Buttons**
   - Selección por campo
   - Opciones: Servidor, Cliente, Combinar

5. **Botones de Acción**
   - "Resolver Conflicto"
   - "Cancelar"

---

## 📊 Estructura de Datos

### Diff Response

```json
{
  "entity_type": "wizard_step",
  "entity_id": "1",
  "server_data": {
    "project_name": "Proyecto A",
    "progress_pct": 50
  },
  "client_data": {
    "project_name": "Proyecto B",
    "progress_pct": 60,
    "new_field": "valor"
  },
  "diff": {
    "added": {
      "new_field": {
        "client": "valor",
        "server": null
      }
    },
    "removed": {},
    "modified": {
      "project_name": {
        "client": "Proyecto B",
        "server": "Proyecto A"
      },
      "progress_pct": {
        "client": 60,
        "server": 50
      }
    },
    "unchanged": {}
  },
  "server_timestamp": "2025-01-18T10:00:00Z",
  "client_timestamp": "2025-01-18T11:00:00Z"
}
```

### Resolution Request

```json
{
  "resolution": {
    "project_name": "server",
    "progress_pct": "client",
    "materials_list": "merge"
  },
  "client_data": {
    "project_name": "Proyecto B",
    "progress_pct": 60
  }
}
```

---

## 🔧 Uso Completo

### Ejemplo 1: Obtener y Mostrar Diff

```javascript
// Inicializar resolver
const resolver = new ConflictResolver(sessionId);

// Obtener diff
const diff = await resolver.getDiff(itemId, clientData);

// Renderizar en contenedor
const container = document.getElementById("conflictContainer");
resolver.renderDiff(container, diff);

// Escuchar resolución
container.addEventListener("conflict:resolved", (e) => {
  console.log("Conflicto resuelto:", e.detail);
  // Recargar o actualizar UI
});
```

### Ejemplo 2: Resolver Manualmente

```javascript
const resolution = {
  "project_name": "server",  // Usar servidor
  "progress_pct": "client", // Usar cliente
  "materials_list": "merge" // Combinar
};

const result = await resolver.resolveConflict(
  itemId,
  resolution,
  clientData
);
```

### Ejemplo 3: Integración con Sync Manager

```javascript
// En sync.js, cuando se detecta conflicto
if (response.data.conflicts && response.data.conflicts.length > 0) {
  const conflictId = response.data.conflicts[0];
  const resolver = new ConflictResolver(response.data.session.id);
  
  // Mostrar modal de resolución
  showConflictModal(async () => {
    const diff = await resolver.getDiff(conflictId);
    resolver.renderDiff(modalContent, diff);
  });
}
```

---

## 🎯 Mejores Prácticas

### 1. Resolución Automática

Para conflictos simples, usar resolución automática:

```javascript
// Usar servidor por defecto
const resolution = Object.keys(diff.modified).reduce((acc, field) => {
  acc[field] = "server";
  return acc;
}, {});
```

### 2. Merge Inteligente

Para arrays y objetos, usar merge:

```javascript
const resolution = {};
Object.keys(diff.modified).forEach(field => {
  const values = diff.modified[field];
  if (Array.isArray(values.server) || typeof values.server === "object") {
    resolution[field] = "merge";
  } else {
    resolution[field] = "server"; // O "client" según lógica de negocio
  }
});
```

### 3. Validación Post-Resolución

Validar datos después de resolver:

```javascript
const result = await resolver.resolveConflict(itemId, resolution, clientData);
const resolvedData = result.resolved_data;

// Validar
if (validateData(resolvedData)) {
  // Continuar
} else {
  // Mostrar error
}
```

---

## 📝 Checklist de Funcionalidades

- [x] Endpoint para obtener diffs
- [x] Endpoint para resolver conflictos
- [x] Cliente JavaScript para conflictos
- [x] Renderizado visual de diffs
- [x] Resolución granular por campo
- [x] Soporte para merge automático
- [x] Eventos personalizados
- [x] Integración con sync existente

---

## 🚀 Próximos Pasos Opcionales

### Mejoras Futuras

1. **Historial de Resoluciones**:
   - Guardar historial de resoluciones
   - Sugerencias basadas en historial

2. **Resolución Inteligente**:
   - IA para sugerir resoluciones
   - Reglas de negocio para merge automático

3. **Compresión de Datos**:
   - Comprimir datos en sync
   - Reducir tamaño de payloads

4. **Sync Incremental**:
   - Solo sincronizar cambios
   - Reducir tráfico de red

---

**Última actualización**: 2026-01-18
