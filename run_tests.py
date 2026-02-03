#!/usr/bin/env python
"""
Script para ejecutar todos los tests del proyecto SITEC Web
"""
import os
import sys
import subprocess
from pathlib import Path

# Cambiar al directorio backend
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)

# Configurar Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Importar Django
import django
django.setup()

# Ejecutar tests
from django.core.management import execute_from_command_line

print("=" * 60)
print("Ejecutando Suite Completa de Tests - SITEC Web")
print("=" * 60)
print()

test_modules = [
    "apps.frontend.tests",
    "apps.frontend.tests_security",
    "apps.frontend.tests_performance",
    "apps.frontend.tests_functional",
    "apps.accounts.tests",
    "apps.audit.tests",
    "apps.companies.tests",
]

results = {}
total_tests = 0
total_failures = 0

for test_module in test_modules:
    print(f"\n{'='*60}")
    print(f"Ejecutando: {test_module}")
    print(f"{'='*60}\n")
    
    try:
        # Ejecutar tests usando Django test runner
        from django.test.utils import get_runner
        from django.conf import settings
        
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
        
        # Ejecutar tests
        result = test_runner.run_tests([test_module])
        
        if result:
            results[test_module] = "PASSED"
        else:
            results[test_module] = "FAILED"
            total_failures += 1
            
    except Exception as e:
        print(f"ERROR ejecutando {test_module}: {e}")
        results[test_module] = "ERROR"
        total_failures += 1

# Resumen
print("\n" + "=" * 60)
print("RESUMEN DE RESULTADOS")
print("=" * 60)
print()

for module, status in results.items():
    status_symbol = "✅" if status == "PASSED" else "❌"
    print(f"{status_symbol} {module}: {status}")

print()
if total_failures == 0:
    print("🎉 Todos los tests pasaron exitosamente!")
    sys.exit(0)
else:
    print(f"⚠️  {total_failures} módulo(s) con fallos. Revisar output arriba.")
    sys.exit(1)
