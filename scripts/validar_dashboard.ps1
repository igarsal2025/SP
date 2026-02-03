# Script de validación manual del Dashboard (PowerShell)
# Verifica que los endpoints y funcionalidades estén funcionando correctamente

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$Username = "admin",
    [string]$Password = "admin123",
    [string]$SitecId = "1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validación Manual del Dashboard" -ForegroundColor Cyan
Write-Host "=================================="
Write-Host ""

# Función para hacer requests
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Data = $null,
        [string]$Description
    )
    
    Write-Host -NoNewline "Testing: $Description... "
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $cred = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${Username}:${Password}"))
    $headers["Authorization"] = "Basic $cred"
    
    try {
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri "$BaseUrl$Endpoint" `
                -Method GET `
                -Headers $headers `
                -UseBasicParsing `
                -ErrorAction Stop
        } else {
            $response = Invoke-WebRequest -Uri "$BaseUrl$Endpoint" `
                -Method POST `
                -Headers $headers `
                -Body $Data `
                -UseBasicParsing `
                -ErrorAction Stop
        }
        
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            Write-Host "✓ OK ($($response.StatusCode))" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ FAIL ($($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 1. Health Check
Write-Host "1. Health Checks" -ForegroundColor Yellow
Write-Host "----------------"
Test-Endpoint -Method "GET" -Endpoint "/health/" -Description "Health check básico"
Test-Endpoint -Method "GET" -Endpoint "/health/detailed/" -Description "Health check detallado"
Write-Host ""

# 2. Dashboard KPIs
Write-Host "2. Dashboard KPIs" -ForegroundColor Yellow
Write-Host "-----------------"
Test-Endpoint -Method "GET" -Endpoint "/api/dashboard/kpi/?sitec_id=$SitecId" -Description "KPIs del dashboard"
Write-Host ""

# 3. Tendencias
Write-Host "3. Tendencias Históricas" -ForegroundColor Yellow
Write-Host "------------------------"
Test-Endpoint -Method "GET" -Endpoint "/api/dashboard/trends/?type=month&periods=12" -Description "Tendencias mensuales"
Test-Endpoint -Method "GET" -Endpoint "/api/dashboard/trends/?type=week&periods=6" -Description "Tendencias semanales"
Write-Host ""

# 4. Comparativos
Write-Host "4. Comparativos" -ForegroundColor Yellow
Write-Host "----------------"
Test-Endpoint -Method "GET" -Endpoint "/api/dashboard/comparatives/?sitec_id=$SitecId" -Description "Comparativos históricos"
Write-Host ""

# 5. ABAC Policies
Write-Host "5. ABAC Policies" -ForegroundColor Yellow
Write-Host "----------------"
$dashboardPolicy = '{"action":"dashboard.view"}'
Test-Endpoint -Method "POST" -Endpoint "/api/policies/evaluate/" -Data $dashboardPolicy -Description "Evaluar política dashboard.view"

$wizardPolicy = '{"action":"wizard.save"}'
Test-Endpoint -Method "POST" -Endpoint "/api/policies/evaluate/" -Data $wizardPolicy -Description "Evaluar política wizard.save"
Write-Host ""

# 6. AI Stats
Write-Host "6. AI Statistics" -ForegroundColor Yellow
Write-Host "-----------------"
Test-Endpoint -Method "GET" -Endpoint "/api/ai/stats/" -Description "Estadísticas de IA"
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Validación completada" -ForegroundColor Green
Write-Host ""
Write-Host "Para verificar en el navegador:"
Write-Host "  - Dashboard: $BaseUrl/dashboard/"
Write-Host "  - Wizard: $BaseUrl/wizard/"
Write-Host "  - Health: $BaseUrl/health/"
