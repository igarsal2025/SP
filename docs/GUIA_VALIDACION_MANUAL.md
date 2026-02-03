# Guía de Validación Manual - SITEC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📋 Introducción

Esta guía proporciona instrucciones paso a paso para validar manualmente todas las funcionalidades implementadas en el sistema SITEC.

---

## 🎯 Checklist de Validación

### 1. Health Checks ✅

#### Validación Básica

1. Abrir navegador
2. Navegar a: `http://localhost:8000/health/`
3. **Esperado**: Respuesta JSON con `{"status": "ok"}`

#### Validación Detallada

1. Navegar a: `http://localhost:8000/health/detailed/`
2. **Esperado**: Respuesta JSON con:
   - `database`: `"ok"`
   - `cache`: `"ok"`
   - `providers`: Información de proveedores opcionales

**Scripts**:
```bash
# Linux/Mac
curl http://localhost:8000/health/

# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health/
```

---

### 2. Dashboard y KPIs ✅

#### Validar Carga de KPIs

1. Iniciar sesión en el sistema
2. Navegar a: `/dashboard/`
3. **Esperado**: Panel de KPIs visible con:
   - Total de reportes
   - Reportes enviados
   - Proyectos activos
   - Riesgos altos

#### Validar Comparativos

1. En el dashboard, buscar sección "Comparativos Históricos"
2. **Esperado**: Tarjetas mostrando:
   - Comparativo mes anterior (MoM)
   - Comparativo año anterior (YoY)
   - Valores con deltas y porcentajes

**Verificar**:
- [ ] KPIs se cargan correctamente
- [ ] Comparativos muestran valores numéricos
- [ ] Deltas se muestran con colores (verde/rojo)
- [ ] Porcentajes se calculan correctamente

---

### 3. Tendencias Históricas ✅

#### Validar Carga de Tendencias

1. En el dashboard, buscar panel "Tendencias Históricas"
2. Seleccionar tipo de período: **Mensual**
3. Seleccionar número de períodos: **12**
4. Hacer clic en **"Cargar"** (si hay botón) o esperar carga automática
5. **Esperado**: Gráficos SVG mostrando tendencias de:
   - Reportes
   - Reportes Enviados
   - Proyectos Creados
   - Riesgos Altos

#### Validar Tooltips

1. Pasar el mouse sobre cualquier punto de un gráfico
2. **Esperado**: Tooltip aparece mostrando:
   - Período (fecha)
   - Valor numérico
   - Delta porcentual (si está disponible)

**Verificar**:
- [ ] Tooltips aparecen al pasar el mouse
- [ ] Información es correcta
- [ ] Tooltip se posiciona correctamente

#### Validar Exportación

1. En cualquier gráfico, hacer clic en botón **"Exportar"**
2. Seleccionar formato: **PNG** o **SVG**
3. **Esperado**: Archivo se descarga automáticamente

**Verificar**:
- [ ] Menú de exportación aparece
- [ ] PNG se descarga correctamente
- [ ] SVG se descarga correctamente
- [ ] Archivos tienen nombres descriptivos

#### Validar Alertas Visuales

1. Buscar gráficos con tendencias significativas (>10% cambio)
2. **Esperado**: Alerta visual aparece mostrando:
   - Icono ⚠️
   - Mensaje descriptivo
   - Color verde (positivo) o rojo (negativo)

**Verificar**:
- [ ] Alertas aparecen para cambios >10%
- [ ] Colores son correctos
- [ ] Mensajes son descriptivos

---

### 4. Sistema ABAC ✅

#### Validar Permisos en Wizard

1. Iniciar sesión como **técnico**
2. Navegar a: `/wizard/`
3. **Esperado**: 
   - Pasos visibles según permisos
   - Botones habilitados/deshabilitados según permisos
   - Campos editables según permisos

#### Validar Permisos en Dashboard

1. Iniciar sesión como **PM**
2. Navegar a: `/dashboard/`
3. **Esperado**: Dashboard completo visible

4. Iniciar sesión como **cliente**
5. Navegar a: `/dashboard/`
6. **Esperado**: Acceso limitado o denegado según políticas

**Verificar**:
- [ ] Permisos se aplican correctamente
- [ ] Elementos se ocultan/muestran según permisos
- [ ] Botones se deshabilitan según permisos

#### Validar Evaluación de Políticas

1. Usar script de validación o hacer request manual:
```bash
curl -X POST http://localhost:8000/api/policies/evaluate/ \
  -H "Content-Type: application/json" \
  -u "username:password" \
  -d '{"action":"dashboard.view"}'
```

2. **Esperado**: Respuesta JSON con:
   - `allowed`: `true` o `false`
   - `action`: Acción evaluada
   - `policy_effect`: Efecto de la política aplicada

---

### 5. Throttling y Costos de IA ✅

#### Validar Throttling

1. Hacer múltiples requests a `/api/ai/suggest/` rápidamente
2. **Esperado**: 
   - Primeros requests: 200 OK
   - Después del límite: 429 Too Many Requests
   - Header `Retry-After` presente

#### Validar Estadísticas

1. Navegar a: `/api/ai/stats/` (requiere autenticación)
2. **Esperado**: Respuesta JSON con:
   - Total de requests
   - Costos estimados
   - Desglose por modelo

**Verificar**:
- [ ] Throttling funciona correctamente
- [ ] Estadísticas se actualizan
- [ ] Costos se calculan correctamente

---

### 6. Seguridad ✅

#### Validar Rate Limiting

1. Hacer múltiples requests rápidamente a cualquier endpoint
2. **Esperado**: Después del límite, respuesta 429

#### Validar Security Headers

1. Hacer request a cualquier endpoint:
```bash
curl -I http://localhost:8000/dashboard/
```

2. **Esperado**: Headers presentes:
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`

#### Validar CSP (si está habilitado)

1. Verificar header `Content-Security-Policy` en respuesta
2. **Esperado**: CSP configurado según settings

---

### 7. Performance ✅

#### Validar Cache de Tendencias

1. Hacer request a `/api/dashboard/trends/` dos veces consecutivas
2. **Esperado**: 
   - Primera request: Tiempo normal
   - Segunda request: Tiempo más rápido (cache hit)

#### Validar Optimización de Queries

1. Monitorear queries de base de datos durante carga del dashboard
2. **Esperado**: 
   - Número reducido de queries
   - Uso de `select_related()` y `only()`
   - Tiempo de respuesta < 200ms

---

## 🛠️ Scripts de Validación

### Script Bash (Linux/Mac)

```bash
chmod +x scripts/validar_dashboard.sh
./scripts/validar_dashboard.sh
```

### Script PowerShell (Windows)

```powershell
.\scripts\validar_dashboard.ps1
```

### Parámetros Opcionales

```bash
# Bash
BASE_URL=http://localhost:8000 \
USERNAME=admin \
PASSWORD=admin123 \
SITEC_ID=1 \
./scripts/validar_dashboard.sh

# PowerShell
.\scripts\validar_dashboard.ps1 `
  -BaseUrl "http://localhost:8000" `
  -Username "admin" `
  -Password "admin123" `
  -SitecId "1"
```

---

## 📊 Checklist Completo

### Funcionalidades Core

- [ ] Health checks básicos y detallados funcionando
- [ ] Dashboard carga KPIs correctamente
- [ ] Comparativos históricos se muestran
- [ ] Tendencias se cargan (mensuales y semanales)
- [ ] Tooltips funcionan en gráficos
- [ ] Exportación PNG funciona
- [ ] Exportación SVG funciona
- [ ] Alertas visuales aparecen para tendencias significativas

### Seguridad y Permisos

- [ ] Permisos ABAC funcionan en wizard
- [ ] Permisos ABAC funcionan en dashboard
- [ ] Evaluación de políticas funciona
- [ ] Rate limiting funciona
- [ ] Security headers presentes
- [ ] CSP configurado (si está habilitado)

### Performance

- [ ] Cache de tendencias funciona
- [ ] Queries optimizadas
- [ ] Tiempo de respuesta < 200ms

### IA y Throttling

- [ ] Throttling funciona
- [ ] Estadísticas de IA se muestran
- [ ] Costos se calculan correctamente

---

## 🐛 Problemas Comunes

### Tendencias no se cargan

**Solución**:
1. Verificar que hay datos históricos
2. Verificar consola del navegador (F12)
3. Limpiar cache: `python manage.py shell` → `cache.clear()`

### Tooltips no aparecen

**Solución**:
1. Verificar que JavaScript está habilitado
2. Verificar consola del navegador
3. Probar en otro navegador

### Exportación no funciona

**Solución**:
1. Verificar permisos de descarga del navegador
2. Verificar que no hay bloqueadores de contenido
3. Probar en modo incógnito

---

## 📝 Notas

- **Navegadores compatibles**: Chrome, Firefox, Edge, Safari (versiones recientes)
- **JavaScript requerido**: Todas las funcionalidades requieren JavaScript
- **Autenticación**: La mayoría de endpoints requieren autenticación
- **Permisos**: Validar con diferentes roles (tecnico, pm, supervisor, cliente)

---

**Última actualización**: 2026-01-18
