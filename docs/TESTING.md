# Guía de Testing - SITEC Web

## Suite de Tests Completa

El proyecto incluye una suite completa de tests que cubre:

1. **Tests de Seguridad** (`tests_security.py`)
2. **Tests de Performance** (`tests_performance.py`)
3. **Tests de Funcionalidad** (`tests_functional.py`)
4. **Tests Básicos** (`tests.py`)

## Ejecutar Tests

### Todos los Tests

```bash
# Linux/Mac
./scripts/run_all_tests.sh

# Windows PowerShell
.\scripts\run_all_tests.ps1

# Manualmente
cd backend
python manage.py test
```

### Tests Específicos

```bash
# Solo tests de seguridad
python manage.py test apps.frontend.tests_security

# Solo tests de performance
python manage.py test apps.frontend.tests_performance

# Solo tests de funcionalidad
python manage.py test apps.frontend.tests_functional

# Tests de una app específica
python manage.py test apps.accounts
python manage.py test apps.audit
```

### Con Cobertura

```bash
# Instalar coverage
pip install coverage

# Ejecutar con cobertura
coverage run --source='.' manage.py test
coverage report
coverage html  # Genera reporte HTML en htmlcov/
```

## Tests de Seguridad

### Cobertura

- ✅ Autenticación y autorización
- ✅ Validación de entrada (XSS, SQL Injection)
- ✅ Protección CSRF
- ✅ Re-autenticación
- ✅ Aislamiento de datos entre empresas
- ✅ Privacidad de datos (contraseñas no expuestas)

### Ejemplos

```python
# Test de autenticación
def test_unauthenticated_access_denied(self):
    self.client.logout()
    response = self.client.post("/api/wizard/steps/save/", ...)
    self.assertEqual(response.status_code, 403)

# Test de XSS
def test_xss_protection_in_step_data(self):
    malicious_data = {"project_name": "<script>alert('XSS')</script>"}
    response = self.client.post("/api/wizard/steps/save/", ...)
    # Verificar que se sanitiza correctamente
```

## Tests de Performance

### Cobertura

- ✅ Tiempo de respuesta de endpoints (< 500ms)
- ✅ Tamaño de bundles JS (< 100KB)
- ✅ Optimización de queries (prevención N+1)
- ✅ Performance bajo carga concurrente

### Límites

```python
PERFORMANCE_LIMITS = {
    "endpoint_response_time_ms": 500,
    "js_bundle_size_kb": 100,
    "max_queries_per_request": 10,
}
```

### Ejemplos

```python
# Test de tiempo de respuesta
def test_save_step_response_time(self):
    start = time.time()
    response = self.client.post("/api/wizard/steps/save/", ...)
    elapsed = (time.time() - start) * 1000
    self.assertLess(elapsed, 500)  # < 500ms

# Test de queries
def test_save_step_query_count(self):
    reset_queries()
    response = self.client.post("/api/wizard/steps/save/", ...)
    query_count = len(connection.queries)
    self.assertLessEqual(query_count, 10)
```

## Tests de Funcionalidad

### Cobertura

- ✅ Flujo completo del wizard (12 pasos)
- ✅ Validaciones por paso
- ✅ Sincronización (sync)
- ✅ Resolución de conflictos
- ✅ Preferencias de usuario (Modo Campo)
- ✅ Analytics
- ✅ Métricas de performance

### Ejemplos

```python
# Test de flujo completo
def test_complete_wizard_flow(self):
    # Paso 1
    response = self.client.post("/api/wizard/steps/save/", ...)
    # Validar paso 1
    response = self.client.post("/api/wizard/validate/", ...)
    # Paso 2
    response = self.client.post("/api/wizard/steps/save/", ...)
    # Verificar draft y steps creados

# Test de validaciones
def test_wizard_validation_all_steps(self):
    # Test validaciones para cada uno de los 12 pasos
    for step, data, expected_errors in validation_tests:
        response = self.client.post("/api/wizard/validate/", ...)
        self.assertFalse(response.data["allowed"])
```

## Estructura de Tests

```
backend/apps/frontend/
├── tests.py                 # Tests básicos (compatibilidad)
├── tests_security.py        # Tests de seguridad
├── tests_performance.py    # Tests de performance
└── tests_functional.py     # Tests de funcionalidad
```

## Mejores Prácticas

### 1. Setup y Teardown

```python
def setUp(self):
    # Crear datos de prueba
    self.company = Company.objects.create(...)
    self.user = User.objects.create_user(...)
    self.client.login(...)
```

### 2. Nombres Descriptivos

```python
def test_unauthenticated_access_denied(self):
    # Nombre claro que describe qué se prueba
```

### 3. Assertions Específicas

```python
# Bueno
self.assertEqual(response.status_code, 200)
self.assertIn("project_name_required", response.data["critical"])

# Evitar
self.assertTrue(response.status_code == 200)  # Menos claro
```

### 4. Datos de Prueba Realistas

```python
# Usar datos que reflejen casos reales
data = {
    "project_name": "Proyecto Test",
    "week_start": "2026-01-01",
    "site_address": "Calle Test 123",
}
```

## CI/CD Integration

Los tests se ejecutan automáticamente en:

- **GitHub Actions**: `.github/workflows/performance.yml`
- **Pre-commit hooks**: (opcional, configurar)

## Troubleshooting

### Tests que fallan intermitentemente

- Verificar que no hay dependencias de orden
- Usar `setUp()` y `tearDown()` correctamente
- Limpiar datos entre tests

### Tests de performance inconsistentes

- Ejecutar múltiples veces y promediar
- Considerar variabilidad del sistema
- Usar límites con margen de error

### Tests de seguridad que pasan cuando no deberían

- Verificar que los tests realmente prueban la vulnerabilidad
- Revisar que las protecciones están habilitadas
- Consultar documentación de Django/DRF

## Referencias

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
