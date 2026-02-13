# AI.REGISTRY — Issue Tracker Index
<!-- AI.REGISTRY: Machine-readable issue index across all Gitea repos.
  Read this to find issues without hitting the API.
  Format: repo#number [priority] [labels] title
  P0=fix now, P1=this sprint, P2=scheduled
  Last updated: 2026-02-12 19:50 EST
  Open: 22 | Closed: 7 | Total filed: 29
  CLI: ~/bin/gitea-issue list <repo> for live data
-->

## Open Issues (22)

### 🔴 P0 — Fix Now (1)
- augur-trading#1 [bug] Taker fees destroy micro-scalp edge

### 🟠 P1 — This Sprint (5)
- augur-trading#2 [feature] Implement maker-only order entry
- augur-trading#7 [research] patterns.db v2 → v3 signal architecture
- augur-trading#8 [research] Overfitting: 39.7% WR live vs 80%+ backtest
- brain-db#3 [bug] cortex_dedupe merge finds 0 despite 842 groups
- cortex#1 [feature] H0-4: Workspace file internalization
- cortex#8 [bug] Incomplete follow-through pattern

### 🟡 P2 — Scheduled (13)
- augur-trading#3 [research] GHST signal clustering and hold times
- augur-trading#6 [bug] Spread gate non-uniform across products
- augur-trading#9 [ops] Documentation update cron missing
- brain-db#1 [feature] Todo ↔ Gitea issue sync
- brain-db#2 [bug] SYNAPSE inbox stale messages
- cortex#4 [bug] Permission-asking pattern
- cortex#5 [feature] Cross-context message sends
- cortex#6 [feature] QA test suite gap
- cortex#7 [bug] Moltbook dedup guard
- llm-fleet#1 [feature] Router availability check
- lbf-dashboard#1 [feature] Stripe payment links

### Unprioritized (3)
- bliss#1 BLISS Pi SSH auth failure (port 2222 responds, key mismatch)
- fleetwood-core#2 Pi-hole v6 dnsmasq.d ignored
- fleetwood-core#3 /boot 83% full (autoremove failed, initramfs-tools error)
- fleetwood-core#4 Ansible SSH lockout risk

## Recently Closed (7)

| Issue | Fixed By | Fix | Prevention |
|-------|----------|-----|------------|
| augur-trading#4 | Helios | External abort, not code failure | Sub-agents should checkpoint to disk |
| augur-trading#5 | Helios | Watchdog detects stuck halt loops | Add hysteresis to regime detection |
| augur-trading#10 | Helios | Manual prune 1.28M+19.5M rows | Automated weekly prune cron needed |
| cortex#2 | Helios+Matthew | Anti-repetition rule in HEARTBEAT.md | State tracking between heartbeats |
| cortex#3 | Helios | Anti-idle mandate: max 2 HEARTBEAT_OKs | Task queue pull on 3rd idle |
| cortex#9 | Helios | `openclaw doctor --fix` | Run doctor after new skills |
| fleetwood-core#1 | Helios | Wazuh dashboard reconnected to API | Add API health monitoring |

---
*Update: close issues with `~/bin/gitea-issue close <repo> <#> -c "details"`*
*Refresh: `for repo in ...; do ~/bin/gitea-issue list "$repo"; done`*
