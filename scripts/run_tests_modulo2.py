#!/usr/bin/env python
"""
Script para ejecutar todos los tests del Módulo 2
"""
import os
import sys

# Cambiar al directorio backend si no estamos ahí
if not os.path.exists('manage.py'):
    if os.path.exists('backend/manage.py'):
        os.chdir('backend')
    else:
        print("Error: No se encontró manage.py")
        sys.exit(1)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    
    import django
    django.setup()
    
    from django.core.management import execute_from_command_line
    
    # Ejecutar tests usando manage.py
    test_modules = [
        "apps.sync.tests",
        "apps.reports.tests",
        "apps.projects.tests",
        "apps.tests_integration_modulo2",
    ]
    
    execute_from_command_line(["manage.py", "test"] + test_modules)
