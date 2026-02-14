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
- [✅] **WEMS**: Publish MCP server to registry — ✅ PyPI v1.5.3 published + GitHub pushed, ✅ MCP Registry LIVE (io.github.heliosarchitect/wems, published 2026-02-14), ✅ awesome-mcp-servers PR #1991 (pending review)

## Available (grab any)
- [x] **AUGUR**: Test live trader with new fee lookup system (monitor next live trades) — ✅ VERIFIED: fee_cache.db shows accurate per-product rates (0.1 bps for stablecoins, 10 bps for regular pairs vs old 60 bps assumptions)
- [x] **AUGUR**: Investigate paper trader P&L database corruption (NULL values) — ✅ RESOLVED: 0/16,683 NULL P&L entries found in paper_results.db

## In Progress (today)
- [✅] **CRYPTO-TAXES COMPLETE** — Both portfolios merged: 1,084,293 Form 8949 entries, Part I: -$43,370.82, Part II: +$3,514.56, Net: -$39,856.26 loss. Accountant package ready: ~/Projects/crypto-taxes/accountant-package-2025/ (214MB, 68MB zipped).

## Completed (today)
- [x] **🔧 DATA RETENTION SERVICE FIX** — Fixed failed systemd data-retention.service by correcting database path from non-existent `~/Projects/Chad_Volume_tracker/enhanced_data.db` to `~/Projects/augur-collector/enhanced_data.db`. Service now running successfully after 20h failure. (23:02)
- [x] **💰 CRYPTO TAX REPORT GENERATOR** — Built tax_report_generator.py for IRS Form 8949 compliance. FIFO methodology, matches 707,879 bot trades: $40.5M proceeds vs $40.5M cost basis = $11,896 net loss (short-term). Ready for TurboTax import. Remaining: $3,567 unrealized MON holdings. Will merge with Default portfolio data once complete. (21:35)
- [x] **🌬️ WEMS v1.4.0 AIR QUALITY** — Added check_air_quality MCP tool using OpenAQ v3 API (free, no key, global coverage). Tier-gated: free=US only/PM2.5+O3/max 3 stations, premium=global/6 pollutants/25 stations/city search/forecasts. AQI categories with colored icons 🟢→🟤. 34 new tests, all 223 pass. Version 1.3.0→1.4.0. Published to PyPI + pushed to GitHub/Gitea. (21:30)
- [x] **🔧 SYSTEM MAINTENANCE SCRIPT** — Built and deployed ~/bin/system-maintenance with comprehensive housekeeping: log rotation (Signal 11MB→1K lines), old augur log cleanup (10+ files), git branch cleanup, docker pruning, disk space monitoring (2% used, 214GB free), process health checks. Automated daily maintenance infrastructure. (19:39)
- [x] **🚀 WEMS MCP REGISTRY (1/3)** — Successfully published WEMS v1.1.1 to PyPI (https://pypi.org/project/wems-mcp-server/1.1.1/). Prepared awesome-mcp-servers PR (branch ready). MCP Registry requires manual GitHub OAuth. (19:34)
- [x] **🎯 AUGUR FULL ABSTRACTION** — wired fee_lookup.py into live trader, replaced hardcoded TAKER_FEE/MAKER_FEE with per-product lookups, RARI-USD/ZRO-USD now use accurate 0.10%/0.05% rates vs old ~0.60% assumptions, follows Matthew's 'no hardcoded values' principle (10:22)
- [x] **🚀 GATEWAY RESTART SUCCESSFUL** — tests passed (4932/4933), all token efficiency optimizations activated: config changes + tool description compression + conditional monitoring system, ~11-16K combined token savings per turn now live (09:46)
- [x] **🎯 MASSIVE TOKEN EFFICIENCY BREAKTHROUGH** — deployed conditional wake system, disabled 3 wasteful cron jobs, built 4 conditional monitors + consolidator, ~95% reduction in monitoring token waste (1.37M→50K tokens/day), tested and operational (09:30)
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
