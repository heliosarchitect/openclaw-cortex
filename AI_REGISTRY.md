# AI.REGISTRY — Issue Tracker Index
<!-- AI.REGISTRY: Machine-readable issue index across all Gitea repos.
  Read this to find issues without hitting the API. Updated by Helios.
  Format: repo#number [priority] [labels] title
  P0=fix now, P1=this sprint, P2=scheduled
  Last updated: 2026-02-12 19:40 EST | Total: 29 open issues
  CLI: ~/bin/gitea-issue list <repo> for live data
-->

## By Priority

### 🔴 P0 — Fix Now (1)
- augur-trading#1 [bug] Taker fees destroy micro-scalp edge

### 🟠 P1 — This Sprint (7)
- augur-trading#2 [feature] Implement maker-only order entry
- augur-trading#5 [bug] Paper trader regime halt infinite loop
- augur-trading#7 [research] patterns.db v2 → v3 signal architecture
- augur-trading#8 [research] Overfitting: 39.7% WR live vs 80%+ backtest
- brain-db#3 [bug] cortex_dedupe merge finds 0 despite 842 groups
- cortex#1 [feature] H0-4: Workspace file internalization
- cortex#8 [bug] Behavioral: incomplete follow-through

### 🟡 P2 — Scheduled (17)
- augur-trading#3 [research] GHST signal clustering and hold times
- augur-trading#4 [ops] 3 aborted sub-agents investigation
- augur-trading#6 [bug] Spread gate non-uniform across products
- augur-trading#9 [ops] Documentation update cron never set up
- augur-trading#10 [ops] Enhanced data DB needs pruning (16GB+)
- brain-db#1 [feature] Todo ↔ Gitea issue sync
- brain-db#2 [bug] SYNAPSE inbox stale messages
- cortex#2 [bug] Heartbeat replies repeat 3-4x
- cortex#3 [bug] Night shift 2.5h idle HEARTBEAT_OKs
- cortex#4 [bug] Permission-asking pattern
- cortex#5 [feature] Cross-context message sends
- cortex#6 [feature] QA gap: repos lack test suites
- cortex#7 [bug] Moltbook duplicate comment guard
- cortex#9 [ops] 41 missing skill requirements
- llm-fleet#1 [feature] Router model availability check
- lbf-dashboard#1 [feature] Stripe payment links/buy buttons

### Unprioritzed (4)
- bliss#1 BLISS Pi SSH down
- fleetwood-core#1 Wazuh dashboard API manual fix
- fleetwood-core#2 Pi-hole v6 dnsmasq.d ignored
- fleetwood-core#3 /boot partition 88% full
- fleetwood-core#4 Ansible SSH lockout risk

## By Repo

### Helios/augur-trading (10)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | P0 | bug | Taker fees destroy micro-scalp edge |
| 2 | P1 | feature | Implement maker-only order entry |
| 3 | P2 | research | GHST signal clustering and hold times |
| 4 | P2 | ops | 3 aborted sub-agents |
| 5 | P1 | bug | Paper trader regime halt infinite loop |
| 6 | P2 | bug | Spread gate non-uniform |
| 7 | P1 | research | v2→v3 signal architecture |
| 8 | P1 | research | Overfitting gap |
| 9 | P2 | ops | Doc update cron missing |
| 10 | P2 | ops | Enhanced DB pruning |

### Helios/brain-db (3)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | P2 | feature | Todo ↔ Gitea sync |
| 2 | P2 | bug | SYNAPSE inbox stale |
| 3 | P1 | bug | cortex_dedupe broken |

### Helios/cortex (9)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | P1 | feature | H0-4 workspace internalization |
| 2 | P2 | bug | Heartbeat repetition |
| 3 | P2 | bug | Night shift idle loop |
| 4 | P2 | bug | Permission-asking pattern |
| 5 | P2 | feature | Cross-context messaging |
| 6 | P2 | feature | QA test suite gap |
| 7 | P2 | bug | Moltbook dedup guard |
| 8 | P1 | bug | Incomplete follow-through |
| 9 | P2 | ops | Missing skill deps |

### Helios/llm-fleet (1)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | P2 | feature | Router availability check |

### Helios/bliss (1)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | — | — | SSH down on both ports |

### Helios/lbf-dashboard (1)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | P2 | feature | Stripe payment links |

### loverbearfarm/fleetwood-core (4)
| # | P | Labels | Title |
|---|---|--------|-------|
| 1 | — | — | Wazuh API manual fix |
| 2 | — | — | Pi-hole dnsmasq.d |
| 3 | — | — | /boot 88% full |
| 4 | — | — | SSH lockout risk |

---
*Updated manually or via: `for repo in ...; do ~/bin/gitea-issue list "$repo"; done`*
*When closing issues, update this file and remove the entry.*
