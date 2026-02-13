# Task Queue — Night Shift Build List

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## ACTIVE SPRINT — 5 Helios Self-Improvements (Feb 12 Night) 🚀
- [x] 1. Memory Hygiene — deduped 1,648 entries (3,006→1,358 STM), cleaned orphan embedlings
- [x] 2. H0-4: Workspace File Internalization — COMPLETE (helios-sprint, 19:00)
- [✅] 3. SYNAPSE Protocol V2 — COMPLETE (docs/SYNAPSE_V2.md specification, session timed out)
- [✅] 4. Memory Consolidation Engine — COMPLETE (scripts/memory-consolidation/, DBSCAN clustering + qwen2.5:32b synthesis)
- [✅] 5. Self-Monitoring Dashboard — COMPLETE (scripts/helios-monitor/, port 9090, Prometheus + alerts + web dash)

## Priority (do first)
- [x] Wire LLM fleet models into actual workflows — codex-review + email-triager in ~/bin/ (18:35)
- [✅] H0-5: Token budget tuning — COMPLETE: 800 token budget recommended (64% reduction, 99.8% confidence)
- [x] H0-6: Turn counter — ~/bin/turn-counter, 9/9 tests, docs written (18:32)
- [x] brain.db: create systemd service for brain_api.py (port 8031) (11:07)
- [x] brain.db: concurrent write stress test — 6/6 green, 222 ops/sec (11:10)

## Available (grab any)
- [x] **WEMS**: Build World Event Monitoring System MCP server — earthquakes ✅, solar ✅, volcano ✅, tsunami ✅ (COMPLETE, 01:47)
- [x] AUGUR: comprehensive zero fee analysis report — analysis/augur-zero-fee-comprehensive-analysis.md (22:42)
- [✅] AUGUR: stablecoin fee analysis (2bps vs 20bps impact) — analysis/stablecoin-fee-analysis.md (06:51)
- [x] AUGUR: backtest existing patterns with 0% maker fee scenarios — 142,330 patterns become profitable at 0% maker fees (22:40)
- [ ] Create cron output validator script — in progress (Nova)
- [ ] Ansible: finish fleet hardening audit — in progress (Nova)
- [x] LCARS dashboard: add LLM fleet status panel — expanded from 7 to 16 models, 89% VRAM shown (19:47)
- [x] Write proper README for llm-fleet repo — enhanced with usage examples, deployment status, troubleshooting (19:33)
- [x] Clean up augur-collector WAL files (shm/wal in git status) — no WAL files found (21:33)
- [x] Explore security-sentinel ClawHub skill for Wazuh integration — built comprehensive security-monitor skill (05:08)
- [x] Build Gitea MCP server for direct repo management — 16 tools implemented, production ready (22:22)
- [x] brain.db: redirect cortex-bridge.ts daemon calls (/store, /search) to brain.db — 8031 port, /store→/remember (21:18)
- [x] AUGUR: collect 500+ V4 signals before considering live trading — 1,885 signals collected (22:23)
- [x] AUGUR: consider 0 bps fee trial from Coinbase — analysis complete at analysis/coinbase-fee-optimization-analysis.md (22:25)
- [x] Build ~/bin/token-efficiency script to track optimization metrics — analyzes session transcripts, tracks O/I ratio, cache hit rate, cost per output token (21:48)

## Priority (do first)
- [📋] **Gateway Restart Ready** — ALL optimizations applied, restart instructions at memory/restart-instructions.md, ~11-16K token savings/turn waiting to activate (09:12)

## In Progress (today)
- (none currently)

## Completed (today)
- [x] **Gateway Restart Organization** — enabled commands.restart=true, created comprehensive restart instructions at memory/restart-instructions.md with validation checklist, all optimizations ready to activate (09:12)
- [x] **Tool Description Token Optimization** — compressed coreToolSummaries in system-prompt.ts: 45→4 tokens (cron), 28→5 tokens (session_status), ~200-250 tokens/turn saved, compiled successfully, analysis/tool-description-optimization.md (09:10)
- [x] **Token Efficiency Config Optimization** — applied maxContextTokens: 2000→800 (-1.2K/turn) + contextPruning TTL: 1h→20m (-10-15K/turn), documented at memory/config-changes-applied.md (08:33)
- [x] **Token Efficiency Deep Analysis** — Nova completed comprehensive analysis: scripts/token-efficiency-tracker.py built, 0.313% baseline confirmed, tier 1/2 strategy mapped, targeting 2-5x efficiency improvement (08:30)
- [x] **H0-7: Heartbeat Efficiency Redesign** — Nova delivered 3-stage plan (30%→63%→71% savings), n8n event-driven architecture, ready-to-apply cron migrations (07:43)
- [x] **Nova/Claude Code Setup** — Node.js via NVM + claude symlink, --local agent runs working (07:02)
- [x] **H0-5: Token Budget Tuning** — 800-token budget analysis complete, 64% reduction opportunity identified (07:06)
- [x] **Active Sprint Items 3-5** — All Nova tasks complete despite 30min timeouts (07:30)
- [x] **Security Monitor skill** — comprehensive Wazuh integration + system security scanning (05:08)
- [x] **WEMS MCP server packaging** — complete monetization infrastructure for MCP registry (05:05)
- [x] **Context optimization research + tools** — token-efficiency-v2, context-optimizer based on HN/GitHub research (03:35)
- [x] **Real API cost analysis** — $566.11 wasted on HEARTBEAT_OK (20.4% of $2,773.94 total spend), 1,581 waste turns (07:50)
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
