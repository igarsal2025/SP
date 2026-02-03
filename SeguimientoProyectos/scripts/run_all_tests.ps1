# Script PowerShell para ejecutar todos los tests: seguridad, performance y funcionalidad

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ejecutando Suite Completa de Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

$exitCodes = @{}

# Tests de Seguridad
Write-Host "🔒 Ejecutando Tests de Seguridad..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.frontend.tests_security --verbosity=2
$exitCodes["Security"] = $LASTEXITCODE

Write-Host ""
Write-Host "⚡ Ejecutando Tests de Performance..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.frontend.tests_performance --verbosity=2
$exitCodes["Performance"] = $LASTEXITCODE

Write-Host ""
Write-Host "✅ Ejecutando Tests de Funcionalidad..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.frontend.tests_functional --verbosity=2
$exitCodes["Functional"] = $LASTEXITCODE

Write-Host ""
Write-Host "📊 Ejecutando Tests Básicos..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python manage.py test apps.frontend.tests --verbosity=2
$exitCodes["Basic"] = $LASTEXITCODE

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Resumen de Resultados" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($key in $exitCodes.Keys) {
    if ($exitCodes[$key] -eq 0) {
        Write-Host "✅ Tests de $key : PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests de $key : FAILED" -ForegroundColor Red
    }
}

Write-Host ""

$totalFailed = ($exitCodes.Values | Where-Object { $_ -ne 0 }).Count

if ($totalFailed -eq 0) {
    Write-Host "🎉 Todos los tests pasaron exitosamente!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Algunos tests fallaron. Revisar output arriba." -ForegroundColor Red
    exit 1
}

Set-Location ..
