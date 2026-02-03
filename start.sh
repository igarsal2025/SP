#!/usr/bin/env bash
# Start script para Render.com
# Este script inicia la aplicación Django con Gunicorn

cd backend

# Iniciar Gunicorn
# PORT es proporcionado automáticamente por Render
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
