# Guía para Ejecutar Tests - SITEC Web

## Requisitos Previos

1. **Python 3.11+** instalado y en PATH
2. **Django** y dependencias instaladas
3. **Base de datos** configurada (SQLite por defecto)

## Instalación de Dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt

# O si usas virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Ejecutar Tests

### Opción 1: Todos los Tests

```bash
cd backend
python manage.py test
```

### Opción 2: Tests Específicos

```bash
cd backend

# Tests básicos
python manage.py test apps.frontend.tests

# Tests de seguridad
python manage.py test apps.frontend.tests_security

# Tests de performance
python manage.py test apps.frontend.tests_performance

# Tests de funcionalidad
python manage.py test apps.frontend.tests_functional

# Tests de otras apps
python manage.py test apps.accounts
python manage.py test apps.audit
python manage.py test apps.companies
```

### Opción 3: Usando Scripts

```bash
# Linux/Mac
./scripts/run_all_tests.sh

# Windows PowerShell
.\scripts\run_all_tests.ps1
```

### Opción 4: Con Verbosidad

```bash
cd backend
python manage.py test --verbosity=2  # Más detallado
python manage.py test --verbosity=3  # Muy detallado
```

## Tests Disponibles

### Tests de Seguridad (`tests_security.py`)
- ✅ Autenticación y autorización
- ✅ Validación de entrada (XSS, SQL Injection)
- ✅ Protección CSRF
- ✅ Re-autenticación
- ✅ Aislamiento de datos
- ✅ Privacidad de datos

**Ejecutar:**
```bash
python manage.py test apps.frontend.tests_security --verbosity=2
```

### Tests de Performance (`tests_performance.py`)
- ✅ Tiempo de respuesta (< 500ms)
- ✅ Tamaño de bundles JS (< 100KB)
- ✅ Optimización de queries (N+1)
- ✅ Carga concurrente

**Ejecutar:**
```bash
python manage.py test apps.frontend.tests_performance --verbosity=2
```

### Tests de Funcionalidad (`tests_functional.py`)
- ✅ Flujo completo del wizard
- ✅ Validaciones por paso
- ✅ Sincronización
- ✅ Preferencias de usuario
- ✅ Analytics
- ✅ Métricas de performance

**Ejecutar:**
```bash
python manage.py test apps.frontend.tests_functional --verbosity=2
```

## Salida Esperada

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
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..F.
======================================================================
FAIL: test_save_step_response_time (apps.frontend.tests_performance.PerformanceEndpointTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AssertionError: save_step tardó 650.23ms, esperado < 500ms

----------------------------------------------------------------------
Ran 4 tests in 0.234s

FAILED (failures=1)
```

## Troubleshooting

### Error: "No module named 'django'"

```bash
pip install -r requirements.txt
```

### Error: "Database does not exist"

Los tests crean automáticamente una base de datos de prueba. Si hay problemas:

```bash
# Limpiar base de datos de prueba
python manage.py test --keepdb  # Mantiene DB entre ejecuciones
```

### Error: "ModuleNotFoundError"

Verificar que estás en el directorio correcto:

```bash
cd backend
python manage.py test
```

### Tests Lentos

Usar `--keepdb` para evitar recrear la base de datos:

```bash
python manage.py test --keepdb
```

## Cobertura de Código (Opcional)

```bash
# Instalar coverage
pip install coverage

# Ejecutar con cobertura
coverage run --source='.' manage.py test

# Ver reporte
coverage report

# Reporte HTML
coverage html
# Abrir htmlcov/index.html
```

## Integración Continua

Los tests se ejecutan automáticamente en:
- GitHub Actions (`.github/workflows/performance.yml`)
- Pre-commit hooks (opcional)

## Resumen de Tests Creados

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `tests_security.py` | 15+ | Seguridad, autenticación, validación |
| `tests_performance.py` | 10+ | Performance, tiempo, queries |
| `tests_functional.py` | 20+ | Funcionalidad completa |
| `tests.py` | 3 | Tests básicos (compatibilidad) |
| **TOTAL** | **45+** | Suite completa |

## Próximos Pasos

1. Ejecutar tests localmente
2. Revisar resultados
3. Corregir cualquier fallo
4. Integrar en CI/CD
5. Configurar alertas de cobertura
