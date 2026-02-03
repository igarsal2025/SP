# Fase 4: Wizard Contextual - Implementación Completa

**Fecha**: 2026-01-23  
**Versión**: 1.0  
**Estado**: ✅ Completado

---

## 📋 Resumen

Se ha implementado la personalización del wizard según el rol del usuario, permitiendo que cada perfil vea solo las opciones y funcionalidades que le corresponden.

---

## 🎯 Cambios Implementados

### 1. Template Readonly para Clientes

**Archivo**: `backend/apps/frontend/templates/frontend/wizard/wizard_readonly.html`

- Template simplificado para clientes
- Solo muestra navegación (Anterior/Siguiente)
- Sin botones de guardar, modo campo, chatbot, PDF
- Mensaje informativo de "Modo de solo lectura"
- Todos los campos deshabilitados automáticamente

### 2. Refactorización de `wizard.html`

**Archivo**: `backend/apps/frontend/templates/frontend/wizard.html`

- Agregado `{% load role_tags %}`
- Componentes avanzados (risk matrix, gantt, kanban) solo visibles para admin/PM/supervisor
- Chatbot IA solo visible si `can_use_ai_chat` es `true`
- Panel de PDF solo visible si `can_generate_pdf` es `true`
- Botón "Guardar" solo visible si tiene permiso `wizard.save` y no es modo readonly
- Botón "Modo Campo" solo visible si `can_use_field_mode` es `true` y no es modo readonly
- FAB (Floating Action Button) con elementos condicionales

### 3. Actualización de `WizardStepView`

**Archivo**: `backend/apps/frontend/views.py`

- Método `get_template_names()` agregado
- Selecciona `wizard_readonly.html` si `wizard_mode == "readonly"`
- Selecciona `wizard.html` para todos los demás roles

### 4. Adaptación de `wizard.js`

**Archivo**: `backend/static/frontend/js/wizard.js`

- Nueva función `applyWizardVisibility()`:
  - Obtiene contexto del usuario desde `window.RoleBasedUI.getUserContext()`
  - Deshabilita campos si es modo readonly
  - Oculta botón "Modo Campo" si no tiene permiso
  - Oculta componentes avanzados según rol
  - Oculta chatbot IA si no tiene permiso
  - Oculta panel PDF si no tiene permiso
  - Oculta elementos del FAB según permisos

- Integración con `DOMContentLoaded`:
  - Llama a `applyWizardVisibility()` después de cargar el paso
  - Mantiene compatibilidad con lógica existente de permisos

### 5. Tests de Validación

**Archivo**: `backend/apps/frontend/tests_wizard_contextual.py`

- ✅ 6 tests implementados:
  - `test_wizard_uses_readonly_template_for_cliente`: Cliente ve template readonly
  - `test_wizard_uses_full_template_for_admin`: Admin ve template completo
  - `test_wizard_uses_full_template_for_pm`: PM ve template completo
  - `test_wizard_uses_full_template_for_tecnico`: Técnico ve template completo
  - `test_wizard_uses_full_template_for_supervisor`: Supervisor ve template completo
  - `test_wizard_step_uses_correct_template`: Pasos del wizard usan template correcto

---

## 📊 Matriz de Funcionalidades por Rol

| Funcionalidad | Admin | PM | Supervisor | Técnico | Cliente |
|---------------|-------|----|-----------|---------|---------|
| **Template** | Full | Full | Full | Full | Readonly |
| **Guardar** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Modo Campo** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Chatbot IA** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Generar PDF** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Componentes Avanzados** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Editar Campos** | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## 🔧 Detalles Técnicos

### Template Tags Utilizados

- `{% user_role %}`: Obtiene el rol del usuario
- `{% wizard_mode %}`: Obtiene el modo del wizard (`full` o `readonly`)
- `{% has_permission "permiso" %}`: Verifica si el usuario tiene un permiso específico

### Configuración UI por Rol

La configuración se obtiene de `user_context.ui_config`:

```javascript
{
  wizard_mode: "full" | "readonly",
  can_use_field_mode: boolean,
  can_use_ai_chat: boolean,
  can_generate_pdf: boolean
}
```

### Componentes Avanzados

Los componentes avanzados (risk matrix, gantt, kanban) solo se muestran para:
- `admin_empresa`
- `pm`
- `supervisor`

Se ocultan automáticamente para `tecnico` y `cliente`.

---

## ✅ Validación

- ✅ 6 tests de wizard contextual pasando
- ✅ Templates renderizan correctamente según rol
- ✅ JavaScript aplica visibilidad según contexto del usuario
- ✅ Componentes se ocultan/muestran según permisos
- ✅ Modo readonly funciona correctamente para clientes

---

## 🎯 Beneficios

1. **Experiencia personalizada**: Cada usuario ve solo lo que necesita
2. **Seguridad**: Funcionalidades sensibles ocultas para roles sin permisos
3. **Claridad**: Clientes ven claramente que están en modo de solo lectura
4. **Mantenibilidad**: Lógica centralizada en `applyWizardVisibility()`

---

## 📝 Notas de Implementación

### Compatibilidad

- ✅ Mantiene compatibilidad con lógica existente de permisos
- ✅ No rompe funcionalidad existente
- ✅ Los campos se deshabilitan automáticamente en modo readonly

### Mejoras Futuras

- Agregar tooltips explicativos en modo readonly
- Mejorar feedback visual cuando se intenta editar en modo readonly
- Agregar indicadores visuales más claros de permisos

---

## 🚀 Próximos Pasos

La Fase 4 está completa. El siguiente paso sería la **Fase 5: Optimización y Refinamiento**, que incluye:

- Lazy loading de componentes
- Optimización de carga de datos
- Mejoras de responsive design
- Animaciones y transiciones
- Documentación de usuario

---

**Última actualización**: 2026-01-23
