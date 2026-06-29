#!/usr/bin/env bash
# ECO-IA Health Check — OVHcloud US | 135.148.232.10
set -euo pipefail
API_URL="${ECO_IA_API_URL:-http://135.148.232.10:8000}"
EXIT_CODE=0
GREEN="\033[0;32m"; RED="\033[0;31m"; YELLOW="\033[1;33m"; NC="\033[0m"

check() {
    local name="$1" cmd="$2"
    if eval "$cmd" &>/dev/null; then echo -e "${GREEN}✅${NC}  $name: OK"
    else echo -e "${RED}❌${NC}  $name: FAILED"; EXIT_CODE=1; fi
}
warn_check() {
    local name="$1" cmd="$2"
    if eval "$cmd" &>/dev/null; then echo -e "${GREEN}✅${NC}  $name: OK"
    else echo -e "${YELLOW}⚠️${NC}   $name: WARNING"; fi
}

echo "══════════════════════════════════════════════"
echo "  🌱 ECO-IA Health Check — $(date)"
echo "  Server: 135.148.232.10 (OVHcloud b3-8)"
echo "══════════════════════════════════════════════"
echo ""
echo "── API ──────────────────────────────────────"
check     "API /health"        "curl -sf --max-time 5 $API_URL/health"
warn_check "API /docs"         "curl -sf --max-time 5 $API_URL/docs"
echo ""
echo "── Docker Containers ────────────────────────"
check "eco-ia-api"       "docker inspect -f '{{.State.Running}}' eco-ia-api | grep -q true"
check "eco-ia-worker"    "docker inspect -f '{{.State.Running}}' eco-ia-worker | grep -q true"
check "eco-ia-beat"      "docker inspect -f '{{.State.Running}}' eco-ia-beat | grep -q true"
check "eco-ia-postgres"  "docker inspect -f '{{.State.Running}}' eco-ia-postgres | grep -q true"
check "eco-ia-redis"     "docker inspect -f '{{.State.Running}}' eco-ia-redis | grep -q true"
check "eco-ia-nginx"     "docker inspect -f '{{.State.Running}}' eco-ia-nginx | grep -q true"
check "eco-ia-prometheus" "docker inspect -f '{{.State.Running}}' eco-ia-prometheus | grep -q true"
check "eco-ia-grafana"   "docker inspect -f '{{.State.Running}}' eco-ia-grafana | grep -q true"
echo ""
echo "── Monitoring ───────────────────────────────"
warn_check "Prometheus" "curl -sf --max-time 5 http://135.148.232.10:9090/-/healthy"
warn_check "Grafana"    "curl -sf --max-time 5 http://135.148.232.10:3000/api/health"
echo ""
echo "── System ───────────────────────────────────"
DISK_PCT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
FREE_MB=$(free -m | awk 'NR==2 {print $7}')
[[ "$DISK_PCT" -lt 85 ]] && echo -e "${GREEN}✅${NC}  Disk: ${DISK_PCT}% used" \
    || { echo -e "${YELLOW}⚠️${NC}   Disk: ${DISK_PCT}% used (HIGH)"; EXIT_CODE=1; }
echo "ℹ️   RAM free: ${FREE_MB} MB"
echo ""
echo "══════════════════════════════════════════════"
[[ "$EXIT_CODE" -eq 0 ]] && echo -e "${GREEN}  Overall: HEALTHY ✅${NC}" \
    || echo -e "${RED}  Overall: DEGRADED ❌${NC}"
echo "══════════════════════════════════════════════"
exit "$EXIT_CODE"
