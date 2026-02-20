# HEARTBEAT.md
#
# EMPTY BY DESIGN — triggers isHeartbeatContentEffectivelyEmpty() in OpenClaw,
# which skips the LLM API call entirely. Zero tokens burned on idle heartbeats.
#
# All event routing moved to cron systemEvents + n8n webhooks (2026-02-16):
#
# ACTIVE CRON EVENTS (these inject systemEvents that DO trigger full agent turns):
#   - ai-model-watch ............. hourly — runs ~/bin/ai-model-watch, alerts on new models
#   - AUGUR Trading Day Start .... 9:00 AM M-F — morning systems check
#   - AUGUR Trading Day End ...... 6:00 PM M-F — EOD performance report
#   - AUGUR EOD Analysis ......... 11:00 PM — deep daily analysis (isolated)
#   - AUGUR Daily Report ......... 6:00 PM M-F — formal report + Discord (isolated)
#   - AUGUR Signal Miner ......... 6:45 PM M-F — mine new signals (isolated)
#   - AUGUR DB Backup ............ 7:00 PM — database backups (isolated)
#   - Cortex Nightly Maintenance . 2:00 AM — STM cleanup, embedding sync
#   - Cortex Weekly Deep Review .. 2:00 AM Sun — high-access analysis, trimming
#   - Helios Nightly Backup ...... 3:00 AM — BC/DR to Google Drive
#   - Memory Hygiene ............. 4:00 AM — daily dedup + prune
#   - End of Day Reflection ...... 11:00 PM — commit, reflect, log
#   - Weekly QA Scrub ............ 4:00 AM Sun — infrastructure audit (isolated)
#   - Cancel 1Password ........... Feb 21 — one-shot reminder
#
# BUILD MODE: Moved to n8n. When n8n detects idle period, it injects a
#   systemEvent with a task from memory/task-queue.md. No heartbeat polling needed.
#
# CONTEXT ALERTS: OpenClaw has built-in context % tracking. No heartbeat needed.
#
# MATTHEW MESSAGES: Always trigger a full agent turn regardless of heartbeat state.
#
# To re-enable heartbeat processing, add non-comment content below this line.
