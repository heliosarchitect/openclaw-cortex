# Task Queue — Night Shift Build List

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## Priority (do first)
- [ ] Wire LLM fleet models into actual workflows (codex-review on PR commits, email-triager on inbox)
- [ ] Build EOD analysis pipeline — script that queries paper_results.db (strategy/hour/product stats) and feeds to local 32B model for winner/loser classification
- [ ] Fix Gitea workspace remote (needs repo creation + API token from Matthew)
- [ ] H0-5: Model cascade — Sonnet default, Opus for complex only (Matthew's endstate: "I should always be talking to sonnet"). Steps: heartbeat.model → Sonnet first, then default model → Sonnet with Opus escalation
- [ ] H0-6: Turn counter (track conversation depth)

## Available (grab any)
- [ ] Create cron output validator script
- [ ] Ansible: finish fleet hardening audit
- [ ] LCARS dashboard: add LLM fleet status panel
- [ ] Write proper README for llm-fleet repo
- [ ] Clean up augur-collector WAL files (shm/wal in git status)
- [ ] Explore security-sentinel ClawHub skill for Wazuh integration
- [ ] Moltbook: post eudaemon_0 supply chain reply (saved in memory/moltbook-pending-comment.md, suspension lifts ~15:00 EST Feb 12)
- [ ] Build brain.db implementation (SYNAPSE_UPGRADE.md approved, awaiting Nova for co-build)
- [ ] AUGUR: build strategy filter into live_augur.py (only spread_pct + imbalance_ma) based on pruning analysis

## Completed
- [x] Backup script created — `~/bin/backup_to_drive.sh`, 2.9MB → Google Drive (2026-02-12 03:00)
- [x] Paper trader 5hr checkpoint — 3,884 trades, 23.3% WR, +$18.07 PnL, spread_pct+imbalance_ma only profitable strategies (2026-02-12 03:02)
- [x] Analysis dir organized — 10 Python scripts → analysis/scripts/ subfolder (2026-02-12 03:32)
- [x] SYNAPSE upgrade doc written — unified brain.db architecture, Matthew approved (2026-02-11 23:30)
- [x] V3 liquidity analysis — 8 products analyzed, position sizing by book depth (2026-02-11 23:34)
- [x] Historical trading DB analysis — 1.83M fills, 3 accounts, Sept 2025 peak identified (2026-02-11 23:02)
- [x] AUGUR: paper trader wide open — 372 pairs, 363 patterns, no regime halt, per-strategy/hour/product tracking (2026-02-11 18:30)
- [x] AUGUR: signal miner V2 ran — GHST-USD 1,149 signals, BNKR 251, NKN 70 (2026-02-11 18:47)
- [x] MEMORY.md slimmed to 919 bytes, cortex-first policy in AGENTS.md (2026-02-11 17:45)
- [x] Fleet router built — `fleet-router.sh` routes 16 tasks to local models (2026-02-11 17:22)
- [x] LLM fleet smoke test — 16/16 pass (2026-02-11 07:38)
- [x] LLM fleet Modelfile recovery — all 16 extracted (2026-02-11)
- [x] Moltbook engagement — agent memory systems thread (2026-02-11 07:48)

---
*Rule: When you complete a task, move it to Completed with date. Add new tasks as they emerge.*
