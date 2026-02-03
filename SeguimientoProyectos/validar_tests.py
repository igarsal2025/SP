#!/usr/bin/env python
"""
Script de validación de tests - Verifica sintaxis sin ejecutar
"""
import ast
import sys
from pathlib import Path

def validate_python_file(file_path):
    """Valida que un archivo Python tenga sintaxis correcta"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code, filename=str(file_path))
        return True, None
    except SyntaxError as e:
        return False, f"Error de sintaxis en línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Valida todos los archivos de test"""
    backend_dir = Path(__file__).parent / "backend"
    test_files = [
        backend_dir / "apps" / "frontend" / "tests.py",
        backend_dir / "apps" / "frontend" / "tests_security.py",
        backend_dir / "apps" / "frontend" / "tests_performance.py",
        backend_dir / "apps" / "frontend" / "tests_functional.py",
    ]
    
    print("=" * 60)
    print("Validación de Sintaxis de Tests")
    print("=" * 60)
    print()
    
    all_valid = True
    results = {}
    
    for test_file in test_files:
        if not test_file.exists():
            print(f"❌ {test_file.name}: Archivo no encontrado")
            all_valid = False
            continue
            
        is_valid, error = validate_python_file(test_file)
        if is_valid:
            print(f"✅ {test_file.name}: Sintaxis correcta")
            results[test_file.name] = "OK"
        else:
            print(f"❌ {test_file.name}: {error}")
            results[test_file.name] = error
            all_valid = False
    
    print()
    print("=" * 60)
    print("Resumen")
    print("=" * 60)
    
    for filename, status in results.items():
        status_symbol = "✅" if status == "OK" else "❌"
        print(f"{status_symbol} {filename}: {status}")
    
    print()
    if all_valid:
        print("🎉 Todos los archivos de test tienen sintaxis correcta!")
        print()
        print("Para ejecutar los tests, usa:")
        print("  cd backend")
        print("  python manage.py test")
        return 0
    else:
        print("⚠️  Algunos archivos tienen errores de sintaxis")
        return 1

if __name__ == "__main__":
    sys.exit(main())
