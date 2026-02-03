# Proveedores Externos Opcionales

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Resumen

El sistema SITEC está diseñado para funcionar **completamente sin proveedores externos**. Todas las integraciones con terceros son **opcionales** y el sistema funciona de manera autónoma sin ellas.

---

## ✅ Integraciones Opcionales

### 1. NOM-151 (Timbrado de Documentos)

**Estado**: ✅ **Opcional** - Sistema funciona sin proveedor

**Comportamiento sin proveedor**:
- Los documentos PDF se generan correctamente
- El sello NOM-151 se marca como "pendiente"
- El sistema funciona normalmente para todos los demás casos de uso

**Configuración**:
```bash
# Opcional - Solo si se requiere timbrado real
NOM151_PROVIDER_URL=https://proveedor-nom151.com/api/stamp
NOM151_API_KEY=tu_api_key_aqui
```

**Código relevante**:
- `backend/apps/documents/services.py` - Función `request_nom151_stamp()`
- Si `NOM151_PROVIDER_URL` está vacío, retorna `"pendiente"` con status `"disabled"`

**Mensaje cuando está deshabilitado**:
```
"Proveedor NOM-151 no configurado. El documento se genera correctamente sin timbrado real."
```

---

### 2. IA Real (Proveedor ML Externo)

**Estado**: ✅ **Opcional** - Sistema funciona sin proveedor

**Comportamiento sin proveedor**:
- Los proveedores locales funcionan sin configuración:
  - `RuleProvider`: Motor de reglas básicas
  - `LightModelProvider`: Modelo ligero local
  - `HeavyProvider`: Modelo pesado local
- Las sugerencias IA funcionan normalmente
- El entrenamiento de modelos se marca como "dataset_ready" sin envío externo

**Configuración**:
```bash
# Opcional - Solo si se requiere entrenamiento con proveedor ML externo
AI_TRAIN_PROVIDER_URL=https://proveedor-ml.com/api/train
AI_TRAIN_API_KEY=tu_api_key_aqui
```

**Código relevante**:
- `backend/apps/ai/pipeline.py` - Función `submit_training_job()`
- Si `AI_TRAIN_PROVIDER_URL` está vacío, el job se marca como `"dataset_ready"` con provider `"disabled"`

**Mensaje cuando está deshabilitado**:
```
"Proveedor ML externo no configurado. El sistema funciona con proveedores locales."
```

---

## 🔧 Configuración Mínima

### Variables de Entorno Requeridas

**Ninguna** - El sistema funciona sin configuración de proveedores externos.

### Variables de Entorno Opcionales

```bash
# NOM-151 (Opcional)
NOM151_PROVIDER_URL=          # Vacío por defecto
NOM151_API_KEY=               # Vacío por defecto
NOM151_TIMEOUT=15             # Opcional
NOM151_VERIFY_SSL=true        # Opcional
NOM151_RETRIES=1              # Opcional
NOM151_BACKOFF_BASE=0.5       # Opcional
NOM151_PROVIDER_MODE=json     # Opcional
NOM151_SEND_PDF=false         # Opcional

# IA Real (Opcional)
AI_TRAIN_PROVIDER_URL=        # Vacío por defecto
AI_TRAIN_API_KEY=             # Vacío por defecto
AI_TRAIN_TIMEOUT=20           # Opcional
AI_TRAIN_VERIFY_SSL=true      # Opcional
AI_TRAIN_RETRIES=1            # Opcional
AI_TRAIN_BACKOFF_BASE=0.5     # Opcional
AI_TRAIN_SEND_FILE=false      # Opcional
```

---

## 📊 Funcionalidades por Modo

### Modo Sin Proveedores Externos (Por Defecto)

| Funcionalidad | Estado | Comportamiento |
|---------------|--------|----------------|
| **Generación de PDFs** | ✅ Funciona | PDFs se generan correctamente |
| **Sello NOM-151** | ⚠️ Pendiente | Se marca como "pendiente" |
| **Sugerencias IA** | ✅ Funciona | Usa proveedores locales (RuleProvider, LightModelProvider) |
| **Entrenamiento IA** | ⚠️ Local | Dataset se prepara pero no se envía externamente |
| **Dashboard** | ✅ Funciona | Todas las métricas funcionan |
| **Wizard** | ✅ Funciona | Todos los pasos funcionan |
| **ABAC** | ✅ Funciona | Sistema de permisos funciona |
| **Comparativos** | ✅ Funciona | Comparativos históricos funcionan |

### Modo Con Proveedores Externos (Opcional)

| Funcionalidad | Estado | Comportamiento |
|---------------|--------|----------------|
| **Generación de PDFs** | ✅ Funciona | PDFs se generan correctamente |
| **Sello NOM-151** | ✅ Real | Se obtiene sello real del proveedor |
| **Sugerencias IA** | ✅ Funciona | Usa proveedores locales + externos si están configurados |
| **Entrenamiento IA** | ✅ Externo | Dataset se envía al proveedor ML externo |

---

## 🚀 Instalación y Configuración

### Instalación Básica (Sin Proveedores Externos)

```bash
# 1. Clonar repositorio
git clone <repo>

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver
```

**No se requiere configuración adicional** - El sistema funciona completamente.

### Configuración con Proveedores Externos (Opcional)

Si deseas habilitar proveedores externos:

```bash
# 1. Configurar NOM-151 (opcional)
export NOM151_PROVIDER_URL="https://proveedor-nom151.com/api/stamp"
export NOM151_API_KEY="tu_api_key"

# 2. Configurar IA Real (opcional)
export AI_TRAIN_PROVIDER_URL="https://proveedor-ml.com/api/train"
export AI_TRAIN_API_KEY="tu_api_key"

# 3. Reiniciar servidor
python manage.py runserver
```

---

## 🔍 Verificación de Estado

### Verificar Estado de NOM-151

```python
from django.conf import settings

if settings.NOM151_PROVIDER_URL:
    print("✅ NOM-151 configurado")
else:
    print("⚠️ NOM-151 no configurado - funcionando en modo pendiente")
```

### Verificar Estado de IA

```python
from django.conf import settings

if settings.AI_TRAIN_PROVIDER_URL:
    print("✅ IA Real configurado")
else:
    print("⚠️ IA Real no configurado - funcionando con proveedores locales")
```

### Verificar en Documentos Generados

```python
from apps.documents.models import Document

document = Document.objects.first()
if document.nom151_stamp == "pendiente":
    print("⚠️ Documento sin timbrado real (proveedor no configurado)")
else:
    print(f"✅ Documento timbrado: {document.nom151_stamp}")
```

---

## 📝 Logs y Mensajes

### Logs de NOM-151

Cuando el proveedor no está configurado:
```
INFO: NOM151 provider no configurado - documento generado sin timbrado real
```

### Logs de IA

Cuando el proveedor no está configurado:
```
INFO: AI training provider no configurado para job {job_id} - 
el sistema funciona con proveedores locales (RuleProvider, LightModelProvider)
```

---

## ⚠️ Consideraciones

### NOM-151

- **Sin proveedor**: Los documentos se generan con sello "pendiente"
- **Con proveedor**: Los documentos se timbran automáticamente
- **Impacto**: Sin impacto en funcionalidad básica del sistema

### IA Real

- **Sin proveedor**: Se usan proveedores locales (RuleProvider, LightModelProvider, HeavyProvider)
- **Con proveedor**: Se puede enviar entrenamiento a proveedor externo
- **Impacto**: Sin impacto en funcionalidad básica del sistema

---

## 🎯 Recomendaciones

### Para Desarrollo

- **No configurar proveedores externos** - El sistema funciona completamente sin ellos
- Usar proveedores locales para desarrollo y testing

### Para Producción

- **Evaluar necesidad** de proveedores externos según requisitos de negocio
- Si se requiere timbrado real, configurar NOM-151
- Si se requiere entrenamiento ML externo, configurar IA Real
- **El sistema funciona perfectamente sin ellos**

---

## 📚 Documentación Relacionada

- `docs/CONFIGURACION_NOM151.md` - Guía de configuración NOM-151 (opcional)
- `backend/config/settings.py` - Configuración de variables de entorno
- `backend/apps/documents/services.py` - Lógica de timbrado NOM-151
- `backend/apps/ai/pipeline.py` - Lógica de entrenamiento IA

---

## ✅ Checklist de Verificación

- [x] Sistema funciona sin NOM-151 configurado
- [x] Sistema funciona sin IA Real configurado
- [x] Documentos se generan correctamente sin timbrado
- [x] Sugerencias IA funcionan con proveedores locales
- [x] Logs informan cuando proveedores no están configurados
- [x] Settings documentan que son opcionales
- [x] Código maneja gracefully cuando no hay proveedores

---

**Última actualización**: 2026-01-18
