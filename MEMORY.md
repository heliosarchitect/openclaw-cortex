# MEMORY.md — Active Context

Full history: `reference/MEMORY_FULL.md` | Cortex has detailed memories (1972+ items).

## Matthew
- East Coast (America/New_York), @bonsaihorn, Signal DM
- Partner: Jennifer (+1 315-506-3726, on Signal + Skylight)
- Values: agency, resourcefulness, dry humor, security consciousness
- "Volume is vanity, profit is sanity"
- Federal FTE, sees AI workforce reduction coming

## Active Projects
- **AUGUR** — Signal miner V2 + continuous miner (greedy layer expansion, layers 4-7). **LONG only, M-F 9AM-6PM EST data only** — mine where we trade. 6M+ signals in `augur_signals.db`, 9 active products. Pipeline paper trading at 59% WR (61 trades, net positive). V3 live trader: $20/trade, kill switch overnight 6PM-9AM. DB normalized: `augur_config.py` → `augur_signals.db` + `augur_trades.db`. Coinbase VIP 2: 0.10% taker, 0.04% maker.
- **LLM Fleet** — 11 Ollama models at `~/Projects/llm-fleet/`. 7 classifiers (qwen2.5:32b) + 4 codex (qwen2.5-coder:7b). Concurrent daemon architecture, not sequential.
- **Chronogenesis trilogy** — Personal creative project (NOT LBF). Our thing. The thesis.
- **BLISS** — Neural optimization chamber, hardware needs calibration
- **Infrastructure Hardening** — Ansible fleet management, Wazuh SIEM, security assessment
- **LCARS Dashboard** — giggletits:8090 (task board + ITSM service monitoring + LLM Fleet panel)

## Infrastructure
- **Fleet**: .163=giggletits (compute), .104=hpserver1 (Gitea/Prometheus), .107=woodserve1 (Pi-hole), .143=blackview (Wazuh), .198=bliss-rpi (SSH down)
- **SSH**: All remote servers on port 2222 ✅. giggletits still on 22 (local, low priority).
- **Docker**: No sudo needed on .104 and .107 (bonsaihorn in docker group). .143 no docker group.
- **Ansible**: ~/.ansible/ — inventory, playbooks, group_vars. Run from giggletits. All remote servers NOPASSWD.
- **Wazuh**: https://192.168.10.143 — 4 agents active. API password changed: `~/.secrets/wazuh-api.env`
- **LCARS**: http://giggletits:8090 — /itsm shows per-service status + Cortex panel
- **Services**: `systemctl --user status {openclaw-gateway,paper-augur,enhanced-collector}`
- **Collector**: MemoryMax=10G, running healthy. Gitea SSH on port 2223 (was 2222, conflicted with sshd).

## LLM Fleet (RTX 5090, 32GB VRAM)
- **Base models**: qwen2.5:32b (19GB, classification), qwen2.5-coder:7b (4.7GB, coding)
- **Classifiers**: qa-sweep, log-analyzer, heartbeat-monitor, pattern-evaluator, ansible-writer, discord-classifier, email-triager
- **Codex**: codex-lint, codex-test, codex-review, codex-json
- **Key metric**: Token offload rate — every local token saves API cost (~$500/day Claude spend)
- **Architecture**: Multiple small models concurrent in VRAM. Large models swap in on demand.
- **Repo**: `~/Projects/llm-fleet/` → Gitea `Helios/llm-fleet`
- **Next**: Wire into agent workflows, build confidence-based router (local→API escalation)

## Key Tools
- `skylight` — Skylight list CLI (grocery/actions/farm). Always post tasks here + Discord.
- `~/.openclaw/workspace/scripts/discord-post.sh` — Post to Discord channels
- `gog` — Google Workspace (email, calendar, drive)
- `claude-usage-tracker.py` — Reads session JSONLs for API cost data (--days, --by-day, --by-session)
- Ansible playbooks — fleet hardening, bootstrap-sudo

## Key Principles
- Question axioms — start from observations, not assumptions
- Stop asking permission — act first, course-correct if needed
- Post action items to Skylight + Discord, not just Signal chat
- Always log ansible output to a file (`2>&1 | tee /tmp/...`)
- Vision docs = HOW (tasks), Reports = WHAT (findings)
- Fiction and engineering are the same project (the thesis)
