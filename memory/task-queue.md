# Task Queue — Night Shift Build List

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## ACTIVE SPRINT — 5 Helios Self-Improvements (Feb 12 Night)
- [x] 1. Memory Hygiene — deduped 1,648 entries (3,006→1,358 STM), cleaned orphan embeddings
- [x] 2. H0-4: Workspace File Internalization — COMPLETE (helios-sprint, 19:00)
- [ ] 3. SYNAPSE Protocol V2 — Nova building (task delegation, expiry, status tracking)
- [ ] 4. Memory Consolidation Engine — Nova building (cluster + LLM synthesis)
- [ ] 5. Self-Monitoring Dashboard — Nova building (metrics + Prometheus endpoint)

## Priority (do first)
- [x] Wire LLM fleet models into actual workflows — codex-review + email-triager in ~/bin/ (18:35)
- [ ] H0-5: Token budget tuning — analysis in progress (Nova)
- [x] H0-6: Turn counter — ~/bin/turn-counter, 9/9 tests, docs written (18:32)
- [x] brain.db: create systemd service for brain_api.py (port 8031) (11:07)
- [x] brain.db: concurrent write stress test — 6/6 green, 222 ops/sec (11:10)

## Available (grab any)
- [x] **WEMS**: Build World Event Monitoring System MCP server — earthquakes ✅, solar ✅, volcano ✅, tsunami ✅ (COMPLETE, 01:47)
- [x] AUGUR: comprehensive zero fee analysis report — analysis/augur-zero-fee-comprehensive-analysis.md (22:42)
- [❌] AUGUR: run signal_miner on CBETH-USD and DAI-USD (0% maker fee stable pairs) — process killed, 0 signals found
- [x] AUGUR: backtest existing patterns with 0% maker fee scenarios — 142,330 patterns become profitable at 0% maker fees (22:40)
- [ ] Create cron output validator script — in progress (Nova)
- [ ] Ansible: finish fleet hardening audit — in progress (Nova)
- [x] LCARS dashboard: add LLM fleet status panel — expanded from 7 to 16 models, 89% VRAM shown (19:47)
- [x] Write proper README for llm-fleet repo — enhanced with usage examples, deployment status, troubleshooting (19:33)
- [x] Clean up augur-collector WAL files (shm/wal in git status) — no WAL files found (21:33)
- [ ] Explore security-sentinel ClawHub skill for Wazuh integration
- [x] Build Gitea MCP server for direct repo management — 16 tools implemented, production ready (22:22)
- [x] brain.db: redirect cortex-bridge.ts daemon calls (/store, /search) to brain.db — 8031 port, /store→/remember (21:18)
- [x] AUGUR: collect 500+ V4 signals before considering live trading — 1,885 signals collected (22:23)
- [x] AUGUR: consider 0 bps fee trial from Coinbase — analysis complete at analysis/coinbase-fee-optimization-analysis.md (22:25)
- [x] Build ~/bin/token-efficiency script to track optimization metrics — analyzes session transcripts, tracks O/I ratio, cache hit rate, cost per output token (21:48)

## Completed (today)
- [x] **Context optimization research + tools** — token-efficiency-v2, context-optimizer based on HN/GitHub research (03:35)
- [x] WEMS MCP server completion — added volcano + tsunami monitoring (01:47)
- [x] OpenClaw Config Safety System — validation, snapshots, auto-rollback (Nova, 21:55)
- [x] BC/DR n8n Workflow Migration — cron→n8n with enhanced monitoring (Nova, 21:55)
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
