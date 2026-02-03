# Guía para Ejecutar Tests de Seguridad y Funcionamiento

**Fecha**: 2026-01-18

---

## 📋 Prerequisitos

1. **Python 3.8+** instalado
2. **Entorno virtual** activado
3. **Dependencias** instaladas (`requirements.txt`)

---

## 🔧 Configuración Inicial

### 1. Activar Entorno Virtual

**Windows (PowerShell)**:
```powershell
# Si el entorno virtual está en la raíz del proyecto
.\venv\Scripts\Activate.ps1

# O si está en otro lugar
cd venv\Scripts
.\Activate.ps1
cd ..\..
```

**Linux/Mac**:
```bash
source venv/bin/activate
```

### 2. Instalar Dependencias (si no están instaladas)

```bash
pip install -r requirements.txt
```

---

## 🧪 Ejecutar Tests

### Opción 1: Scripts Automatizados

**Windows (PowerShell)**:
```powershell
.\scripts\run_tests_seguridad.ps1
```

**Linux/Mac**:
```bash
chmod +x scripts/run_tests_seguridad.sh
./scripts/run_tests_seguridad.sh
```

### Opción 2: Manualmente

**Navegar al directorio backend**:
```bash
cd backend
```

**Ejecutar todos los tests nuevos**:
```bash
python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2
```

**Ejecutar tests individuales**:

```bash
# Tests de throttling de IA
python manage.py test apps.ai.tests_throttling --verbosity=2

# Tests de seguridad
python manage.py test apps.accounts.tests_security --verbosity=2

# Tests de integración ABAC
python manage.py test apps.accounts.tests_abac_integration --verbosity=2
```

---

## 📊 Tests Incluidos

### 1. Tests de Throttling de IA (10 tests)

- `test_throttle_disabled_allows_all`
- `test_throttle_quick_per_hour`
- `test_throttle_heavy_per_day`
- `test_estimate_cost_rule_engine`
- `test_estimate_cost_light_model`
- `test_estimate_cost_heavy`
- `test_record_usage_updates_cache`
- `test_get_usage_stats`
- `test_endpoint_returns_429_when_throttled`
- `test_endpoint_allows_when_not_throttled`

### 2. Tests de Seguridad (8 tests)

- `test_rate_limit_disabled_allows_all`
- `test_rate_limit_blocks_after_limit`
- `test_security_headers_present`
- `test_csp_header_when_enabled`
- `test_csp_header_when_disabled`
- `test_health_check_basic`
- `test_health_check_detailed`
- `test_health_check_no_auth_required`

### 3. Tests de Integración ABAC (4 tests)

- `test_tecnico_can_access_wizard`
- `test_pm_can_access_dashboard`
- `test_cliente_cannot_submit_wizard`
- `test_multiple_actions_evaluation`

**Total**: 22 tests nuevos

---

## 🐛 Troubleshooting

### Error: "Django no está instalado"

**Solución**:
1. Verificar que el entorno virtual está activado:
   ```powershell
   # Debería mostrar (venv) al inicio del prompt
   ```
2. Instalar Django:
   ```bash
   pip install django
   ```
3. O instalar todas las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Error: "ModuleNotFoundError"

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "No such file or directory: manage.py"

**Solución**:
Asegurarse de estar en el directorio `backend`:
```bash
cd backend
python manage.py test ...
```

### Tests Fallan por Cache

**Solución**: Los tests limpian el cache automáticamente en `setUp()`. Si persiste, verificar configuración de cache en `settings.py`.

### Tests de Rate Limiting Flaky

**Nota**: Los tests de rate limiting pueden ser flaky si el cache no está configurado correctamente. En producción, se recomienda usar Redis.

---

## 📈 Cobertura de Tests

Para obtener un reporte de cobertura:

```bash
# Instalar coverage si no está instalado
pip install coverage

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration

# Ver reporte en consola
coverage report

# Generar reporte HTML
coverage html

# Abrir reporte en navegador (Windows)
start htmlcov/index.html
```

---

## ✅ Validación Esperada

### Salida Exitosa

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 22 tests in X.XXXs

OK
Destroying test database for alias 'default'...
```

### Si Hay Errores

Los tests mostrarán:
- Qué test falló
- Línea del error
- Traceback completo
- Mensaje de error

---

## 🔍 Verificar Tests Específicos

### Test Individual

```bash
python manage.py test apps.ai.tests_throttling.AiThrottlingTests.test_throttle_disabled_allows_all
```

### Con Más Detalle

```bash
python manage.py test apps.ai.tests_throttling --verbosity=3
```

---

## 📝 Notas Importantes

1. **Base de Datos de Tests**: Django crea una base de datos temporal en memoria para los tests
2. **Cache**: Los tests limpian el cache automáticamente
3. **Configuración**: Los tests usan `@override_settings` para configurar valores específicos
4. **Aislamiento**: Cada test se ejecuta en un entorno limpio

---

## 🚀 Integración Continua

Para ejecutar en CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Run tests
  run: |
    cd backend
    python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2
```

---

**Última actualización**: 2026-01-18
