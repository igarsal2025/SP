# Ejecutar Tests del Módulo 2

## 📋 Requisitos Previos

1. **Python instalado** (3.8+)
2. **Dependencias instaladas**: `pip install -r requirements.txt`
3. **Base de datos configurada**: Migraciones aplicadas

## 🚀 Opciones de Ejecución

### Opción 1: Todos los tests del Módulo 2

```bash
cd backend
python manage.py test apps.sync.tests apps.reports.tests apps.projects.tests apps.tests_integration_modulo2
```

### Opción 2: Usando el script dedicado

```bash
cd backend
python scripts/run_tests_modulo2.py
```

### Opción 3: Tests por App

#### Tests de Sync
```bash
cd backend
python manage.py test apps.sync.tests
```

#### Tests de Reports
```bash
cd backend
python manage.py test apps.reports.tests
```

#### Tests de Projects
```bash
cd backend
python manage.py test apps.projects.tests
```

#### Tests de Integración
```bash
cd backend
python manage.py test apps.tests_integration_modulo2
```

### Opción 4: Test Específico

```bash
cd backend
# Ejemplo: test de creación de sesión de sync
python manage.py test apps.sync.tests.SyncTests.test_sync_creates_session

# Ejemplo: test de creación de reporte
python manage.py test apps.reports.tests.ReporteSemanalTests.test_create_reporte

# Ejemplo: test de creación de proyecto
python manage.py test apps.projects.tests.ProyectoTests.test_create_proyecto
```

## 📊 Ver Cobertura de Tests

Para ver qué código está cubierto por los tests:

```bash
cd backend
pip install coverage
coverage run --source='.' manage.py test apps.sync.tests apps.reports.tests apps.projects.tests apps.tests_integration_modulo2
coverage report
coverage html  # Genera reporte HTML en htmlcov/
```

## 🔍 Opciones Avanzadas

### Ejecutar con verbosidad
```bash
python manage.py test apps.sync.tests --verbosity=2
```

### Ejecutar tests en paralelo (Django 3.1+)
```bash
python manage.py test apps.sync.tests --parallel
```

### Ejecutar solo tests que fallan
```bash
python manage.py test apps.sync.tests --failfast
```

### Ejecutar con keepdb (más rápido, reutiliza DB)
```bash
python manage.py test apps.sync.tests --keepdb
```

## 📝 Estructura de Tests

```
backend/apps/
├── sync/
│   └── tests.py          # 12 tests de sincronización
├── reports/
│   └── tests.py          # 16 tests de reportes
├── projects/
│   └── tests.py          # 14 tests de proyectos
└── tests_integration_modulo2.py  # 5 tests de integración
```

## ✅ Verificación de Éxito

Al ejecutar los tests, deberías ver algo como:

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....................
----------------------------------------------------------------------
Ran 47 tests in X.XXXs

OK
Destroying test database for alias 'default'...
```

## 🐛 Solución de Problemas

### Error: "No module named 'apps'"
**Solución**: Asegúrate de estar en el directorio `backend/`:
```bash
cd backend
python manage.py test apps.sync.tests
```

### Error: "Database doesn't exist"
**Solución**: Las bases de datos de test se crean automáticamente. Si persiste:
```bash
python manage.py test apps.sync.tests --keepdb
```

### Error: "Migration issues"
**Solución**: Aplica las migraciones primero:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📈 Estadísticas Esperadas

- **Total de tests**: 47
- **Tiempo de ejecución**: ~5-15 segundos (depende del hardware)
- **Cobertura esperada**: >80% de código del Módulo 2

## 🔄 Integración en CI/CD

Para integrar en GitHub Actions o similar:

```yaml
- name: Run Módulo 2 Tests
  run: |
    cd backend
    python manage.py test apps.sync.tests apps.reports.tests apps.projects.tests apps.tests_integration_modulo2
```
