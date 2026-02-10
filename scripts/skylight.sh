#!/usr/bin/env bash
# skylight.sh — Skylight list management CLI
# Usage:
#   skylight.sh list [grocery|actions|farm_store]
#   skylight.sh add <list> "item text"
#   skylight.sh add <list> "item1" "item2" "item3"
#   skylight.sh done <list> <item_id>
#   skylight.sh remove <list> <item_id>
#   skylight.sh calendar [days]
#
# Requires: ~/.secrets/skylight.env with SKYLIGHT_EMAIL and SKYLIGHT_PASSWORD

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/skylight.py" "$@"
