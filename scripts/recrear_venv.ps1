# Script rapido para recrear entorno virtual con Python correcto

Write-Host "Recreando entorno virtual..." -ForegroundColor Cyan
Write-Host ""

# Obtener Python actual
$pythonExe = (Get-Command python).Source
Write-Host "Python encontrado: $pythonExe" -ForegroundColor Green
$version = python --version
Write-Host "Version: $version" -ForegroundColor Gray
Write-Host ""

# Eliminar .venv si existe
if (Test-Path ".venv") {
    Write-Host "Eliminando .venv existente..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
    Write-Host "Eliminado" -ForegroundColor Green
    Write-Host ""
}

# Crear nuevo entorno virtual
Write-Host "Creando nuevo entorno virtual..." -ForegroundColor Yellow
python -m venv .venv

if ($LASTEXITCODE -eq 0) {
    Write-Host "Entorno virtual creado" -ForegroundColor Green
    Write-Host ""
    
    # Activar
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    
    # Verificar
    if ($env:VIRTUAL_ENV) {
        Write-Host "Activado: $env:VIRTUAL_ENV" -ForegroundColor Green
        Write-Host ""
        
        # Verificar Python en venv
        $venvPython = & .\.venv\Scripts\python.exe --version
        Write-Host "Python en venv: $venvPython" -ForegroundColor Green
        Write-Host ""
        
        # Instalar dependencias
        Write-Host "Instalando dependencias..." -ForegroundColor Yellow
        & .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
        & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "Listo! Entorno virtual recreado correctamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "Proximos pasos:" -ForegroundColor Cyan
        Write-Host "   cd backend" -ForegroundColor Gray
        Write-Host "   python manage.py test apps.ai.tests_throttling apps.accounts.tests_security apps.accounts.tests_abac_integration --verbosity=2" -ForegroundColor Gray
    } else {
        Write-Host "Activa manualmente: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    }
} else {
    Write-Host "Error al crear entorno virtual" -ForegroundColor Red
    exit 1
}
