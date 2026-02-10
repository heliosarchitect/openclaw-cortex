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
- **Fleet**: .163=giggletits (compute), .104=hpserver1 (Gitea/Prometheus), .107=woodserve1 (Pi-hole), .143=blackview (Wazuh), .198=bliss-rpi (SSH down)
- **SSH**: All remote servers on port 2222 ✅. giggletits still on 22 (local, low priority).
- **Docker**: No sudo needed on .104 and .107 (bonsaihorn in docker group). .143 no docker group.
- **Ansible**: ~/.ansible/ — inventory, playbooks, group_vars. Run from giggletits. All remote servers NOPASSWD.
- **Wazuh**: https://192.168.10.143 — 4 agents active. API password changed: `~/.secrets/wazuh-api.env`
- **LCARS**: http://giggletits:8090 — /itsm shows per-service status + Cortex panel
- **Services**: `systemctl --user status {openclaw-gateway,paper-augur,enhanced-collector}`
- **Collector**: MemoryMax=10G, running healthy. Gitea SSH on port 2223 (was 2222, conflicted with sshd).

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
