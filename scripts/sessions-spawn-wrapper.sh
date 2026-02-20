#!/bin/bash
# sessions-spawn wrapper with n8n event integration
#
# Usage: same as sessions_spawn, but sends completion events to n8n
# This wrapper should be used instead of direct sessions_spawn calls when n8n integration is desired

set -euo pipefail

# Capture start time
START_TIME=$(date +%s)
START_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Run sessions_spawn with all arguments
echo "Starting session with args: $*"
SESSION_OUTPUT=$(openclaw sessions_spawn "$@" 2>&1) 
EXIT_CODE=$?

# Capture end time and duration
END_TIME=$(date +%s)
END_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
DURATION=$((END_TIME - START_TIME))

# Extract session ID from output (format: agent:main:subagent:uuid)
SESSION_ID=$(echo "$SESSION_OUTPUT" | grep -oE 'agent:[^[:space:]]+' | head -1 || echo "unknown")

# Determine status
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="success"
else
    STATUS="failure"
fi

# Extract task description (first argument if provided, or use generic)
TASK_DESC="${1:-subagent-task}"

# Build event data
EVENT_DATA=$(jq -n \
    --arg session_id "$SESSION_ID" \
    --arg agent_type "subagent" \
    --arg duration "$DURATION" \
    --arg status "$STATUS" \
    --arg task "$TASK_DESC" \
    --arg start_time "$START_ISO" \
    --arg end_time "$END_ISO" \
    --arg output_preview "$(echo "$SESSION_OUTPUT" | head -3 | tr '\n' ' ' | cut -c1-200)" \
    ${EXIT_CODE:+--arg error "Exit code: $EXIT_CODE"} \
    '{
        session_id: $session_id,
        agent_type: $agent_type, 
        duration: ($duration | tonumber),
        status: $status,
        task: $task,
        start_time: $start_time,
        end_time: $end_time,
        output_preview: $output_preview
    } + (if $error then {error: $error} else {} end)')

# Send event to n8n (only if openclaw-event script exists and n8n integration is enabled)
if [ -x "$HOME/bin/openclaw-event" ] && [ "${N8N_INTEGRATION_ENABLED:-true}" = "true" ]; then
    "$HOME/bin/openclaw-event" "agent-complete" "$EVENT_DATA" &
    # Run in background to avoid blocking the main session result
fi

# Output the original session result
echo "$SESSION_OUTPUT"

# Preserve original exit code
exit $EXIT_CODE