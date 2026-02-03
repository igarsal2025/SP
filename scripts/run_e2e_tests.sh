#!/bin/bash
# Script bash para ejecutar pruebas E2E con Playwright
# Uso: ./scripts/run_e2e_tests.sh [opciones]

set -e

echo "=== Ejecutando Pruebas E2E con Playwright ==="

# Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js no está instalado"
    exit 1
fi

echo "Node.js version: $(node --version)"

# Verificar que npm esté instalado
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm no está instalado"
    exit 1
fi

echo "npm version: $(npm --version)"

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias de Node.js..."
    npm install
fi

# Instalar navegadores de Playwright si se solicita
if [ "$1" == "--install" ]; then
    echo "Instalando navegadores de Playwright..."
    npx playwright install
    shift
fi

# Verificar que el servidor Django esté corriendo
echo "Verificando que el servidor Django esté corriendo..."
if curl -s http://127.0.0.1:8000/health/ > /dev/null; then
    echo "Servidor Django está corriendo"
else
    echo "ADVERTENCIA: No se pudo conectar al servidor Django en http://127.0.0.1:8000"
    echo "Asegúrate de que el servidor esté corriendo antes de ejecutar las pruebas"
    echo "Ejecuta: cd backend && python manage.py runserver"
fi

# Ejecutar pruebas
echo "Ejecutando pruebas E2E..."
npx playwright test "$@"

# Mostrar reporte si las pruebas terminaron
if [ $? -eq 0 ]; then
    echo ""
    echo "=== Pruebas completadas exitosamente ==="
    echo "Para ver el reporte HTML, ejecuta: npm run test:e2e:report"
else
    echo ""
    echo "=== Algunas pruebas fallaron ==="
    echo "Revisa los resultados en test-results/ y playwright-report/"
fi
