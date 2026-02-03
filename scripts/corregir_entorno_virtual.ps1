# Script para corregir entorno virtual con ubicación incorrecta de Python

Write-Host "🔧 Corrigiendo entorno virtual..." -ForegroundColor Cyan
Write-Host ""

# Verificar Python disponible
Write-Host "1. Buscando Python instalado..." -ForegroundColor Yellow

# Intentar diferentes ubicaciones comunes
$pythonPaths = @(
    "python",
    "py",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python3.14\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python3.13\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python3.12\python.exe",
    "C:\Python3.14\python.exe",
    "C:\Python3.13\python.exe",
    "C:\Python3.12\python.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    try {
        if ($path -eq "python" -or $path -eq "py") {
            $version = & $path --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $fullPath = (Get-Command $path).Source
                Write-Host "   ✅ Python encontrado: $fullPath" -ForegroundColor Green
                Write-Host "      Versión: $version" -ForegroundColor Gray
                $pythonExe = $fullPath
                break
            }
        } else {
            if (Test-Path $path) {
                $version = & $path --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "   ✅ Python encontrado: $path" -ForegroundColor Green
                    Write-Host "      Versión: $version" -ForegroundColor Gray
                    $pythonExe = $path
                    break
                }
            }
        }
    } catch {
        # Continuar buscando
    }
}

if (-not $pythonExe) {
    Write-Host "   ❌ Python no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Soluciones:" -ForegroundColor Yellow
    Write-Host "   1. Instalar Python desde python.org" -ForegroundColor Gray
    Write-Host "   2. Agregar Python al PATH del sistema" -ForegroundColor Gray
    Write-Host "   3. Usar 'py' launcher de Python" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Verificar si existe .venv
Write-Host "2. Verificando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   ⚠️  Entorno virtual existente encontrado (.venv)" -ForegroundColor Yellow
    Write-Host "   💡 Se recomienda recrear el entorno virtual" -ForegroundColor Yellow
    Write-Host ""
    
    $recrear = Read-Host "¿Deseas recrear el entorno virtual? (S/N)"
    if ($recrear -eq "S" -or $recrear -eq "s") {
        Write-Host ""
        Write-Host "   🗑️  Eliminando entorno virtual existente..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
        Write-Host "   ✅ Entorno virtual eliminado" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Manteniendo entorno virtual existente" -ForegroundColor Yellow
        Write-Host "   💡 Puedes intentar actualizar el entorno virtual manualmente" -ForegroundColor Gray
        exit 0
    }
} elseif (Test-Path "venv") {
    Write-Host "   ⚠️  Entorno virtual existente encontrado (venv)" -ForegroundColor Yellow
    Write-Host "   💡 Se recomienda recrear el entorno virtual" -ForegroundColor Yellow
    Write-Host ""
    
    $recrear = Read-Host "¿Deseas recrear el entorno virtual? (S/N)"
    if ($recrear -eq "S" -or $recrear -eq "s") {
        Write-Host ""
        Write-Host "   🗑️  Eliminando entorno virtual existente..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
        Write-Host "   ✅ Entorno virtual eliminado" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Manteniendo entorno virtual existente" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "   ℹ️  No se encontró entorno virtual existente" -ForegroundColor Gray
}

Write-Host ""

# Crear nuevo entorno virtual
Write-Host "3. Creando nuevo entorno virtual..." -ForegroundColor Yellow
Write-Host "   Usando: $pythonExe" -ForegroundColor Gray

try {
    & $pythonExe -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Entorno virtual creado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Error al crear entorno virtual" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Activar y verificar
Write-Host "4. Activando entorno virtual..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

if ($env:VIRTUAL_ENV) {
    Write-Host "   ✅ Entorno virtual activado: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Entorno virtual no se activó automáticamente" -ForegroundColor Yellow
    Write-Host "   💡 Ejecuta manualmente: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
}

Write-Host ""

# Instalar dependencias
Write-Host "5. Instalando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    & .venv\Scripts\python.exe -m pip install --upgrade pip
    & .venv\Scripts\python.exe -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Hubo algunos errores durante la instalación" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  requirements.txt no encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Proceso completado!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Activar entorno virtual: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   2. Navegar a backend: cd backend" -ForegroundColor Gray
Write-Host "   3. Ejecutar tests: python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2" -ForegroundColor Gray
