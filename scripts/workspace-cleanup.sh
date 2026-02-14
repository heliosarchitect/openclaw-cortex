#!/bin/bash
# Workspace Cleanup — moves loose files from workspace root to proper subdirectories
# Run: ./scripts/workspace-cleanup.sh [--dry]

set -euo pipefail

WS="$HOME/.openclaw/workspace"
DRY="${1:-}"
MOVED=0

# Protected files that belong in root
PROTECTED="SOUL.md IDENTITY.md USER.md MEMORY.md AGENTS.md TOOLS.md HEARTBEAT.md CHANGELOG.md HELIOS_VISION.md BOOTSTRAP.md .gitignore README.md"

move_file() {
    local src="$1" dest_dir="$2"
    local fname=$(basename "$src")
    
    # Skip protected files
    for p in $PROTECTED; do
        [[ "$fname" == "$p" ]] && return
    done
    
    mkdir -p "$dest_dir"
    if [[ "$DRY" == "--dry" ]]; then
        echo "[DRY] $fname → $dest_dir/"
    else
        mv "$src" "$dest_dir/"
        echo "Moved: $fname → $dest_dir/"
    fi
    MOVED=$((MOVED + 1))
}

echo "=== Workspace Cleanup $(date -Iseconds) ==="

# Python scripts → scripts/ or analysis/
for f in "$WS"/*.py; do
    [[ -f "$f" ]] || continue
    fname=$(basename "$f")
    case "$fname" in
        *test*|*check*|*verify*|*investigate*|*analyze*|*pattern*|*backtest*)
            move_file "$f" "$WS/analysis"
            ;;
        *fix*|*migrate*|*deploy*|*build*)
            move_file "$f" "$WS/scripts"
            ;;
        *)
            move_file "$f" "$WS/scripts"
            ;;
    esac
done

# Loose shell scripts → scripts/
for f in "$WS"/*.sh; do
    [[ -f "$f" ]] || continue
    move_file "$f" "$WS/scripts"
done

# CSV/JSON data files → analysis/
for f in "$WS"/*.csv "$WS"/*.json; do
    [[ -f "$f" ]] || continue
    fname=$(basename "$f")
    # Skip config files
    [[ "$fname" == "package.json" || "$fname" == "tsconfig.json" ]] && continue
    move_file "$f" "$WS/analysis"
done

# Excel/PDF → reports/
for f in "$WS"/*.xlsx "$WS"/*.pdf; do
    [[ -f "$f" ]] || continue
    move_file "$f" "$WS/reports"
done

# TOML → analysis/
for f in "$WS"/*.toml; do
    [[ -f "$f" ]] || continue
    move_file "$f" "$WS/analysis"
done

# Loose markdown (non-protected) → reports/
for f in "$WS"/*.md; do
    [[ -f "$f" ]] || continue
    fname=$(basename "$f")
    skip=false
    for p in $PROTECTED; do
        [[ "$fname" == "$p" ]] && skip=true && break
    done
    $skip && continue
    move_file "$f" "$WS/reports"
done

echo "=== Moved: $MOVED files ==="
