#!/bin/bash
# System Health Check — comprehensive status for heartbeat use
# Usage: ./system-health-check.sh [--json] [--brief]
# Exit codes: 0=healthy, 1=warnings, 2=critical

set -euo pipefail

MODE="${1:-}"
WARNINGS=0
CRITICALS=0
ISSUES=()

check() {
    local name="$1" cmd="$2" expected="$3"
    result=$(eval "$cmd" 2>/dev/null || echo "FAILED")
    if [[ "$result" == *"$expected"* ]]; then
        return 0
    else
        WARNINGS=$((WARNINGS + 1))
        ISSUES+=("⚠️ $name: got '$result', expected '$expected'")
        return 1
    fi
}

critical() {
    local name="$1" cmd="$2" expected="$3"
    result=$(eval "$cmd" 2>/dev/null || echo "FAILED")
    if [[ "$result" == *"$expected"* ]]; then
        return 0
    else
        CRITICALS=$((CRITICALS + 1))
        ISSUES+=("❌ $name: got '$result', expected '$expected'")
        return 1
    fi
}

# Core services
critical "brain-api" "curl -sf http://localhost:8031/health | jq -r .status" "ok"
critical "enhanced-collector" "systemctl --user is-active enhanced-collector" "active"
critical "augur-v4-scanner" "systemctl --user is-active augur-v4-scanner" "active"
critical "augur-v4-executor" "systemctl --user is-active augur-v4-executor" "active"

# n8n automation hub (hpserver1)
critical "n8n" "curl -sf -o /dev/null -w '%{http_code}' http://192.168.10.104:5678" "200"

# Supporting services  
check "augur-signal-tracker" "systemctl --user is-active augur-signal-tracker" "active"
check "augur-continuous-miner" "systemctl --user is-active augur-continuous-miner" "active"
check "helios-monitor" "systemctl --user is-active helios-monitor" "active"
check "embeddings-daemon" "curl -sf http://localhost:8030/health" "ok"

# Disk space (warn if < 20GB free)
FREE_GB=$(df -BG /home | tail -1 | awk '{print $4}' | tr -d 'G')
if [ "$FREE_GB" -lt 20 ]; then
    WARNINGS=$((WARNINGS + 1))
    ISSUES+=("⚠️ Low disk: ${FREE_GB}GB free")
fi

# Brain.db STM count
STM_COUNT=$(sqlite3 ~/.openclaw/workspace/memory/brain.db "SELECT COUNT(*) FROM stm;" 2>/dev/null || echo "0")

# AUGUR live trading status
LIVE_TRADES=$(tail -100 /tmp/augur-live-v4.log 2>/dev/null | grep -c "ENTERED" || echo "0")

if [ "$MODE" = "--brief" ]; then
    if [ $CRITICALS -gt 0 ]; then
        echo "CRITICAL: $CRITICALS issues"
        for i in "${ISSUES[@]}"; do [[ "$i" == "❌"* ]] && echo "  $i"; done
        exit 2
    elif [ $WARNINGS -gt 0 ]; then
        echo "WARN: $WARNINGS issues | STM:$STM_COUNT | Disk:${FREE_GB}GB"
        exit 1
    else
        echo "OK | STM:$STM_COUNT | Disk:${FREE_GB}GB | LiveTrades(1h):$LIVE_TRADES"
        exit 0
    fi
fi

echo "=== System Health $(date -Iseconds) ==="
echo "Criticals: $CRITICALS | Warnings: $WARNINGS"
echo "STM: $STM_COUNT | Disk: ${FREE_GB}GB free | Live trades (recent): $LIVE_TRADES"
if [ ${#ISSUES[@]} -gt 0 ]; then
    echo ""
    for issue in "${ISSUES[@]}"; do echo "  $issue"; done
fi
echo "=== Done ==="

[ $CRITICALS -gt 0 ] && exit 2
[ $WARNINGS -gt 0 ] && exit 1
exit 0
