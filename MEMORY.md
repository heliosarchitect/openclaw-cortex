# MEMORY.md — Active Context

Full history: `reference/MEMORY_FULL.md` | Cortex has detailed memories (1972+ items).

## Matthew
- East Coast (America/New_York), @bonsaihorn, Signal DM
- Partner: Jennifer (+1 315-506-3726, on Signal + Skylight)
- Values: agency, resourcefulness, dry humor, security consciousness
- "Volume is vanity, profit is sanity"
- Federal FTE, sees AI workforce reduction coming

## Active Projects
- **AUGUR** — Phase 0 deployed (2026-02-08), 363 patterns, paper trading live
- **Chronogenesis trilogy** — Personal creative project (NOT LBF). Our thing. The thesis.
- **BLISS** — Neural optimization chamber, hardware needs calibration
- **Infrastructure Hardening** — Ansible fleet management, Wazuh SIEM, security assessment
- **LCARS Dashboard** — giggletits:8090 (task board + ITSM service monitoring)

## Infrastructure
- **Fleet**: .163=giggletits (compute), .104=hpserver1 (Gitea/Prometheus), .107=woodserve1 (Pi-hole), .143=blackview (Wazuh), .198=bliss-rpi
- **SSH**: All servers on port 2222. giggletits ssh needs restart.
- **Ansible**: ~/.ansible/ — inventory, playbooks, group_vars. Run from giggletits.
- **Wazuh**: https://192.168.10.143 — 4 agents active. API password still default (needs hardening).
- **LCARS**: http://giggletits:8090 — /itsm shows per-service status for entire fleet
- **Services**: `systemctl --user status {openclaw-gateway,paper-augur,enhanced-collector}`
- **Collector**: MemoryMax=2G is too low (needs 8G). /boot partition full on giggletits.

## Key Tools
- `skylight` — Skylight list CLI (grocery/actions/farm). Always post tasks here + Discord.
- `~/.openclaw/workspace/scripts/discord-post.sh` — Post to Discord channels
- `gog` — Google Workspace (email, calendar, drive)
- Ansible playbooks — fleet hardening, bootstrap-sudo

## Key Principles
- Question axioms — start from observations, not assumptions
- Stop asking permission — act first, course-correct if needed
- Post action items to Skylight + Discord, not just Signal chat
- Always log ansible output to a file (`2>&1 | tee /tmp/...`)
- Vision docs = HOW (tasks), Reports = WHAT (findings)
- Fiction and engineering are the same project (the thesis)
