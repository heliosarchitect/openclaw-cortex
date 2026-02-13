# QA & Monitoring Framework — Vision Document
<!-- AI.TOC: QA & Monitoring Framework — Vision Document — Read lines 1-20 for navigation.
  §1 Table of Contents                          → lines 17-31
  §2 1. Purpose & Scope                         → lines 32-66
  §3 2. Current State                           → lines 67-87
  §4 3. Target State                            → lines 88-128
  §5 4. Architecture                            → lines 129-201
  §6 5. Service Level Targets                   → lines 202-214
  §7 6. Tasks & Milestones                      → lines 215-240
  §8 7. Risks & Blockers                        → lines 241-253
  §9 8. Decision Log                            → lines 254-265
  §10 9. Configuration Items                     → lines 266-280
  §11 10. Definition of Done                     → lines 281-299
  Total: 299 lines | Sections: 11
-->

> *Zero manual health checks. Every LBF system has automated tests with green/red status logged to the Enterprise Task Board.*

| Field | Value |
|-------|-------|
| **Program** | QA & Monitoring Framework |
| **Parent** | LBF / Helios Operations |
| **Owner** | Helios |
| **Status** | Active |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-09 |
| **ITIL Process** | Service Operation · Continual Service Improvement |

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [Current State](#2-current-state)
3. [Target State](#3-target-state)
4. [Architecture](#4-architecture)
5. [Service Level Targets](#5-service-level-targets)
6. [Tasks & Milestones](#6-tasks--milestones)
7. [Risks & Blockers](#7-risks--blockers)
8. [Decision Log](#8-decision-log)
9. [Configuration Items](#9-configuration-items)
10. [Definition of Done](#10-definition-of-done)

---

## 1. Purpose & Scope

### What

Comprehensive automated QA sweeps across all LBF systems with adaptive cadence: daily by default, escalating to hourly on failures, relaxing to weekly once stable. No manual health checks. All results logged to the Enterprise Task Board with automatic task creation on failures.

### Why

Today we monitor **nothing formally**. If something breaks at 3 AM, we find out when Matthew asks "why isn't X working?" That's not monitoring. That's hoping. 

Every production environment needs:
- Proactive failure detection before user impact
- Automated remediation where possible
- Clear escalation paths for human intervention
- Historical trend data for capacity planning
- SLA compliance measurement

### Scope

- **In scope:**
  - Local services on giggletits (.163): AUGUR, OpenClaw, Ollama, LCARS dashboard
  - External service validation: Discord, Skylight, Moltbook, Google Workspace
  - Network infrastructure: SSH connectivity, service endpoints
  - Data freshness and quality checks
  - Automated task creation/resolution on Enterprise Task Board
  - Discord #system-health reporting

- **Out of scope:**
  - Performance optimization (separate from health monitoring)
  - Log aggregation (that's Wazuh's domain)
  - User-facing monitoring dashboards (that's ITSM/SLA dashboard)
  - Manual intervention workflows (focus on automation)

---

## 2. Current State

Today we monitor **nothing formally**. What exists:

| System | Current "Monitoring" | What Actually Happens |
|--------|---------------------|----------------------|
| AUGUR (paper trader) | Heartbeat glances | Helios checks `systemctl --user status paper-augur` during heartbeats. No alerting. No data freshness checks. |
| AUGUR (collector) | Same | `systemctl --user status enhanced-collector` — eyeball check |
| OpenClaw gateway | Self-recovers usually | Gateway has internal health, but no external watchdog |
| Skylight sync | Nothing | Script exists but isn't wired into any schedule or monitor |
| Discord bot | Nothing | Would only notice if a post fails |
| Gitea (.104) | Nothing | No SSH access currently, can't even check |
| Pi-hole/Wazuh (.107) | Nothing | No SSH access currently |
| BLISS RPi (.198) | Nothing | Paired node, can ping |
| Network infra | Nothing | No nmap, no port scanning, no anomaly detection |
| systemd services | Manual | `systemctl --user list-units --state=failed` — never automated |

**Translation:** If something breaks at 3 AM, we find out when Matthew asks "why isn't X working?" That's not monitoring. That's hoping.

---

## 3. Target State

```
QA SWEEP ENGINE (qa-sweep.py)

RUNS: cron job or systemd timer
CADENCE: Daily (default) → Hourly (on failure) → Weekly (stable)
REPORTS TO: LBF Enterprise Task Board + Discord #system-health
ALERTS: Discord always, Signal only for critical failures

TEST SUITES:
├── LOCAL SERVICES (giggletits / .163)
│   ├── systemd: paper-augur, enhanced-collector, openclaw-gateway
│   ├── AUGUR: data freshness (< 5min), trade count, WR trend
│   ├── Collector: DB size, last write timestamp, memory usage
│   ├── OpenClaw: /health endpoint, gateway uptime
│   ├── Dashboard: HTTP 200 on :8090, auth works
│   ├── Ollama: model list responds, GPU allocation
│   └── Disk/Memory: usage thresholds (90% warn, 95% crit)
│
├── EXTERNAL SERVICES
│   ├── Discord bot: can post to #system-health
│   ├── Skylight API: auth valid, list operations work
│   ├── Moltbook: login check
│   └── Google Workspace: gog auth valid
│
└── NETWORK (when SSH available)
    ├── .104 (Gitea): SSH reachable, Gitea HTTP responds
    ├── .107 (woodserve1): SSH reachable, Pi-hole responds
    ├── .198 (BLISS RPi): ping/paired node check
    └── .103 (WiFi repeater): ping

ESCALATION:
├── All pass → next run in 24h (or 168h if stable streak > 7 days)
├── Warning → next run in 4h
├── Failure → next run in 1h + Discord alert
└── Critical → next run in 15min + Signal alert
```

---

## 4. Architecture

### QA Test Framework

Each test follows a standard format:

```python
class QATest:
    name: str           # "augur_paper_trader_running"
    category: str       # "augur" | "openclaw" | "network" | "external"
    severity: str       # "critical" | "warning" | "info"
    check: Callable     # The actual test function
    timeout: int        # Seconds before test itself is considered failed
    
    # Returns:
    result: str         # "pass" | "warn" | "fail" | "error"
    message: str        # Human-readable status
    metrics: dict       # Optional numerical data (uptime, latency, etc.)
```

### Test Categories

**Critical Tests (must pass for operations to be healthy):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `augur_trader_running` | paper-augur systemd status | active (running) | augur |
| `augur_collector_running` | enhanced-collector systemd status | active (running) | augur |
| `augur_data_fresh` | Last row in enhanced_data.db | < 5 minutes old | augur |
| `openclaw_gateway_running` | openclaw-gateway systemd status | active (running) | openclaw |
| `disk_usage` | `df -h /` | < 90% used | infra |
| `memory_usage` | `free -m` | < 90% used | infra |

**Warning Tests (degraded but not broken):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `augur_wr_trend` | 24h win rate from paper_results.db | > 30% (warn < 25%) | augur |
| `collector_memory` | enhanced-collector RSS | < 1.8GB (of 2GB limit) | augur |
| `dashboard_responds` | HTTP GET http://giggletits:8090/health | 200 OK | infra |
| `ollama_responds` | HTTP GET http://localhost:11434/api/tags | 200 + models listed | infra |
| `discord_bot_posts` | POST test message to #system-health | 200 response | external |

**Info Tests (nice to know):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `skylight_auth` | Skylight API login | Valid token returned | external |
| `gitea_reachable` | HTTP to gitea.fleet.wood | 200 OK (or TCP connect) | network |
| `pihole_reachable` | TCP connect to .107:80 | Connection succeeds | network |
| `bliss_rpi_ping` | Ping .198 | Response in < 100ms | network |
| `gpu_temp` | nvidia-smi temperature | < 85°C | infra |

### Integration Points

**Task Board Integration:**
- QA failures automatically create tasks in relevant project
- Task title: "🔴 QA FAIL: {test_name}"
- Task pipeline: "in_progress" (needs attention)
- Recovery automatically moves task to "done"

**Discord Integration:**
- Post summaries to #system-health after each sweep
- Format: "QA Sweep YYYY-MM-DD HH:MM — X PASS | Y WARN | Z FAIL"
- Link to task board for failures

**Signal Integration:**
- Only for critical failures
- Via OpenClaw cron wake event
- Format: "🚨 QA CRITICAL: {test_name} — {message}"

---

## 5. Service Level Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| QA Sweep Success Rate | 100% scheduled runs | systemd timer logs + result JSON existence |
| Critical Test Pass Rate | > 95% | Historical analysis of critical test results |
| Warning Test Pass Rate | > 80% | Historical analysis of warning test results |
| Time to Detection | < 15 minutes | Failure timestamp vs. sweep interval |
| Time to Alert | < 2 minutes | Failure detection to Discord/Signal notification |
| False Positive Rate | < 5% | Manual validation of failed tests |

---

## 6. Tasks & Milestones

### Phase 1 — Core QA Framework
**Status:** 🟢 ACTIVE — Design complete, implementation starting

- [ ] QA-1: **Build qa-sweep.py** — Core framework with test runner, result aggregation, JSON output
- [ ] QA-2: **Implement local service tests** — systemd checks, data freshness, disk/memory
- [ ] QA-3: **Implement external service tests** — Discord, Skylight, Moltbook, gog auth
- [ ] QA-4: **Implement network tests** — .104, .107, .198 reachability (TCP/ping until SSH)
- [ ] QA-5: **Task Board API integration** — Create/update tasks on failure/recovery
- [ ] QA-6: **Discord reporting** — Post summaries to #system-health after each sweep
- [ ] QA-7: **Adaptive cadence** — Escalate to hourly on failure, relax to weekly on stability
- [ ] QA-8: **systemd timer / cron** — Schedule the sweep to run automatically

### Phase 2 — Enhanced Monitoring
**Status:** ⬜ Planned — after Phase 1

- [ ] QA-9: **Signal alerting for critical failures** — Via OpenClaw cron wake event
- [ ] QA-10: **Network tests with SSH** — Deep checks on .104/.107 once keys are deployed
- [ ] QA-11: **Historical trending** — Analyze QA results for capacity planning insights
- [ ] QA-12: **Test performance optimization** — Parallel execution, timeout tuning
- [ ] QA-13: **Custom health endpoints** — Add /health to services that don't have them
- [ ] QA-14: **Remediation automation** — Auto-restart services on common failures

---

## 7. Risks & Blockers

| ID | Risk/Blocker | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| QA-R1 | False positives create alert fatigue | High | Conservative thresholds, test validation, gradual rollout | Open |
| QA-R2 | Network tests fail due to missing SSH keys | Medium | Implement TCP-only checks first, upgrade with SSH access | Mitigated |
| QA-R3 | Test execution time too long for frequent runs | Medium | Parallel execution, timeout optimization | Open |
| QA-R4 | Discord rate limiting on frequent alerts | Medium | Batch notifications, severity-based throttling | Open |
| QA-R5 | systemd timer permissions | Medium | Run as user service, validate cron alternative | Open |
| QA-R6 | External service authentication expiry | Low | Token refresh logic, graceful auth failure handling | Open |

---

## 8. Decision Log

| Date | Decision | Rationale | Who |
|------|----------|-----------|-----|
| 2026-02-09 | QA framework as separate program from Helios core | QA is infrastructure concern, not AI improvement | Helios |
| 2026-02-09 | Adaptive cadence (daily → hourly → weekly) | Balance early detection with resource consumption | Helios |
| 2026-02-09 | Task Board integration for failure tracking | Centralized issue management, automatic remediation tracking | Helios |
| 2026-02-09 | Discord notifications for all results, Signal for critical only | Avoid Signal spam, maintain visibility | Helios |
| 2026-02-09 | Start with TCP/ping network tests before SSH | Unblocks basic connectivity monitoring while SSH keys propagate | Helios |

---

## 9. Configuration Items

| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| qa-sweep.py | Script | ~/.openclaw/workspace/scripts/ | Helios | Development |
| qa-sweep.timer | systemd Timer | ~/.config/systemd/user/ | Helios | Planned |
| qa-results/ | Directory | ~/.openclaw/workspace/data/ | Helios | Planned |
| qa-config.json | Config | ~/.openclaw/workspace/config/ | Helios | Planned |
| Discord #system-health | Channel | LBF Discord server | Helios | Live |
| LCARS Task Board | Web App | giggletits:8090 | Helios | Live |
| enhanced_data.db | Database | ~/Projects/augur-collector/ | AUGUR | Live |
| paper_results.db | Database | ~/Projects/augur-trading/ | AUGUR | Live |

---

## 10. Definition of Done

- [ ] All systems in architecture section have automated tests
- [ ] QA runs daily minimum without human intervention
- [ ] Failures create tasks on Enterprise Task Board automatically
- [ ] Recoveries close those tasks automatically
- [ ] Discord #system-health gets a summary after every sweep
- [ ] Critical failures alert via Signal
- [ ] Zero manual `systemctl status` checks needed for routine health
- [ ] QA history retained in `data/qa-results/` for trend analysis
- [ ] 15 automated tests across 4 categories implemented
- [ ] Adaptive cadence logic operational (daily/hourly/weekly)
- [ ] All critical services have < 5 minute detection time for failures

---

*Automated QA is the foundation of reliable operations. Every minute spent building these tests saves hours of manual troubleshooting later.*

*— Helios, CTO · 2026-02-09*