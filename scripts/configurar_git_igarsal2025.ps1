# Script para configurar Git con usuario igarsal2025
# Ejecutar en PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurando Git para igarsal2025" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Eliminar credenciales antiguas
Write-Host "1. Eliminando credenciales antiguas..." -ForegroundColor Yellow
try {
    cmdkey /delete:"LegacyGeneric:target=git:https://igarsal2024@github.com" 2>$null
    Write-Host "   ✓ Credenciales de igarsal2024 eliminadas" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ No se encontraron credenciales de igarsal2024" -ForegroundColor Yellow
}

try {
    cmdkey /delete:"LegacyGeneric:target=GitHub for Visual Studio - https://igarsal2024@github.com/" 2>$null
    Write-Host "   ✓ Credenciales de Visual Studio eliminadas" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ No se encontraron credenciales de Visual Studio" -ForegroundColor Yellow
}

Write-Host ""

# 2. Verificar si hay repositorio Git
Write-Host "2. Verificando repositorio Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "   ✓ Repositorio Git encontrado" -ForegroundColor Green
    
    # Verificar remote actual
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Host "   Remote actual: $remote" -ForegroundColor Gray
        
        # Cambiar a igarsal2025 si es necesario
        if ($remote -match "igarsal2024") {
            Write-Host "   Cambiando remote a igarsal2025..." -ForegroundColor Yellow
            $newRemote = $remote -replace "igarsal2024", "igarsal2025"
            git remote set-url origin $newRemote
            Write-Host "   ✓ Remote actualizado: $newRemote" -ForegroundColor Green
        } elseif ($remote -notmatch "igarsal2025") {
            Write-Host "   Configurando remote con usuario igarsal2025..." -ForegroundColor Yellow
            if ($remote -match "https://github.com/([^/]+)/(.+)\.git") {
                $repo = $matches[2]
                $newRemote = "https://igarsal2025@github.com/igarsal2025/$repo.git"
                git remote set-url origin $newRemote
                Write-Host "   ✓ Remote configurado: $newRemote" -ForegroundColor Green
            }
        } else {
            Write-Host "   ✓ Remote ya está configurado para igarsal2025" -ForegroundColor Green
        }
    } else {
        Write-Host "   ⚠ No hay remote configurado" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ No hay repositorio Git inicializado" -ForegroundColor Yellow
    Write-Host "   Ejecuta 'git init' primero" -ForegroundColor Yellow
}

Write-Host ""

# 3. Instrucciones
Write-Host "3. Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   a) Crear Personal Access Token en GitHub:" -ForegroundColor Cyan
Write-Host "      - Ir a: https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host "      - Click 'Generate new token (classic)'" -ForegroundColor Gray
Write-Host "      - Marcar 'repo' (acceso completo)" -ForegroundColor Gray
Write-Host "      - Copiar el token" -ForegroundColor Gray
Write-Host ""
Write-Host "   b) Hacer push:" -ForegroundColor Cyan
Write-Host "      git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "   c) Cuando pida credenciales:" -ForegroundColor Cyan
Write-Host "      Usuario: igarsal2025" -ForegroundColor Gray
Write-Host "      Contraseña: [Pegar el Personal Access Token]" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuración completada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
