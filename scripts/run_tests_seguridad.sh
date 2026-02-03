#!/bin/bash
# Script para ejecutar tests de seguridad y funcionamiento

echo "🧪 Ejecutando tests de seguridad y funcionamiento..."
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

cd backend

echo "📦 Tests de Throttling de IA..."
python manage.py test apps.ai.tests_throttling --verbosity=2
echo ""

echo "🔒 Tests de Seguridad..."
python manage.py test apps.accounts.tests_security --verbosity=2
echo ""

echo "🔗 Tests de Integración ABAC..."
python manage.py test apps.accounts.tests_abac_integration --verbosity=2
echo ""

echo "✅ Tests completados!"
