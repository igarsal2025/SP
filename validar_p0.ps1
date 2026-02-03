# Script de Validación P0 - Pendientes Críticos
# Ejecuta los tests automatizados para validar la implementación P0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación P0 - Pendientes Críticos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio backend
Set-Location "G:\SeguimientoProyectos\backend"

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "ERROR: No se encontró el entorno virtual en .venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Ejecutando tests de navegación..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.frontend.tests_p0_navigation --verbosity=2

Write-Host ""
Write-Host "Ejecutando tests de rechazo de reportes..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.reports.tests_reject --verbosity=2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación completada" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
