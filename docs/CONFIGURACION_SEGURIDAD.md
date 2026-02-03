# Configuración de Seguridad - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Resumen

Esta guía describe la configuración de seguridad del sistema SITEC, incluyendo rate limiting, security headers y health checks. **Todas las configuraciones son opcionales** - el sistema funciona sin ellas.

---

## 🔒 Rate Limiting

### Descripción

Rate limiting protege el sistema contra abuso y ataques de fuerza bruta limitando el número de requests por IP en una ventana de tiempo.

### Configuración

**Variables de Entorno** (todas opcionales):

```bash
# Habilitar rate limiting (default: false)
RATE_LIMIT_ENABLED=true

# Número máximo de requests por ventana (default: 100)
RATE_LIMIT_REQUESTS=100

# Ventana de tiempo en segundos (default: 60)
RATE_LIMIT_WINDOW=60
```

### Comportamiento

- **Deshabilitado** (por defecto): No aplica rate limiting
- **Habilitado**: Limita requests por IP según configuración
- **Respuesta 429**: Cuando se excede el límite

### Ejemplo de Respuesta

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Maximum 100 requests per 60 seconds."
}
```

### Recomendaciones

- **Desarrollo**: Mantener deshabilitado
- **Producción**: Habilitar con valores apropiados
  - `RATE_LIMIT_REQUESTS=200` para usuarios normales
  - `RATE_LIMIT_REQUESTS=50` para endpoints sensibles

---

## 🛡️ Security Headers

### Headers Implementados

El sistema incluye los siguientes headers de seguridad:

1. **X-Content-Type-Options: nosniff**
   - Previene MIME type sniffing

2. **X-Frame-Options: DENY**
   - Previene clickjacking

3. **X-XSS-Protection: 1; mode=block**
   - Habilita protección XSS del navegador

4. **Referrer-Policy: strict-origin-when-cross-origin**
   - Controla información de referrer

5. **Content-Security-Policy** (opcional)
   - Política de seguridad de contenido

### Configuración CSP

**Variables de Entorno** (opcionales):

```bash
# Habilitar CSP (default: false)
CSP_ENABLED=true

# Directivas CSP
CSP_DEFAULT_SRC='self'
CSP_SCRIPT_SRC='self' 'unsafe-inline'
CSP_STYLE_SRC='self' 'unsafe-inline'
CSP_IMG_SRC='self' data: https:
CSP_FONT_SRC='self' data:
CSP_CONNECT_SRC='self'
```

### Verificar Headers

```bash
# Verificar headers de seguridad
curl -I http://localhost:8000/

# Debería incluir:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Referrer-Policy: strict-origin-when-cross-origin
```

### Recomendaciones

- **Desarrollo**: CSP deshabilitado (puede interferir con desarrollo)
- **Producción**: Habilitar CSP y ajustar según necesidades

---

## 🏥 Health Checks

### Endpoints Disponibles

#### 1. Health Check Básico

**Endpoint**: `GET /health/`

**Características**:
- Sin autenticación requerida
- Respuesta rápida
- Útil para load balancers

**Respuesta**:
```json
{
  "status": "ok",
  "service": "SITEC",
  "version": "1.0.0"
}
```

#### 2. Health Check Detallado

**Endpoint**: `GET /health/detailed/`

**Características**:
- Sin autenticación requerida
- Verifica dependencias:
  - Base de datos
  - Cache
  - Proveedores opcionales

**Respuesta**:
```json
{
  "status": "ok",
  "service": "SITEC",
  "version": "1.0.0",
  "dependencies": {
    "database": {
      "status": "ok",
      "message": "Database connection successful"
    },
    "cache": {
      "status": "ok",
      "message": "Cache connection successful"
    },
    "nom151": {
      "status": "optional",
      "message": "NOM-151 provider not configured (optional)"
    },
    "ai": {
      "status": "optional",
      "message": "AI provider not configured (using local providers)"
    }
  }
}
```

**Status Codes**:
- `200`: Todas las dependencias críticas funcionando
- `503`: Alguna dependencia crítica fallando

### Uso con Load Balancers

```nginx
# Nginx
location /health {
    proxy_pass http://backend/health/;
    access_log off;
}

# Kubernetes
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/detailed/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## 🔧 Configuración Completa

### Ejemplo de `.env` para Producción

```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60

# CSP Headers
CSP_ENABLED=true
CSP_DEFAULT_SRC='self'
CSP_SCRIPT_SRC='self' 'unsafe-inline'
CSP_STYLE_SRC='self' 'unsafe-inline'
CSP_IMG_SRC='self' data: https:
CSP_FONT_SRC='self' data:
CSP_CONNECT_SRC='self'

# Security Headers (siempre activos)
SECURE_CONTENT_TYPE_NOSNIFF=true
SECURE_BROWSER_XSS_FILTER=true
X_FRAME_OPTIONS=DENY
SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
```

### Ejemplo de `.env` para Desarrollo

```bash
# Rate Limiting deshabilitado
RATE_LIMIT_ENABLED=false

# CSP deshabilitado (puede interferir con desarrollo)
CSP_ENABLED=false
```

---

## ✅ Checklist de Seguridad

### Desarrollo

- [ ] Rate limiting deshabilitado
- [ ] CSP deshabilitado
- [ ] Security headers básicos activos (siempre)

### Producción

- [ ] Rate limiting habilitado y configurado
- [ ] CSP habilitado y ajustado según necesidades
- [ ] Security headers verificados
- [ ] Health checks configurados en load balancer
- [ ] Monitoreo de health checks configurado

---

## 📚 Referencias

- `docs/PROVEEDORES_OPCIONALES.md` - Proveedores externos opcionales
- `docs/RESUMEN_MEJORAS_P1.md` - Resumen de mejoras P1
- `backend/config/settings.py` - Configuración completa

---

**Última actualización**: 2026-01-18
