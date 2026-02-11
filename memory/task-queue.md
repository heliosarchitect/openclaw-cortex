# Task Queue — Night Shift Build List

When nothing's broken, BUILD. Pull from here, don't cycle HEARTBEAT_OK.

## Priority (do first)
- [ ] Wire LLM fleet models into actual workflows (codex-review on PR commits, email-triager on inbox)
- [ ] Fix Gitea workspace remote (needs repo creation + API token from Matthew)
- [ ] AUGUR: continuous miner V2 — greedy layer expansion on accumulating data
- [ ] H0-5: Budget tuning (reduce token spend per turn)
- [ ] H0-6: Turn counter (track conversation depth)

## Available (grab any)
- [ ] Create cron output validator script
- [ ] Ansible: finish fleet hardening audit
- [ ] LCARS dashboard: add LLM fleet status panel
- [ ] Write proper README for llm-fleet repo
- [ ] Clean up augur-collector WAL files (shm/wal in git status)
- [ ] Explore security-sentinel ClawHub skill for Wazuh integration

## Completed
- [x] Fleet router built — `fleet-router.sh` routes 16 tasks to local models, JSON validation, exit codes for API fallback, `~/bin/fleet` symlink (2026-02-11 17:22)
- [x] LLM fleet smoke test — 16/16 pass (2026-02-11 07:38)
- [x] LLM fleet Modelfile recovery — all 16 extracted (2026-02-11)
- [x] Moltbook engagement — agent memory systems thread (2026-02-11 07:48)

---
*Rule: When you complete a task, move it to Completed with date. Add new tasks as they emerge.*
