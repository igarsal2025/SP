# Script para verificar entorno antes de ejecutar tests

Write-Host "🔍 Verificando entorno para ejecutar tests..." -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python no encontrado. Por favor instala Python 3.8+" -ForegroundColor Red
    exit 1
}

# Verificar Django
Write-Host "2. Verificando Django..." -ForegroundColor Yellow
$djangoCheck = python -c "import django; print(django.get_version())" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Django encontrado: $djangoCheck" -ForegroundColor Green
} else {
    Write-Host "   ❌ Django no esta instalado" -ForegroundColor Red
    Write-Host "   💡 Ejecuta: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Verificar entorno virtual
Write-Host "3. Verificando entorno virtual..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    Write-Host "   ✅ Entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Entorno virtual no detectado" -ForegroundColor Yellow
    Write-Host "   💡 Se recomienda activar el entorno virtual:" -ForegroundColor Yellow
    Write-Host "      .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
}

# Verificar archivos de tests
Write-Host "4. Verificando archivos de tests..." -ForegroundColor Yellow
$testFiles = @(
    "backend\apps\ai\tests_throttling.py",
    "backend\apps\accounts\tests_security.py",
    "backend\apps\accounts\tests_abac_integration.py"
)

$allFound = $true
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file no encontrado" -ForegroundColor Red
        $allFound = $false
    }
}

if (-not $allFound) {
    Write-Host ""
    Write-Host "   ❌ Algunos archivos de tests no se encontraron" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Entorno verificado correctamente" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Para ejecutar los tests:" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor Yellow
Write-Host "   python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2" -ForegroundColor Yellow
