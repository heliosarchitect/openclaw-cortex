#!/bin/bash
# Memory Event Webhook Integration
#
# This script sends memory events to n8n when significant memories are added or processed.
# It should be integrated into cortex operations and memory management workflows.
#
# Usage: memory-event-webhook.sh <event_type> <importance> <category> [content_preview] [agent] 
#
# Examples:
#   memory-event-webhook.sh "cortex_add" "2.5" "trading" "New AUGUR pattern discovered..." "helios"
#   memory-event-webhook.sh "insight_generated" "3.0" "technical" "Critical system insight..." "claude-code"
#   memory-event-webhook.sh "atom_create" "2.8" "learning" "Causal relationship identified..." "helios"

set -euo pipefail

EVENT_TYPE="${1:-}"
IMPORTANCE="${2:-1.0}"
CATEGORY="${3:-general}"
CONTENT_PREVIEW="${4:-}"
AGENT="${5:-openclaw}"

# Usage function
usage() {
    cat << EOF
Usage: $0 <event_type> <importance> <category> [content_preview] [agent]

Event Types:
  cortex_add         - New memory added to cortex
  insight_generated  - New insight generated from analysis
  atom_create        - New atomic knowledge unit created
  pattern_detected   - Pattern recognition event
  dedup_complete     - Memory deduplication completed
  
Parameters:
  importance    - Importance score (0.0-3.0, threshold for alerting: >2.0)
  category      - Memory category (trading, technical, personal, etc.)
  content_preview - First ~100 chars of content (optional)
  agent         - Agent that generated the event (optional)

Examples:
  $0 cortex_add 2.5 trading "AUGUR V4 discovered new pattern..."
  $0 insight_generated 3.0 technical "Critical security vulnerability found" claude-code
EOF
}

# Validate inputs
if [[ -z "$EVENT_TYPE" ]]; then
    usage
    exit 1
fi

# Validate importance score
if ! echo "$IMPORTANCE" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
    echo "ERROR: Invalid importance score: $IMPORTANCE" >&2
    exit 1
fi

# Check if importance meets threshold (only send events for importance > 2.0 unless explicitly enabled)
IMPORTANCE_THRESHOLD="${MEMORY_EVENT_THRESHOLD:-2.0}"
if (( $(echo "$IMPORTANCE < $IMPORTANCE_THRESHOLD" | bc -l) )); then
    # Exit silently for low-importance events unless debugging
    if [[ "${MEMORY_EVENT_DEBUG:-false}" == "true" ]]; then
        echo "DEBUG: Skipping low-importance event ($IMPORTANCE < $IMPORTANCE_THRESHOLD)"
    fi
    exit 0
fi

# Truncate content preview
if [[ -n "$CONTENT_PREVIEW" ]]; then
    CONTENT_PREVIEW=$(echo "$CONTENT_PREVIEW" | cut -c1-200)
fi

# Build event data
EVENT_DATA=$(jq -n \
    --arg type "$EVENT_TYPE" \
    --arg importance "$IMPORTANCE" \
    --arg category "$CATEGORY" \
    --arg agent "$AGENT" \
    --arg timestamp "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    $([ -n "$CONTENT_PREVIEW" ] && echo --arg content_preview "$CONTENT_PREVIEW") \
    '{
        type: $type,
        importance: ($importance | tonumber),
        category: $category,
        agent: $agent,
        timestamp: $timestamp
    } + (if $content_preview then {content_preview: $content_preview} else {} end)')

# Check if openclaw-event exists and n8n integration is enabled
if [[ ! -x "$HOME/bin/openclaw-event" ]]; then
    echo "ERROR: openclaw-event script not found or not executable" >&2
    exit 1
fi

if [[ "${N8N_INTEGRATION_ENABLED:-true}" != "true" ]]; then
    echo "DEBUG: n8n integration disabled, skipping event" >&2
    exit 0
fi

# Send event to n8n (run in background to avoid blocking)
"$HOME/bin/openclaw-event" "memory-event" "$EVENT_DATA" &

# Log event for debugging
if [[ "${MEMORY_EVENT_DEBUG:-false}" == "true" ]]; then
    echo "$(date): Memory event sent - $EVENT_TYPE (importance: $IMPORTANCE, category: $CATEGORY)" >> /tmp/memory-events-debug.log
fi