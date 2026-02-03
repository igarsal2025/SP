# Guía de Configuración ABAC - Políticas de Acceso

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

El sistema SITEC utiliza un modelo **ABAC (Attribute-Based Access Control)** híbrido con RBAC para controlar el acceso a funcionalidades según roles, condiciones y contexto.

---

## 🎯 Conceptos Básicos

### Política de Acceso

Una política define:
- **Acción**: Qué acción se está evaluando (ej: `wizard.save`, `dashboard.view`)
- **Condiciones**: Atributos requeridos (ej: `role: "pm"`)
- **Efecto**: `allow` o `deny`
- **Prioridad**: Número mayor = mayor prioridad

### Evaluación

El sistema evalúa políticas en orden de prioridad:
1. Políticas con mayor prioridad primero
2. Si una política coincide, se aplica su efecto
3. Si ninguna coincide, se aplica la política base (`*`)

---

## 👥 Roles Disponibles

- **`admin_empresa`**: Administrador de empresa (acceso completo)
- **`pm`**: Project Manager (gestión de proyectos y dashboard)
- **`supervisor`**: Supervisor (aprobaciones y supervisión)
- **`tecnico`**: Técnico (operación y reportes)
- **`cliente`**: Cliente (solo lectura)

---

## 📝 Catálogo de Políticas Base

### Wizard

```python
# Acceso general
{"action": "wizard.*", "conditions": {"role": "tecnico"}, "priority": 5}
{"action": "wizard.*", "conditions": {"role": "supervisor"}, "priority": 5}
{"action": "wizard.*", "conditions": {"role": "pm"}, "priority": 5}

# Acciones específicas
{"action": "wizard.save", "conditions": {"role": "tecnico"}, "priority": 6}
{"action": "wizard.submit", "conditions": {"role": "supervisor"}, "priority": 6}

# Pasos específicos
{"action": "wizard.step.11.view", "conditions": {"role": "tecnico"}, "priority": 7}
{"action": "wizard.step.12.view", "conditions": {"role": "supervisor"}, "priority": 7}
```

### Dashboard

```python
{"action": "dashboard.view", "conditions": {"role": "pm"}, "priority": 5}
{"action": "dashboard.trends.view", "conditions": {"role": "pm"}, "priority": 6}
{"action": "dashboard.export", "conditions": {"role": "pm"}, "priority": 6}
```

### IA y Documentos

```python
{"action": "ai.suggest", "conditions": {"role": "tecnico"}, "priority": 5}
{"action": "ai.stats.view", "conditions": {"role": "pm"}, "priority": 6}
{"action": "documents.generate", "conditions": {"role": "tecnico"}, "priority": 5}
{"action": "documents.download", "conditions": {"role": "cliente"}, "priority": 5}
```

### Reportes y Proyectos

```python
{"action": "reports.*", "conditions": {"role": "tecnico"}, "priority": 5}
{"action": "reports.approve", "conditions": {"role": "supervisor"}, "priority": 6}
{"action": "projects.create", "conditions": {"role": "pm"}, "priority": 6}
{"action": "projects.edit", "conditions": {"role": "pm"}, "priority": 6}
```

---

## 🔧 Configuración de Políticas

### Crear Nueva Política

```python
from apps.accounts.models import AccessPolicy

AccessPolicy.objects.create(
    company=company,
    action="wizard.custom_action",
    conditions={"role": "tecnico", "department": "IT"},
    effect="allow",
    priority=10,
    is_active=True,
)
```

### Modificar Política Existente

```python
policy = AccessPolicy.objects.get(
    company=company,
    action="dashboard.view",
    conditions={"role": "tecnico"}
)
policy.effect = "deny"
policy.priority = 15
policy.save()
```

### Desactivar Política

```python
policy.is_active = False
policy.save()
```

---

## 🎨 Patrones de Acción

### Acciones con Wildcard

- `wizard.*`: Todas las acciones de wizard
- `dashboard.*`: Todas las acciones de dashboard
- `reports.*`: Todas las acciones de reportes

### Acciones Específicas

- `wizard.save`: Guardar wizard
- `wizard.submit`: Enviar wizard
- `wizard.step.11.view`: Ver paso 11
- `dashboard.view`: Ver dashboard
- `dashboard.trends.view`: Ver tendencias

---

## 🔍 Condiciones Avanzadas

### Condiciones Múltiples

```python
{
    "action": "wizard.submit",
    "conditions": {
        "role": "supervisor",
        "department": "Operations",
        "method": "post"
    },
    "priority": 10
}
```

### Condiciones Dinámicas

```python
{
    "action": "wizard.signature.require.supervisor",
    "conditions": {
        "signature_supervisor_required": "true"
    },
    "priority": 20
}
```

---

## 🚀 Uso en Frontend

### JavaScript Helper

```javascript
// Verificar permiso
const canSave = await permissions.can("wizard.save");
if (canSave) {
    // Permitir guardar
}

// Verificar múltiples permisos
const permissions = await permissions.canMultiple([
    "wizard.save",
    "wizard.submit"
]);
```

### Integración en Wizard

```javascript
// Ocultar/mostrar según permiso
await permissions.toggleByPermission(
    "#saveButton",
    "wizard.save"
);

// Validar antes de acción
if (!(await permissions.can("wizard.submit"))) {
    alert("No tienes permiso para enviar");
    return;
}
```

---

## 📊 Prioridades Recomendadas

- **0-4**: Políticas base (wildcards generales)
- **5-9**: Políticas por rol
- **10-19**: Políticas específicas por acción
- **20+**: Políticas condicionales avanzadas

---

## ✅ Mejores Prácticas

1. **Usar prioridades consistentes**: Agrupar políticas similares
2. **Documentar políticas complejas**: Agregar comentarios en código
3. **Probar en desarrollo**: Validar antes de producción
4. **Revisar periódicamente**: Ajustar según necesidades de negocio
5. **Usar condiciones específicas**: Evitar políticas demasiado amplias

---

## 🔐 Seguridad

- Las políticas se evalúan en el servidor (backend)
- El frontend solo oculta/muestra elementos (UX)
- Siempre validar en backend antes de ejecutar acciones
- Usar `deny` explícito para restricciones críticas

---

## 📝 Ejemplos Comunes

### Permitir solo lectura a cliente

```python
AccessPolicy.objects.create(
    company=company,
    action="wizard.*",
    conditions={"role": "cliente", "method": "get"},
    effect="allow",
    priority=5,
)
AccessPolicy.objects.create(
    company=company,
    action="wizard.save",
    conditions={"role": "cliente"},
    effect="deny",
    priority=15,
)
```

### Restringir dashboard a PM y admin

```python
AccessPolicy.objects.create(
    company=company,
    action="dashboard.*",
    conditions={"role": "pm"},
    effect="allow",
    priority=5,
)
AccessPolicy.objects.create(
    company=company,
    action="dashboard.*",
    conditions={"role": "admin_empresa"},
    effect="allow",
    priority=5,
)
```

---

**Última actualización**: 2026-01-18
