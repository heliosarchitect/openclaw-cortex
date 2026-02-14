#!/bin/bash
# Memory Hygiene — runs dedup + prune via consolidation engine
# Intended to run as OpenClaw cron (systemEvent) or standalone

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONSOLIDATE="$SCRIPT_DIR/memory-consolidation/consolidate.py"

echo "=== Memory Hygiene $(date -Iseconds) ==="

# Check if embedding server is up
if ! curl -s http://localhost:8030/health > /dev/null 2>&1; then
    echo "WARNING: Embedding server not available at :8030, skipping semantic dedup"
    echo "Only exact-match dedup will work"
fi

# Run prune (handles exact and near-duplicate removal)
echo "--- Pruning duplicates ---"
PRUNED=$(python3 "$CONSOLIDATE" prune 2>&1 | grep -oP 'Pruned: \K\d+' || echo "0")
echo "Pruned: $PRUNED memories"

# Run scan for cluster report
echo "--- Cluster scan ---"
python3 "$CONSOLIDATE" scan 2>&1 | tail -5

# Get final stats
TOTAL=$(sqlite3 ~/.openclaw/workspace/memory/brain.db "SELECT COUNT(*) FROM stm;" 2>/dev/null || echo "?")
echo "--- Final STM count: $TOTAL ---"
# Run workspace cleanup (dry run to report only)
echo "--- Workspace cleanup check ---"
CLEANUP_COUNT=$(bash "$SCRIPT_DIR/workspace-cleanup.sh" --dry 2>&1 | grep -oP 'Moved: \K\d+' || echo "0")
if [ "$CLEANUP_COUNT" -gt 0 ]; then
    echo "WARNING: $CLEANUP_COUNT files in workspace root need organizing"
    echo "Run: scripts/workspace-cleanup.sh to move them"
fi

echo "=== Done ==="
