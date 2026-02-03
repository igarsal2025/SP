# Guía de Componentes Reutilizables - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Esta guía documenta todos los componentes reutilizables disponibles en el sistema SITEC. Estos componentes están diseñados para ser consistentes, accesibles y compatibles con el modo offline.

---

## 🎨 Componentes Base

### 1. Inputs Básicos

#### TextField

**Función**: `createField(field)`

**Uso**:
```javascript
const field = {
  name: "project_name",
  type: "text",
  label: "Nombre del proyecto",
  required: true,
  placeholder: "Ingrese el nombre"
};
const input = SitecComponents.createField(field);
```

**Props**:
- `name`: Nombre del campo (requerido)
- `type`: Tipo de input (`text`, `number`, `email`, `date`, `textarea`, `select`)
- `label`: Etiqueta visible
- `required`: Si es requerido
- `placeholder`: Texto de ayuda
- `options`: Array de opciones (para `select`)
- `show_if`: Condiciones para mostrar
- `required_if`: Condiciones para requerir

**Estados**:
- `pending`: Sin validar
- `valid`: Válido
- `invalid`: Inválido
- `syncing`: Sincronizando
- `synced`: Sincronizado
- `error`: Error

---

#### NumberField

Similar a TextField pero con validación numérica.

**Props adicionales**:
- `min`: Valor mínimo
- `max`: Valor máximo
- `step`: Incremento

---

#### SelectField

Similar a TextField pero con dropdown.

**Props adicionales**:
- `options`: Array de opciones `["opción1", "opción2"]`
- `multiple`: Si permite selección múltiple

---

#### DateField

Campo de fecha con validación.

**Props adicionales**:
- `min_date`: Fecha mínima
- `max_date`: Fecha máxima

---

#### Textarea

Campo de texto multilínea.

**Props adicionales**:
- `rows`: Número de filas
- `maxlength`: Longitud máxima

---

## 🎨 Componentes Avanzados

### 2. SignaturePad (Firma Digital)

**Función**: `createSignaturePad(targetInput, labelText, options)`

**Descripción**: Componente para capturar firmas digitales con canvas.

**Uso**:
```javascript
const input = document.querySelector('[name="signature_tech"]');
const wrapper = SitecComponents.createSignaturePad(input, "Firma Técnico", {
  dateInput: document.querySelector('[name="signature_date"]'),
  methodInput: document.querySelector('[name="signature_method"]'),
  exportName: "signature_tech",
  readOnly: false
});
```

**Opciones**:
- `dateInput`: Input de fecha (opcional)
- `methodInput`: Input de método de firma (opcional)
- `exportName`: Nombre para exportar (opcional)
- `readOnly`: Si es solo lectura (default: false)

**Funcionalidades**:
- Captura de firma con mouse/touch
- Exportación como imagen base64
- Validación de firma
- Integración con campos de fecha y método

**Eventos**:
- `signature:changed`: Cuando cambia la firma
- `signature:cleared`: Cuando se limpia
- `signature:exported`: Cuando se exporta

---

### 3. PhotoGallery (Galería de Fotos)

**Función**: `createEvidenceUploader(targetInput, labelText, options)`

**Descripción**: Componente para subir y gestionar evidencias fotográficas.

**Uso**:
```javascript
const input = document.querySelector('[name="evidence_photos"]');
const wrapper = SitecComponents.createEvidenceUploader(input, "Evidencias", {
  maxFiles: 10,
  maxSize: 5 * 1024 * 1024, // 5MB
  accept: "image/*"
});
```

**Opciones**:
- `maxFiles`: Número máximo de archivos (default: 10)
- `maxSize`: Tamaño máximo por archivo en bytes (default: 5MB)
- `accept`: Tipos MIME aceptados (default: "image/*")
- `multiple`: Si permite múltiples archivos (default: true)

**Funcionalidades**:
- Vista previa de imágenes
- Drag & drop
- Validación de tamaño y tipo
- Compresión automática (opcional)
- Geolocalización automática (opcional)

---

### 4. GeoPicker (Geolocalización)

**Función**: `createGeoPicker(targetInput, labelText, options)`

**Descripción**: Componente para capturar coordenadas GPS.

**Uso**:
```javascript
const input = document.querySelector('[name="evidence_geo"]');
const wrapper = SitecComponents.createGeoPicker(input, "Ubicación", {
  accuracy: 10, // metros
  timeout: 5000 // ms
});
```

**Opciones**:
- `accuracy`: Precisión deseada en metros (default: 10)
- `timeout`: Tiempo máximo de espera en ms (default: 5000)
- `showMap`: Si muestra mapa (default: true)

**Funcionalidades**:
- Captura GPS automática
- Visualización en mapa
- Validación de precisión
- Fallback a geocodificación inversa

---

### 5. RiskMatrix (Matriz de Riesgos)

**Función**: `createRiskMatrix(risks)`

**Descripción**: Visualización de matriz de riesgos 5x5.

**Uso**:
```javascript
const risks = [
  {
    id: "uuid",
    title: "Riesgo de seguridad",
    severity: "high",
    probability: "medium"
  }
];
const matrix = SitecComponents.createRiskMatrix(risks);
```

**Estructura de datos**:
```javascript
risks = [
  {
    id: "UUID",
    title: "string",
    severity: "low|medium|high|critical",
    probability: "very_low|low|medium|high|very_high"
  }
]
```

**Funcionalidades**:
- Matriz 5x5 con conteos
- Colores por nivel de riesgo
- Tooltips con detalles
- Filtrado por severidad/probabilidad

**Contrato**:
```javascript
{
  input: {
    project_id: "UUID",
    riesgos: [...]
  },
  output: {
    levels: ["Muy baja", "Baja", "Media", "Alta", "Muy alta"],
    matrix: "5x5 con conteos por celda"
  }
}
```

---

### 6. GanttLite (Gráfico de Gantt Ligero)

**Función**: `createGanttLite(tasks)`

**Descripción**: Visualización de cronograma de tareas.

**Uso**:
```javascript
const tasks = [
  {
    id: "uuid",
    title: "Tarea 1",
    status: "in_progress",
    start_date: "2025-01-01",
    end_date: "2025-01-15"
  }
];
const gantt = SitecComponents.createGanttLite(tasks);
```

**Estructura de datos**:
```javascript
tasks = [
  {
    id: "UUID",
    title: "string",
    status: "pending|in_progress|completed|blocked",
    start_date: "YYYY-MM-DD",
    end_date: "YYYY-MM-DD"
  }
]
```

**Funcionalidades**:
- Barras de progreso por tarea
- Colores por estado
- Filtrado por estado
- Zoom temporal

**Contrato**:
```javascript
{
  input: {
    project_id: "UUID",
    tareas: [...]
  },
  output: {
    rows: [{ name: "string", progress: "0-100" }]
  }
}
```

---

### 7. KanbanBoard (Tablero Kanban)

**Función**: `createKanbanBoard(tasks)`

**Descripción**: Tablero Kanban para gestión de tareas.

**Uso**:
```javascript
const tasks = [
  {
    id: "uuid",
    title: "Tarea 1",
    status: "pending"
  }
];
const kanban = SitecComponents.createKanbanBoard(tasks);
```

**Estructura de datos**:
```javascript
tasks = [
  {
    id: "UUID",
    title: "string",
    status: "pending|in_progress|completed|blocked"
  }
]
```

**Funcionalidades**:
- Columnas por estado
- Drag & drop (básico)
- Conteo de tareas por columna
- Filtrado y búsqueda

**Contrato**:
```javascript
{
  input: {
    project_id: "UUID",
    tareas: [...]
  },
  output: {
    columns: ["Pendiente", "En progreso", "Hecho", "Bloqueado"]
  }
}
```

---

## 🔧 Contrato de Componentes

### Props Estándar

Todos los componentes aceptan estas props:

```javascript
{
  value: any,              // Valor actual
  onChange: function,      // Callback al cambiar
  errors: array,           // Array de errores
  isBlocking: boolean,     // Si bloquea el flujo
  disabledReason: string,  // Razón de deshabilitado
  syncState: string,       // Estado de sync: "offline"|"syncing"|"synced"|"error"
  isOffline: boolean,      // Si está offline
  lastSavedAt: string,     // Timestamp del último guardado
  validationSeverity: string, // "error"|"warning"|"info"
  validationMessage: string   // Mensaje de validación
}
```

### Estados de Sincronización

- `offline`: Sin conexión
- `syncing`: Sincronizando
- `synced`: Sincronizado
- `error`: Error de sincronización

### Modo Campo

Los componentes se adaptan automáticamente al modo campo:

```html
<div data-mode="field">
  <!-- Componentes con tamaños táctiles >= 56px -->
</div>
```

**Características**:
- Tamaños táctiles mínimos (56-64px)
- Contraste AA
- Adaptación automática

---

## 📱 Integración con Wizard

### Inicialización Automática

Los componentes avanzados se inicializan automáticamente en el wizard:

```javascript
// En wizard.js
if (components && components.startAdvancedComponents) {
  const projectId = wizard?.dataset?.projectId || "";
  components.startAdvancedComponents(projectId, { refreshMs: 60000 });
}
```

### Uso Manual

```javascript
// Inicializar componentes avanzados
SitecComponents.initAdvancedComponents(projectId);

// Iniciar con auto-refresh
const stop = SitecComponents.startAdvancedComponents(projectId, {
  refreshMs: 60000 // Refrescar cada 60 segundos
});

// Detener auto-refresh
stop();
```

---

## 🎯 Mejores Prácticas

### 1. Validación

```javascript
const field = {
  name: "email",
  type: "email",
  required: true,
  validation: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: "Email inválido"
  }
};
```

### 2. Condiciones

```javascript
// Mostrar solo si otro campo tiene valor
field.show_if = {
  other_field: "value"
};

// Requerir si otro campo tiene valor
field.required_if = {
  other_field: "value"
};
```

### 3. Offline

```javascript
// Verificar estado offline
if (navigator.onLine) {
  // Sincronizar
} else {
  // Guardar localmente
}
```

### 4. Accesibilidad

- Usar `aria-required` para campos requeridos
- Usar `aria-label` para etiquetas
- Usar `aria-describedby` para mensajes de ayuda
- Mantener contraste AA mínimo

---

## 📚 Ejemplos Completos

### Ejemplo 1: Campo de Texto con Validación

```javascript
const field = {
  name: "project_name",
  type: "text",
  label: "Nombre del proyecto",
  required: true,
  placeholder: "Ingrese el nombre",
  validation: {
    minLength: 3,
    maxLength: 100,
    message: "El nombre debe tener entre 3 y 100 caracteres"
  }
};
const input = SitecComponents.createField(field);
container.appendChild(input);
```

### Ejemplo 2: Firma Digital Completa

```javascript
const signatureInput = document.querySelector('[name="signature_tech"]');
const dateInput = document.querySelector('[name="signature_date"]');
const methodInput = document.querySelector('[name="signature_method"]');

const wrapper = SitecComponents.createSignaturePad(
  signatureInput,
  "Firma Técnico",
  {
    dateInput: dateInput,
    methodInput: methodInput,
    exportName: "signature_tech",
    readOnly: false
  }
);

wrapper.addEventListener("signature:changed", (e) => {
  console.log("Firma capturada:", e.detail.dataUrl);
});
```

### Ejemplo 3: Matriz de Riesgos con Datos Reales

```javascript
async function loadRiskMatrix(projectId) {
  const response = await fetch(`/api/projects/proyectos/${projectId}/`);
  const data = await response.json();
  const risks = data.riesgos || [];
  
  const matrix = SitecComponents.createRiskMatrix(risks);
  document.getElementById("riskMatrixContainer").appendChild(matrix);
}
```

---

## 🔍 Debugging

### Verificar Contratos

```javascript
// Ver contratos disponibles
console.log(SitecComponents.contracts);

// Verificar contrato de un componente
console.log(SitecComponents.contracts.riskMatrix);
```

### Verificar Estado de Componentes

```javascript
// Ver estado de sync
const wrapper = document.querySelector('[data-component="signature-pad"]');
console.log(wrapper.dataset.state); // "synced", "syncing", "error", etc.
```

---

## 📝 Checklist de Implementación

- [x] Componentes base (TextField, NumberField, SelectField, DateField, Textarea)
- [x] Componentes avanzados (SignaturePad, PhotoGallery, GeoPicker)
- [x] Componentes de visualización (RiskMatrix, GanttLite, KanbanBoard)
- [x] Contrato de props estándar
- [x] Estados de sincronización
- [x] Modo campo
- [x] Integración con wizard
- [x] Validación y reglas
- [x] Accesibilidad AA
- [x] Documentación completa

---

**Última actualización**: 2026-01-18
