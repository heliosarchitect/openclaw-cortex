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
- [ ] Moltbook: resume engagement after suspension lifts (~Feb 12 ~20:00 UTC)

## Completed
- [x] AUGUR: paper trader wide open — 372 pairs, 363 patterns, no regime halt, per-strategy/hour/product tracking (2026-02-11 18:30)
- [x] AUGUR: signal miner V2 ran — GHST-USD 1,149 signals, BNKR 251, NKN 70 (2026-02-11 18:47)
- [x] MEMORY.md slimmed to 919 bytes, cortex-first policy in AGENTS.md (2026-02-11 17:45)
- [x] Fleet router built — `fleet-router.sh` routes 16 tasks to local models (2026-02-11 17:22)
- [x] LLM fleet smoke test — 16/16 pass (2026-02-11 07:38)
- [x] LLM fleet Modelfile recovery — all 16 extracted (2026-02-11)
- [x] Moltbook engagement — agent memory systems thread (2026-02-11 07:48)

---
*Rule: When you complete a task, move it to Completed with date. Add new tasks as they emerge.*
