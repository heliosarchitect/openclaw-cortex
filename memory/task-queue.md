# Task Queue — Night Shift Build List

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## Priority (do first)
- [x] Wire LLM fleet models into actual workflows — codex-review + email-triager in ~/bin/ (18:35)
- [ ] H0-5: Token budget tuning — analysis in progress (Nova)
- [x] H0-6: Turn counter — ~/bin/turn-counter, 9/9 tests, docs written (18:32)
- [x] brain.db: create systemd service for brain_api.py (port 8031) (11:07)
- [x] brain.db: concurrent write stress test — 6/6 green, 222 ops/sec (11:10)

## Available (grab any)
- [ ] Create cron output validator script — in progress (Nova)
- [ ] Ansible: finish fleet hardening audit — in progress (Nova)
- [ ] LCARS dashboard: add LLM fleet status panel
- [ ] Write proper README for llm-fleet repo
- [ ] Clean up augur-collector WAL files (shm/wal in git status)
- [ ] Explore security-sentinel ClawHub skill for Wazuh integration
- [ ] Moltbook: post eudaemon_0 supply chain reply (saved in memory/moltbook-pending-comment.md, suspension lifts ~15:00 EST Feb 12)
- [ ] Fix Gitea workspace remote (needs repo creation + API token from Matthew)
- [ ] brain.db: redirect cortex-bridge.ts daemon calls (/store, /search) to brain.db
- [ ] AUGUR: collect 500+ V4 signals before considering live trading (currently 457)
- [ ] AUGUR: consider 0 bps fee trial from Coinbase (current fees destroy gross edge)

## Completed (today)
- [x] brain_api.py — FastAPI REST server, 9 endpoints, port 8031 (10:47)
- [x] working_memory + categories → brain.db, 75/75 tests (10:50)
- [x] brain-cli Docker deployed to hpserver1 (10:47)
- [x] V4 executor product+strategy filters (10:49)
- [x] Nova: MCP tests 6/6, provenance_viz, brain_backup.py (10:23-10:29)
- [x] EOD analysis pipeline + cron (10:24)
- [x] Docker CLI image (brain-cli:latest, 198MB) (09:55)
- [x] git-commit-ai — local LLM commit message generator (10:20)
- [x] brain.db Phase 2-3: provenance, auto-extract, 75 tests green (08:00-10:00)
- [x] brain.db Phase 1: schema, CLI, all managers redirected (07:52-08:15)
- [x] AUGUR V4 blitz: scanner, regime, tracker, executor (07:00-07:50)
- [x] Enhanced collector crypto 24/7 fix (07:39)
- [x] Backup script + Google Drive (03:00)
- [x] Analysis dir organized (03:32)

---
*Rule: When you complete a task, move it to Completed with date. Add new tasks as they emerge.*
