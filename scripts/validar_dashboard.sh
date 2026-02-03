#!/bin/bash
# Script de validación manual del Dashboard
# Verifica que los endpoints y funcionalidades estén funcionando correctamente

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"

echo "🔍 Validación Manual del Dashboard"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para hacer requests
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing: $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET \
            -H "Content-Type: application/json" \
            -u "$USERNAME:$PASSWORD" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -u "$USERNAME:$PASSWORD" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ OK (${http_code})${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL (${http_code})${NC}"
        echo "Response: $body"
        return 1
    fi
}

# 1. Health Check
echo "1. Health Checks"
echo "----------------"
make_request "GET" "/health/" "" "Health check básico"
make_request "GET" "/health/detailed/" "" "Health check detallado"
echo ""

# 2. Dashboard KPIs
echo "2. Dashboard KPIs"
echo "-----------------"
# Necesitamos un sitec_id, asumimos que existe
SITEC_ID="${SITEC_ID:-1}"
make_request "GET" "/api/dashboard/kpi/?sitec_id=$SITEC_ID" "" "KPIs del dashboard"
echo ""

# 3. Tendencias
echo "3. Tendencias Históricas"
echo "------------------------"
make_request "GET" "/api/dashboard/trends/?type=month&periods=12" "" "Tendencias mensuales"
make_request "GET" "/api/dashboard/trends/?type=week&periods=6" "" "Tendencias semanales"
echo ""

# 4. Comparativos
echo "4. Comparativos"
echo "----------------"
make_request "GET" "/api/dashboard/comparatives/?sitec_id=$SITEC_ID" "" "Comparativos históricos"
echo ""

# 5. ABAC Policies
echo "5. ABAC Policies"
echo "----------------"
make_request "POST" "/api/policies/evaluate/" '{"action":"dashboard.view"}' "Evaluar política dashboard.view"
make_request "POST" "/api/policies/evaluate/" '{"action":"wizard.save"}' "Evaluar política wizard.save"
echo ""

# 6. AI Stats (si está disponible)
echo "6. AI Statistics"
echo "-----------------"
make_request "GET" "/api/ai/stats/" "" "Estadísticas de IA"
echo ""

echo "=================================="
echo -e "${GREEN}Validación completada${NC}"
echo ""
echo "Para verificar en el navegador:"
echo "  - Dashboard: $BASE_URL/dashboard/"
echo "  - Wizard: $BASE_URL/wizard/"
echo "  - Health: $BASE_URL/health/"
