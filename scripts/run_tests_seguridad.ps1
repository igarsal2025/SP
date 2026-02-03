# Script PowerShell para ejecutar tests de seguridad y funcionamiento

Write-Host "🧪 Ejecutando tests de seguridad y funcionamiento..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual si existe
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

Set-Location backend

Write-Host "📦 Tests de Throttling de IA..." -ForegroundColor Yellow
python manage.py test apps.ai.tests_throttling --verbosity=2
Write-Host ""

Write-Host "🔒 Tests de Seguridad..." -ForegroundColor Yellow
python manage.py test apps.accounts.tests_security --verbosity=2
Write-Host ""

Write-Host "🔗 Tests de Integración ABAC..." -ForegroundColor Yellow
python manage.py test apps.accounts.tests_abac_integration --verbosity=2
Write-Host ""

Write-Host "✅ Tests completados!" -ForegroundColor Green
