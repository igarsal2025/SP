# Script para organizar documentación en subdirectorios
# Ejecutar cuando los archivos no estén bloqueados

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Organizando Documentación" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$docsPath = "docs"

# Crear directorios si no existen
$directories = @(
    "deployment",
    "security",
    "testing",
    "implementation",
    "guides",
    "troubleshooting",
    "summaries"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $docsPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Creado: $fullPath" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Moviendo archivos..." -ForegroundColor Yellow

# Deployment
$deploymentFiles = Get-ChildItem -Path $docsPath -Filter "*DEPLOYMENT*.md" -ErrorAction SilentlyContinue
$deploymentFiles += Get-ChildItem -Path $docsPath -Filter "*RENDER*.md" -ErrorAction SilentlyContinue
foreach ($file in $deploymentFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "deployment") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> deployment/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Security
$securityFiles = Get-ChildItem -Path $docsPath -Filter "*MFA*.md" -ErrorAction SilentlyContinue
$securityFiles += Get-ChildItem -Path $docsPath -Filter "*RATE*.md" -ErrorAction SilentlyContinue
$securityFiles += Get-ChildItem -Path $docsPath -Filter "*SEGURIDAD*.md" -ErrorAction SilentlyContinue
foreach ($file in $securityFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "security") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> security/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Testing
$testingFiles = Get-ChildItem -Path $docsPath -Filter "*TEST*.md" -ErrorAction SilentlyContinue
$testingFiles += Get-ChildItem -Path $docsPath -Filter "*RESULTADOS*.md" -ErrorAction SilentlyContinue
$testingFiles += Get-ChildItem -Path $docsPath -Filter "*VALIDACION*.md" -ErrorAction SilentlyContinue
foreach ($file in $testingFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "testing") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> testing/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Implementation
$implFiles = Get-ChildItem -Path $docsPath -Filter "*FASE*.md" -ErrorAction SilentlyContinue
$implFiles += Get-ChildItem -Path $docsPath -Filter "*IMPLEMENTACION*.md" -ErrorAction SilentlyContinue
$implFiles += Get-ChildItem -Path $docsPath -Filter "*P0*.md" -ErrorAction SilentlyContinue
foreach ($file in $implFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "implementation") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> implementation/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Guides
$guideFiles = Get-ChildItem -Path $docsPath -Filter "*GUIA*.md" -ErrorAction SilentlyContinue
$guideFiles += Get-ChildItem -Path $docsPath -Filter "*MANUAL*.md" -ErrorAction SilentlyContinue
$guideFiles += Get-ChildItem -Path $docsPath -Filter "*INSTRUCCIONES*.md" -ErrorAction SilentlyContinue
foreach ($file in $guideFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "guides") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> guides/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Troubleshooting
$troubleFiles = Get-ChildItem -Path $docsPath -Filter "*SOLUCION*.md" -ErrorAction SilentlyContinue
$troubleFiles += Get-ChildItem -Path $docsPath -Filter "*PROBLEMA*.md" -ErrorAction SilentlyContinue
$troubleFiles += Get-ChildItem -Path $docsPath -Filter "*DEBUG*.md" -ErrorAction SilentlyContinue
$troubleFiles += Get-ChildItem -Path $docsPath -Filter "TROUBLESHOOTING.md" -ErrorAction SilentlyContinue
foreach ($file in $troubleFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "troubleshooting") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> troubleshooting/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

# Summaries
$summaryFiles = Get-ChildItem -Path $docsPath -Filter "*RESUMEN*.md" -ErrorAction SilentlyContinue
$summaryFiles += Get-ChildItem -Path $docsPath -Filter "*ESTADO*.md" -ErrorAction SilentlyContinue
foreach ($file in $summaryFiles) {
    try {
        Move-Item -Path $file.FullName -Destination (Join-Path $docsPath "summaries") -Force -ErrorAction Stop
        Write-Host "  Movido: $($file.Name) -> summaries/" -ForegroundColor Gray
    } catch {
        Write-Host "  ERROR moviendo $($file.Name): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Organización completada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nota: Algunos archivos pueden no haberse movido si estaban abiertos." -ForegroundColor Yellow
Write-Host "Cierra los archivos y ejecuta este script nuevamente si es necesario." -ForegroundColor Yellow
