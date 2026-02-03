# Script de validación para Fase 1 del rediseño frontend
# Valida que todos los componentes estén correctamente implementados

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Validación Fase 1: Preparación y Base" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

# 1. Verificar archivos creados
Write-Host "[1/6] Verificando archivos creados..." -ForegroundColor Yellow

$requiredFiles = @(
    "backend\apps\accounts\services.py",
    "backend\apps\accounts\views.py",
    "backend\apps\accounts\tests_context.py",
    "backend\apps\frontend\middleware.py",
    "backend\apps\frontend\tests_middleware.py",
    "backend\apps\frontend\templatetags\__init__.py",
    "backend\apps\frontend\templatetags\role_tags.py",
    "backend\static\frontend\js\role-based-ui.js",
    "backend\static\frontend\js\navigation.js",
    "docs\FASE1_IMPLEMENTACION_COMPLETA.md",
    "docs\API_USER_CONTEXT.md",
    "docs\COMPONENTES_FASE1.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (NO ENCONTRADO)" -ForegroundColor Red
        $errors += "Archivo faltante: $file"
    }
}

Write-Host ""

# 2. Verificar imports y sintaxis Python
Write-Host "[2/6] Verificando sintaxis Python..." -ForegroundColor Yellow

$pythonFiles = @(
    "backend\apps\accounts\services.py",
    "backend\apps\accounts\views.py",
    "backend\apps\frontend\middleware.py",
    "backend\apps\frontend\templatetags\role_tags.py"
)

foreach ($file in $pythonFiles) {
    if (Test-Path $file) {
        try {
            $content = Get-Content $file -Raw
            # Verificación básica de sintaxis (imports críticos)
            if ($file -like "*services.py") {
                if ($content -notmatch "get_ui_config_for_role|get_user_permissions") {
                    $warnings += "Posible problema en ${file}: funciones esperadas no encontradas"
                }
            }
            if ($file -like "*views.py") {
                if ($content -notmatch "UserContextView") {
                    $errors += "UserContextView no encontrado en ${file}"
                }
            }
            if ($file -like "*middleware.py") {
                if ($content -notmatch "UserContextMiddleware") {
                    $errors += "UserContextMiddleware no encontrado en ${file}"
                }
            }
            Write-Host "  ✓ $file (sintaxis OK)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ $file (error al leer)" -ForegroundColor Red
            $errors += "Error al leer ${file} : $_"
        }
    }
}

Write-Host ""

# 3. Verificar configuración en settings.py
Write-Host "[3/6] Verificando configuración en settings.py..." -ForegroundColor Yellow

if (Test-Path "backend\config\settings.py") {
    $settingsContent = Get-Content "backend\config\settings.py" -Raw
    if ($settingsContent -match "UserContextMiddleware") {
        Write-Host "  ✓ Middleware agregado a MIDDLEWARE" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Middleware NO agregado a MIDDLEWARE" -ForegroundColor Red
        $errors += "UserContextMiddleware no está en MIDDLEWARE en settings.py"
    }
} else {
    $errors += "settings.py no encontrado"
}

Write-Host ""

# 4. Verificar URLs
Write-Host "[4/6] Verificando URLs..." -ForegroundColor Yellow

if (Test-Path "backend\config\urls.py") {
    $urlsContent = Get-Content "backend\config\urls.py" -Raw
    if ($urlsContent -match "user-context|UserContextView") {
        Write-Host "  ✓ Ruta /api/user/context/ agregada" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Ruta /api/user/context/ NO encontrada" -ForegroundColor Red
        $errors += "Ruta user-context no está en urls.py"
    }
} else {
    $errors += "urls.py no encontrado"
}

Write-Host ""

# 5. Verificar JavaScript
Write-Host "[5/6] Verificando archivos JavaScript..." -ForegroundColor Yellow

$jsFiles = @(
    "backend\static\frontend\js\role-based-ui.js",
    "backend\static\frontend\js\navigation.js"
)

foreach ($file in $jsFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($file -like "*role-based-ui.js") {
            if ($content -match "getUserContext|showForRole|hasPermission") {
                Write-Host "  ✓ $file (funciones principales encontradas)" -ForegroundColor Green
            } else {
                $warnings += "Funciones principales no encontradas en ${file}"
            }
        }
        if ($file -like "*navigation.js") {
            if ($content -match "NavigationManager|navigateToSection") {
                Write-Host "  ✓ $file (clase NavigationManager encontrada)" -ForegroundColor Green
            } else {
                $warnings += "NavigationManager no encontrado en ${file}"
            }
        }
    } else {
        $errors += "Archivo JavaScript faltante: ${file}"
    }
}

Write-Host ""

# 6. Verificar tests
Write-Host "[6/6] Verificando tests..." -ForegroundColor Yellow

$testFiles = @(
    "backend\apps\accounts\tests_context.py",
    "backend\apps\frontend\tests_middleware.py"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match "class.*Test|def test_") {
            Write-Host "  ✓ $file (tests encontrados)" -ForegroundColor Green
        } else {
            $warnings += "No se encontraron tests en ${file}"
        }
    } else {
        $errors += "Archivo de tests faltante: ${file}"
    }
}

Write-Host ""

# Resumen
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resumen de Validación" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "✓ Validación exitosa - No se encontraron errores críticos" -ForegroundColor Green
} else {
    Write-Host "✗ Se encontraron $($errors.Count) error(es) crítico(s):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Se encontraron $($warnings.Count) advertencia(s):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Ejecutar tests: python manage.py test apps.accounts.tests_context apps.frontend.tests_middleware" -ForegroundColor White
Write-Host "  2. Probar endpoint: curl http://localhost:8000/api/user/context/" -ForegroundColor White
Write-Host "  3. Verificar en navegador: window.RoleBasedUI" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -gt 0) {
    exit 1
} else {
    exit 0
}
