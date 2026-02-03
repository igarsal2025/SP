# Script PowerShell para ejecutar pruebas E2E con Playwright
# Uso: .\scripts\run_e2e_tests.ps1 [opciones]

param(
    [string]$TestFile = "",
    [switch]$UI = $false,
    [switch]$Debug = $false,
    [switch]$Headed = $false,
    [switch]$Install = $false
)

Write-Host "=== Ejecutando Pruebas E2E con Playwright ===" -ForegroundColor Cyan

# Verificar que Node.js esté instalado
try {
    $nodeVersion = node --version
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}

# Verificar que npm esté instalado
try {
    $npmVersion = npm --version
    Write-Host "npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: npm no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}

# Instalar dependencias si es necesario
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
}

# Instalar navegadores de Playwright si es necesario
if ($Install) {
    Write-Host "Instalando navegadores de Playwright..." -ForegroundColor Yellow
    npx playwright install
}

# Verificar que el servidor Django esté corriendo
Write-Host "Verificando que el servidor Django esté corriendo..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health/" -Method GET -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Servidor Django está corriendo" -ForegroundColor Green
    }
} catch {
    Write-Host "ADVERTENCIA: No se pudo conectar al servidor Django en http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host "Asegúrate de que el servidor esté corriendo antes de ejecutar las pruebas" -ForegroundColor Yellow
    Write-Host "Ejecuta: cd backend && python manage.py runserver" -ForegroundColor Yellow
}

# Construir comando de Playwright
$playwrightCmd = "npx playwright test"

if ($TestFile -ne "") {
    $playwrightCmd += " $TestFile"
}

if ($UI) {
    $playwrightCmd += " --ui"
}

if ($Debug) {
    $playwrightCmd += " --debug"
}

if ($Headed) {
    $playwrightCmd += " --headed"
}

# Ejecutar pruebas
Write-Host "Ejecutando: $playwrightCmd" -ForegroundColor Cyan
Invoke-Expression $playwrightCmd

# Mostrar reporte si las pruebas terminaron
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Pruebas completadas exitosamente ===" -ForegroundColor Green
    Write-Host "Para ver el reporte HTML, ejecuta: npm run test:e2e:report" -ForegroundColor Cyan
} else {
    Write-Host "`n=== Algunas pruebas fallaron ===" -ForegroundColor Red
    Write-Host "Revisa los resultados en test-results/ y playwright-report/" -ForegroundColor Yellow
}

exit $LASTEXITCODE
