# Configuración de Integración NOM-151 (Opcional)

> **⚠️ IMPORTANTE**: La configuración de NOM-151 es **completamente opcional**. El sistema funciona perfectamente sin proveedor configurado. Los documentos se generan con sello "pendiente" cuando no hay proveedor. Ver `docs/PROVEEDORES_OPCIONALES.md` para más información.

## 📋 Resumen

La integración con proveedores de timbrado NOM-151 está implementada y lista para usar. **Es completamente opcional** - el sistema funciona sin ella. Si deseas habilitar timbrado real, solo requiere configurar las variables de entorno con las credenciales del proveedor.

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# URL del proveedor de timbrado NOM-151
NOM151_PROVIDER_URL=https://api.proveedor-nom151.com/v1/timbrar

# API Key del proveedor
NOM151_API_KEY=tu_api_key_aqui

# Timeout en segundos (default: 15)
NOM151_TIMEOUT=15

# Verificar certificados SSL (default: true)
NOM151_VERIFY_SSL=true

# Número de reintentos en caso de error (default: 1)
NOM151_RETRIES=3

# Base del backoff exponencial en segundos (default: 0.5)
NOM151_BACKOFF_BASE=0.5

# Modo de envío: "json" o "multipart" (default: json)
NOM151_PROVIDER_MODE=json

# Enviar PDF en el request (default: false)
NOM151_SEND_PDF=false
```

### Configuración en `.env`

Crear o editar el archivo `.env` en la raíz del proyecto:

```env
# NOM-151 Provider Configuration
NOM151_PROVIDER_URL=https://api.proveedor-nom151.com/v1/timbrar
NOM151_API_KEY=tu_api_key_secreta
NOM151_TIMEOUT=15
NOM151_VERIFY_SSL=true
NOM151_RETRIES=3
NOM151_BACKOFF_BASE=0.5
NOM151_PROVIDER_MODE=json
NOM151_SEND_PDF=false
```

## 🔌 Proveedores Compatibles

La integración es compatible con proveedores que soporten:

### Modo JSON (Recomendado)
- **Endpoint**: POST a `NOM151_PROVIDER_URL`
- **Headers**: 
  - `Authorization: Bearer {API_KEY}`
  - `Content-Type: application/json`
- **Body**:
```json
{
  "document_id": "uuid-del-documento",
  "report_id": "uuid-del-reporte",
  "file_name": "reporte_semanal_v1.pdf",
  "file_size": 12345,
  "checksum_sha256": "hash-sha256-del-archivo",
  "issued_at": "2026-01-18T10:30:00Z"
}
```
- **Respuesta Esperada**:
```json
{
  "nom151_stamp": "folio-o-sello-nom151",
  "status": "ok"
}
```

### Modo Multipart
- **Endpoint**: POST a `NOM151_PROVIDER_URL`
- **Headers**: 
  - `Authorization: Bearer {API_KEY}`
  - `Content-Type: multipart/form-data`
- **Body**: Form-data con campos JSON + archivo PDF (opcional)

## 🧪 Pruebas

### Prueba Manual

1. **Configurar variables de entorno**:
```bash
export NOM151_PROVIDER_URL=https://api.proveedor-nom151.com/v1/timbrar
export NOM151_API_KEY=tu_api_key
```

2. **Generar un documento de prueba**:
```bash
cd backend
python manage.py shell
```

```python
from apps.documents.models import Document
from apps.reports.models import ReporteSemanal
from apps.documents.services import generate_report_pdf

# Obtener o crear un reporte
report = ReporteSemanal.objects.first()

# Crear documento
document = Document.objects.create(
    report=report,
    version=1,
    status="pending"
)

# Generar PDF con timbrado
document = generate_report_pdf(document)

# Verificar sello
print(f"Sello NOM-151: {document.nom151_stamp}")
print(f"Métricas: {document.metadata.get('nom151', {})}")
```

### Prueba con Mock (Desarrollo)

Para desarrollo sin proveedor real, la integración retornará `"pendiente"` cuando `NOM151_PROVIDER_URL` esté vacío.

## 📊 Monitoreo

Las métricas de timbrado se guardan en `Document.metadata['nom151']`:

```json
{
  "nom151": {
    "latency_ms": 250,
    "attempts": 1,
    "success": true,
    "status": "ok"
  }
}
```

### Estados Posibles

- `"ok"`: Timbrado exitoso
- `"empty"`: Respuesta sin sello
- `"error"`: Error en la comunicación
- `"disabled"`: Proveedor no configurado
- `"cached"`: Sello obtenido de caché

## ⚠️ Manejo de Errores

La integración incluye:

- ✅ Reintentos automáticos con backoff exponencial
- ✅ Timeout configurable
- ✅ Manejo de errores HTTP/SSL
- ✅ Logging de errores
- ✅ Fallback a "pendiente" si falla

### Logs

Los errores se registran en el logger de Django:
```python
import logging
logger = logging.getLogger('apps.documents.services')
```

## 🔒 Seguridad

- ✅ API Key almacenada en variables de entorno (nunca en código)
- ✅ Verificación SSL configurable
- ✅ Timeout para prevenir bloqueos
- ✅ Checksum SHA256 para validación de integridad

## 📝 Notas de Implementación

- El sello se obtiene **después** de generar el PDF inicial
- Si el timbrado es exitoso, el PDF se regenera con el sello
- El sello se guarda en `Document.nom151_stamp`
- Si el proveedor no está configurado, el sistema funciona con sello "pendiente"

## 🚀 Próximos Pasos

1. **Seleccionar proveedor**: Elegir proveedor de timbrado NOM-151
2. **Obtener credenciales**: Solicitar API key del proveedor
3. **Configurar entorno**: Agregar variables de entorno
4. **Probar integración**: Ejecutar prueba end-to-end
5. **Validar PDFs**: Verificar que los sellos aparecen correctamente

## 📚 Referencias

- Código: `backend/apps/documents/services.py`
- Configuración: `backend/config/settings.py` (líneas 151-159)
- Modelo: `backend/apps/documents/models.py`
