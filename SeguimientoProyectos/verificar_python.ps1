# Script para verificar instalación de Python
# Ejecutar: .\verificar_python.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verificación de Instalación de Python" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$checks = @{
    "Python instalado" = $false
    "Python en PATH" = $false
    "Versión correcta (3.11+)" = $false
    "pip disponible" = $false
    "Django instalado" = $false
}

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $checks["Python instalado"] = $true
        $checks["Python en PATH"] = $true
        Write-Host "   ✅ Python encontrado: $pythonVersion" -ForegroundColor Green
        
        # Verificar versión
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 11)) {
                $checks["Versión correcta (3.11+)"] = $true
                Write-Host "   ✅ Versión correcta (3.11+)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Versión antigua: $pythonVersion (requiere 3.11+)" -ForegroundColor Yellow
            }
        }
    }
} catch {
        Write-Host "   ❌ Python no encontrado" -ForegroundColor Red
    }

Write-Host ""

# Verificar pip
Write-Host "2. Verificando pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $checks["pip disponible"] = $true
        Write-Host "   ✅ pip encontrado: $pipVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ pip no encontrado" -ForegroundColor Red
}

Write-Host ""

# Verificar ubicación
Write-Host "3. Verificando ubicación..." -ForegroundColor Yellow
try {
    $pythonPath = where.exe python 2>&1
    if ($pythonPath) {
        Write-Host "   ✅ Python en: $pythonPath" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  No se pudo determinar ubicación" -ForegroundColor Yellow
}

Write-Host ""

# Verificar Django
Write-Host "4. Verificando Django..." -ForegroundColor Yellow
try {
    $djangoVersion = python -c "import django; print(django.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $checks["Django instalado"] = $true
        Write-Host "   ✅ Django instalado: $djangoVersion" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Django no instalado" -ForegroundColor Yellow
        Write-Host "      Ejecuta: pip install -r requirements.txt" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Django no instalado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Resumen" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true
foreach ($check in $checks.GetEnumerator()) {
    $status = if ($check.Value) { "✅" } else { "❌" }
    $color = if ($check.Value) { "Green" } else { "Red"; $allOk = $false }
    Write-Host "$status $($check.Key)" -ForegroundColor $color
}

Write-Host ""

if ($allOk) {
    Write-Host "🎉 ¡Python está correctamente instalado y configurado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. cd backend" -ForegroundColor Gray
    Write-Host "  2. python manage.py makemigrations" -ForegroundColor Gray
    Write-Host "  3. python manage.py migrate" -ForegroundColor Gray
    Write-Host "  4. python manage.py test" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Hay problemas con la instalación de Python" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Cyan
    Write-Host "  1. Instala Python desde: https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "  2. Asegúrate de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Gray
    Write-Host "  3. Reinicia la terminal después de instalar" -ForegroundColor Gray
    Write-Host "  4. Ejecuta este script de nuevo para verificar" -ForegroundColor Gray
}

Write-Host ""
