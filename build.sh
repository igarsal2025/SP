#!/usr/bin/env bash
# Build script para Render.com
# Este script se ejecuta durante cada deploy

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure

echo "=========================================="
echo "Building SITEC application for Render..."
echo "=========================================="

# Actualizar pip
echo "Upgrading pip..."
pip install --upgrade pip

# Instalar dependencias
echo "Installing dependencies..."
pip install -r requirements.txt

# Cambiar al directorio backend
cd backend

# Ejecutar migraciones
echo "Running database migrations..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
