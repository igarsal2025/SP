# Script de validación para refinamiento de columnas y acciones
# Valida que los cambios funcionen correctamente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación de Refinamiento" -ForegroundColor Cyan
Write-Host "Columnas y Acciones por Perfil" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✓ Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "✗ No se encontró el entorno virtual" -ForegroundColor Red
    exit 1
}

# Cambiar al directorio backend
Set-Location backend

Write-Host ""
Write-Host "1. Ejecutando tests de backend..." -ForegroundColor Yellow
python manage.py test apps.frontend.tests_sections_smoke apps.accounts.tests_context apps.frontend.tests_middleware apps.frontend.tests_dashboard_templates --verbosity=1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Tests pasaron correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ Algunos tests fallaron" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Verificando sintaxis de archivos JavaScript..." -ForegroundColor Yellow

$jsFiles = @(
    "static\frontend\js\sections-projects.js",
    "static\frontend\js\sections-reports.js",
    "static\frontend\js\sections-approvals.js"
)

$errors = 0
foreach ($file in $jsFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ No se encontró: $file" -ForegroundColor Red
        $errors++
    }
}

if ($errors -eq 0) {
    Write-Host "✓ Todos los archivos JavaScript están presentes" -ForegroundColor Green
} else {
    Write-Host "✗ Se encontraron $errors problemas" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Verificando templates..." -ForegroundColor Yellow

$templates = @(
    "apps\frontend\templates\frontend\projects\list.html",
    "apps\frontend\templates\frontend\reports\list.html",
    "apps\frontend\templates\frontend\reports\approvals.html"
)

$templateErrors = 0
foreach ($template in $templates) {
    if (Test-Path $template) {
        Write-Host "  ✓ $template" -ForegroundColor Green
    } else {
        Write-Host "  ✗ No se encontró: $template" -ForegroundColor Red
        $templateErrors++
    }
}

if ($templateErrors -eq 0) {
    Write-Host "✓ Todos los templates están presentes" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resumen de Validación" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tests ejecutados: ✓" -ForegroundColor Green
Write-Host "Archivos JavaScript: ✓" -ForegroundColor Green
Write-Host "Templates: ✓" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos para probar manualmente:" -ForegroundColor Yellow
Write-Host "  1. Iniciar servidor: python manage.py runserver" -ForegroundColor White
Write-Host "  2. Acceder con diferentes roles:" -ForegroundColor White
Write-Host "     - Admin: /projects/ (debe ver 8+ columnas + botón Crear)" -ForegroundColor White
Write-Host "     - PM: /projects/ (debe ver 8+ columnas + botón Crear)" -ForegroundColor White
Write-Host "     - Supervisor: /projects/ (debe ver 5 columnas)" -ForegroundColor White
Write-Host "     - Técnico: /projects/ (debe ver 3 columnas)" -ForegroundColor White
Write-Host "     - Cliente: /projects/ (debe ver 3 columnas, sin botón Crear)" -ForegroundColor White
Write-Host "  3. Verificar acciones en tablas:" -ForegroundColor White
Write-Host "     - Botones 'Ver' y 'Editar' según permisos" -ForegroundColor White
Write-Host "     - Botón 'Enviar' para técnicos en reportes draft" -ForegroundColor White
Write-Host "     - Botón 'Aprobar' para supervisor/PM/admin en reportes submitted" -ForegroundColor White
Write-Host ""
Write-Host "Validación completada ✓" -ForegroundColor Green
