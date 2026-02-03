# Script para instalar dependencias del proyecto
# Ejecutar: .\instalar_dependencias.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Instalación de Dependencias - SITEC Web" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python no encontrado. Por favor instala Python primero." -ForegroundColor Red
        Write-Host "   Ver: INSTALAR_PYTHON.md" -ForegroundColor Gray
        exit 1
    }
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar requirements.txt
Write-Host "Verificando requirements.txt..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "✅ requirements.txt encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
Write-Host "Esto puede tomar unos minutos..." -ForegroundColor Gray
Write-Host ""

try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Hubo algunos errores durante la instalación" -ForegroundColor Yellow
        Write-Host "   Revisa los mensajes arriba" -ForegroundColor Gray
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error instalando dependencias: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar Django
Write-Host "Verificando Django..." -ForegroundColor Yellow
try {
    $djangoVersion = python -c "import django; print(django.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Django $djangoVersion instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Django no se pudo importar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Instalación Completada" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. cd backend" -ForegroundColor Gray
Write-Host "  2. python manage.py makemigrations" -ForegroundColor Gray
Write-Host "  3. python manage.py migrate" -ForegroundColor Gray
Write-Host "  4. python manage.py test" -ForegroundColor Gray
Write-Host ""
