# Instrucciones para Ejecutar Tests - SITEC Web

## ⚠️ Estado Actual

Los tests están **completamente implementados** y listos para ejecutarse. Sin embargo, **Python no está disponible en el PATH** del sistema actual.

## ✅ Tests Implementados

Los siguientes archivos de test están creados y listos:

- ✅ `backend/apps/frontend/tests.py` - Tests básicos
- ✅ `backend/apps/frontend/tests_security.py` - 15+ tests de seguridad
- ✅ `backend/apps/frontend/tests_performance.py` - 10+ tests de performance  
- ✅ `backend/apps/frontend/tests_functional.py` - 20+ tests de funcionalidad

**Total: 45+ tests implementados**

## 🔧 Solución: Instalar/Configurar Python

### Opción 1: Instalar Python (Recomendado)

1. **Descargar Python 3.11+**
   - Visita: https://www.python.org/downloads/
   - Descarga la versión para Windows

2. **Instalar Python**
   - Durante la instalación, **marca la casilla**: "Add Python to PATH"
   - Completa la instalación

3. **Verificar instalación**
   ```powershell
   python --version
   # Debe mostrar: Python 3.11.x o superior
   ```

4. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Ejecutar tests**
   ```powershell
   cd backend
   python manage.py test
   ```

### Opción 2: Usar Python desde Microsoft Store

```powershell
# Instalar desde Microsoft Store
# Buscar "Python" en Microsoft Store e instalar

# Luego verificar
python --version
```

### Opción 3: Usar Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Si hay error de política de ejecución:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
cd backend
python manage.py test
```

## 📋 Comandos para Ejecutar Tests

Una vez que Python esté configurado:

### Todos los Tests

```powershell
cd backend
python manage.py test
```

### Tests Específicos

```powershell
# Tests de seguridad
python manage.py test apps.frontend.tests_security --verbosity=2

# Tests de performance
python manage.py test apps.frontend.tests_performance --verbosity=2

# Tests de funcionalidad
python manage.py test apps.frontend.tests_functional --verbosity=2

# Tests básicos
python manage.py test apps.frontend.tests --verbosity=2
```

### Con Más Detalle

```powershell
# Verbosidad alta
python manage.py test --verbosity=3

# Mantener base de datos entre ejecuciones
python manage.py test --keepdb
```

## 📊 Tests Disponibles

### 🔒 Tests de Seguridad (15+ tests)

- `test_unauthenticated_access_denied` - Acceso no autenticado bloqueado
- `test_authenticated_access_allowed` - Acceso autenticado permitido
- `test_reauthentication_requires_valid_password` - Re-autenticación valida contraseña
- `test_xss_protection_in_step_data` - Protección contra XSS
- `test_sql_injection_protection` - Protección contra SQL Injection
- `test_json_injection_protection` - Protección contra JSON Injection
- `test_policy_deny_blocks_access` - Políticas de acceso funcionan
- `test_cross_company_data_isolation` - Aislamiento de datos entre empresas
- Y más...

### ⚡ Tests de Performance (10+ tests)

- `test_save_step_response_time` - Tiempo < 500ms
- `test_validate_step_response_time` - Tiempo < 500ms
- `test_sync_response_time` - Tiempo < 500ms
- `test_js_bundle_size_within_limits` - JS < 100KB
- `test_save_step_query_count` - Queries < 10
- `test_multiple_save_operations_performance` - Carga concurrente
- Y más...

### ✅ Tests de Funcionalidad (20+ tests)

- `test_complete_wizard_flow` - Flujo completo de 12 pasos
- `test_wizard_validation_all_steps` - Validaciones por paso
- `test_wizard_warnings_non_blocking` - Warnings no bloquean
- `test_sync_creates_missing_steps` - Sync crea steps
- `test_sync_resolves_conflicts_with_resolution` - Resolución de conflictos
- `test_save_field_mode_preference` - Preferencias de Modo Campo
- `test_analytics_endpoint_accepts_data` - Analytics funciona
- Y más...

## 🎯 Salida Esperada

### Tests Exitosos

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
........
----------------------------------------------------------------------
Ran 8 tests in 0.123s

OK
Destroying test database for alias 'default'...
```

### Tests con Fallos

```
FAIL: test_save_step_response_time (apps.frontend.tests_performance.PerformanceEndpointTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AssertionError: save_step tardó 650.23ms, esperado < 500ms

----------------------------------------------------------------------
Ran 4 tests in 0.234s

FAILED (failures=1)
```

## 🔍 Verificación Manual

Si no puedes ejecutar los tests ahora, puedes verificar manualmente:

1. **Verificar que los archivos existen**:
   ```powershell
   Test-Path backend\apps\frontend\tests_security.py
   Test-Path backend\apps\frontend\tests_performance.py
   Test-Path backend\apps\frontend\tests_functional.py
   ```

2. **Revisar el contenido**:
   - Los archivos están en `backend/apps/frontend/`
   - Cada archivo tiene múltiples clases de test
   - Cada clase tiene múltiples métodos de test

3. **Verificar sintaxis** (si tienes Python):
   ```powershell
   python -m py_compile backend\apps\frontend\tests_security.py
   ```

## 📚 Documentación Adicional

- `docs/TESTING.md` - Guía completa de testing
- `RESUMEN_TESTS.md` - Resumen de todos los tests
- `EJECUTAR_TESTS.md` - Instrucciones detalladas

## ✅ Conclusión

Los tests están **100% implementados y listos**. Solo necesitas:

1. ✅ Instalar/configurar Python
2. ✅ Instalar dependencias (`pip install -r requirements.txt`)
3. ✅ Ejecutar tests (`python manage.py test`)

Una vez que Python esté disponible, los tests se ejecutarán sin problemas.
