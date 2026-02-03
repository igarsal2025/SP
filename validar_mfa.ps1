# Script de validación para tests MFA
# Ejecuta todos los tests relacionados con MFA

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación de Tests MFA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "G:\SeguimientoProyectos\backend"
$venvPython = "G:\SeguimientoProyectos\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: No se encontró el entorno virtual en $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando tests MFA..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar tests MFA
$testCommand = "cd $backendPath; $venvPython manage.py test apps.accounts.tests_mfa --verbosity=2"
Invoke-Expression $testCommand

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Todos los tests MFA pasaron" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Algunos tests MFA fallaron" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

exit $exitCode
