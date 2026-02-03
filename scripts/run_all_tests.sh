#!/bin/bash
# Script para ejecutar todos los tests: seguridad, performance y funcionalidad

echo "=========================================="
echo "Ejecutando Suite Completa de Tests"
echo "=========================================="
echo ""

cd backend"

# Tests de Seguridad
echo "🔒 Ejecutando Tests de Seguridad..."
echo "----------------------------------------"
python manage.py test apps.frontend.tests_security --verbosity=2
SECURITY_EXIT=$?

echo ""
echo "⚡ Ejecutando Tests de Performance..."
echo "----------------------------------------"
python manage.py test apps.frontend.tests_performance --verbosity=2
PERF_EXIT=$?

echo ""
echo "✅ Ejecutando Tests de Funcionalidad..."
echo "----------------------------------------"
python manage.py test apps.frontend.tests_functional --verbosity=2
FUNC_EXIT=$?

echo ""
echo "📊 Ejecutando Tests Básicos..."
echo "----------------------------------------"
python manage.py test apps.frontend.tests --verbosity=2
BASIC_EXIT=$?

echo ""
echo "=========================================="
echo "Resumen de Resultados"
echo "=========================================="
echo ""

if [ $SECURITY_EXIT -eq 0 ]; then
    echo "✅ Tests de Seguridad: PASSED"
else
    echo "❌ Tests de Seguridad: FAILED"
fi

if [ $PERF_EXIT -eq 0 ]; then
    echo "✅ Tests de Performance: PASSED"
else
    echo "❌ Tests de Performance: FAILED"
fi

if [ $FUNC_EXIT -eq 0 ]; then
    echo "✅ Tests de Funcionalidad: PASSED"
else
    echo "❌ Tests de Funcionalidad: FAILED"
fi

if [ $BASIC_EXIT -eq 0 ]; then
    echo "✅ Tests Básicos: PASSED"
else
    echo "❌ Tests Básicos: FAILED"
fi

echo ""

TOTAL_EXIT=$((SECURITY_EXIT + PERF_EXIT + FUNC_EXIT + BASIC_EXIT))

if [ $TOTAL_EXIT -eq 0 ]; then
    echo "🎉 Todos los tests pasaron exitosamente!"
    exit 0
else
    echo "⚠️  Algunos tests fallaron. Revisar output arriba."
    exit 1
fi
