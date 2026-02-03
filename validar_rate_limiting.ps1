# Script de validación para Rate Limiting Avanzado
# Ejecuta todos los tests relacionados con rate limiting

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación: Rate Limiting Avanzado" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio backend
Set-Location -Path "backend"

# Ejecutar tests de rate limiting avanzado
Write-Host "1. Ejecutando tests de Rate Limiting Avanzado..." -ForegroundColor Yellow
& "..\.venv\Scripts\python.exe" manage.py test apps.accounts.tests_rate_limit_advanced --verbosity=1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tests de rate limiting avanzado fallaron" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Ejecutar tests de seguridad (rate limiting básico)
Write-Host "2. Ejecutando tests de Rate Limiting Básico (compatibilidad)..." -ForegroundColor Yellow
& "..\.venv\Scripts\python.exe" manage.py test apps.accounts.tests_security.RateLimitingTests --verbosity=1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tests de rate limiting básico fallaron" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Resumen
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Todos los tests pasaron correctamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Funcionalidades validadas:" -ForegroundColor Cyan
Write-Host "  ✅ Rate limiting por IP" -ForegroundColor Green
Write-Host "  ✅ Rate limiting por usuario" -ForegroundColor Green
Write-Host "  ✅ Rate limiting por endpoint" -ForegroundColor Green
Write-Host "  ✅ Headers informativos" -ForegroundColor Green
Write-Host "  ✅ Paths excluidos" -ForegroundColor Green
Write-Host "  ✅ Compatibilidad con versión anterior" -ForegroundColor Green
Write-Host ""
