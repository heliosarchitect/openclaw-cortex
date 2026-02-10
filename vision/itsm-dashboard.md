# ITSM/SLA Dashboard — Vision Document

> *A single LCARS-themed page showing fleet health, SLA compliance, and service status. Replaces the need for external ITSM tools.*

| Field | Value |
|-------|-------|
| **Program** | ITSM/SLA Dashboard |
| **Parent** | LBF / Helios Operations |
| **Owner** | Helios |
| **Status** | Planned |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-09 |
| **ITIL Process** | Service Operation · Service Reporting |

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

A single LCARS-themed page at `http://giggletits:8090/itsm` showing fleet health, SLA compliance, and service status. Centralizes operational visibility without external ITSM tool dependencies.

### Why

Currently, there's no unified view of:
- Service availability and performance
- SLA compliance across all services
- Security alert summaries
- Infrastructure health trends
- Fleet-wide status at a glance

ITIL best practices require service reporting and performance monitoring. Rather than deploy a complex external ITSM tool like iTop, build a focused dashboard that integrates with our existing QA sweep framework and monitoring infrastructure.

### Scope

- **In scope:**
  - Fleet status overview (all servers)
  - SLA compliance calculation and reporting (30-day rolling)
  - Recent QA sweep results integration
  - Wazuh security alert summaries (24h)
  - Device inventory display (static + dynamic)
  - LCARS UI theme consistency with existing dashboard

- **Out of scope:**
  - Incident management workflows (manual processes)
  - Change management tracking (use task board)
  - Configuration management database (use Ansible inventory)
  - Service catalog or request fulfillment
  - Complex reporting or business intelligence

---

## 2. Current State

No centralized ITSM dashboard exists. Operational visibility requires:

| Information Need | Current Method | Problems |
|-----------------|----------------|----------|
| Service Health | Manual `systemctl status` checks | Time-consuming, reactive only |
| Fleet Status | SSH to each server individually | No single pane of glass |
| SLA Compliance | Not measured | No historical data or accountability |
| Security Alerts | Manual Wazuh dashboard checks | Isolated from operational context |
| Infrastructure Trends | Not tracked | No capacity planning data |
| Device Inventory | Mental model + scattered notes | Incomplete, outdated |

**Result:** Operational blindness. No proactive management. Issues discovered when users complain or services fail visibly.

---

## 3. Target State

### Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  LBF ENTERPRISE — INFRASTRUCTURE STATUS           [LCARS]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FLEET STATUS                    SLA COMPLIANCE (30 DAY)    │
│  ┌──────────┬────────┐          ┌──────────────────────┐    │
│  │ giggletits│ ● UP  │          │ AUGUR trader   99.2% │    │
│  │ hpserver1 │ ● UP  │          │ OpenClaw       99.8% │    │
│  │ woodserve1│ ● UP  │          │ Data collector 98.5% │    │
│  │ blackview │ ● UP  │          │ Gitea          99.9% │    │
│  │ bliss RPi │ ● UP  │          │ Pi-hole        99.9% │    │
│  └──────────┴────────┘          │ Wazuh          99.7% │    │
│                                  └──────────────────────┘    │
│  RECENT QA SWEEP                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 2026-02-09 19:51 — 14 PASS | 1 WARN | 0 FAIL       │   │
│  │ ⚠ collector_memory: RSS 245MB (threshold 200MB)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  WAZUH SECURITY ALERTS (24H)     DEVICE INVENTORY          │
│  ┌────────────────────────┐     ┌────────────────────────┐  │
│  │ 0 Critical             │     │ 5 Servers              │  │
│  │ 2 High                 │     │ 6 Network devices      │  │
│  │ 12 Medium              │     │ 7 IoT/Smart home       │  │
│  │ 45 Low                 │     │ 30+ Total on subnet    │  │
│  └────────────────────────┘     └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

**Fleet Status Section:**
- Real-time server status (UP/DOWN/DEGRADED)
- Color-coded indicators (green/yellow/red)
- Data source: Wazuh agent status + QA sweep results

**SLA Compliance Section:**
- Per-service uptime percentage (30-day rolling window)
- Color-coded by threshold: green ≥99%, yellow ≥95%, red <95%
- Data source: QA sweep historical results

**Recent QA Sweep Section:**
- Latest sweep timestamp and summary (X PASS | Y WARN | Z FAIL)
- Details for any warnings or failures
- Link to full QA results

**Wazuh Security Alerts Section:**
- 24-hour alert counts by severity level
- Data source: Wazuh API alert aggregation

**Device Inventory Section:**
- Static count of managed devices
- Dynamic discovery from nmap scans (future)
- Links to detailed inventory

---

## 4. Architecture

### Data Sources Integration

| Data Source | Endpoint | Information Provided | Update Frequency |
|-------------|----------|---------------------|------------------|
| **QA Sweep JSON** | `data/qa-results/` | Per-service pass/fail/warn, timestamps | Per sweep (daily/hourly) |
| **Wazuh API** | blackview:55000 | Agent status, security alerts, fleet health | Real-time (API query) |
| **Prometheus** | .104:9090 | Time-series metrics (CPU, RAM, disk, network) | 15s scrape interval |
| **systemd status** | local | Service health for AUGUR, OpenClaw, etc. | On-demand |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/itsm` | GET | LCARS HTML page |
| `/api/itsm/status` | GET | JSON: fleet status + SLA + alerts |
| `/api/itsm/sla?days=30` | GET | JSON: per-service uptime percentages |
| `/api/itsm/wazuh` | GET | JSON: Wazuh alert summary (proxied from .143) |
| `/api/itsm/inventory` | GET | JSON: device inventory (static + dynamic) |

### SLA Calculation Logic

```python
# Simple uptime percentage from QA sweep history
uptime_pct = (passing_sweeps / total_sweeps) * 100

# Per-service, rolling 30-day window
# Source: data/qa-results/*.json → filter by test name → count pass/total
# Display: color-coded (green ≥ 99%, yellow ≥ 95%, red < 95%)
```

### Integration with Existing Systems

**LCARS Dashboard:** Extends existing FastAPI app at giggletits:8090
- No new dependencies required
- Uses existing authentication (admin/4KXPu6XH8BbmLcG0AcQOoA)
- Consistent LCARS theme and styling

**QA Framework:** Consumes QA sweep JSON results
- Historical analysis for SLA calculations
- Real-time status from latest sweep
- Failure details for troubleshooting

**Wazuh SIEM:** Proxies API calls to blackview:55000
- Security alert aggregation and summarization
- Agent status for fleet health
- Authentication: wazuh-wui/wazuh-wui

---

## 5. Service Level Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Dashboard Availability | 99.5% | HTTP health checks via QA sweep |
| Data Freshness | < 5 minutes | Timestamp comparison of latest data sources |
| Page Load Time | < 2 seconds | Client-side performance monitoring |
| SLA Calculation Accuracy | 100% | Audit against raw QA sweep data |
| Wazuh API Response Time | < 1 second | API call latency measurement |
| Auto-refresh Reliability | 99% success | Browser-side refresh error tracking |

---

## 6. Tasks & Milestones

### Phase 1 — Core Dashboard
**Status:** 🔲 PLANNED

- [ ] ITSM-1: **SLA calculation engine** — Parse QA result history, compute per-service uptime %
- [ ] ITSM-2: **Fleet status API** — Query Wazuh for agent status, merge with QA data
- [ ] ITSM-3: **LCARS /itsm page** — HTML/CSS matching existing dashboard theme
- [ ] ITSM-4: **Wazuh alert proxy** — Fetch and summarize 24h alerts from .143 API

### Phase 2 — Enhanced Features
**Status:** ⬜ Planned — after Phase 1

- [ ] ITSM-5: **Device inventory section** — Static + dynamic (nmap) device list
- [ ] ITSM-6: **Historical trending charts** — SLA trends over time
- [ ] ITSM-7: **Drill-down capabilities** — Click service for detailed history
- [ ] ITSM-8: **Alert threshold configuration** — Configurable SLA targets per service

### Phase 3 — Advanced Analytics
**Status:** ⬜ Future — after operational stability

- [ ] ITSM-9: **Capacity planning indicators** — Resource utilization trends
- [ ] ITSM-10: **Incident correlation** — Link QA failures to security events
- [ ] ITSM-11: **Performance benchmarking** — Service response time tracking
- [ ] ITSM-12: **Automated reporting** — Weekly/monthly SLA reports

---

## 7. Risks & Blockers

| ID | Risk/Blocker | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| ITSM-R1 | Wazuh API authentication expiry | Medium | Implement token refresh logic, fallback graceful degradation | Open |
| ITSM-R2 | QA sweep history insufficient for accurate SLA | High | Requires 30+ days of QA data, start with available data | Open |
| ITSM-R3 | Performance issues with real-time data refresh | Medium | Implement caching, optimize API calls, async loading | Open |
| ITSM-R4 | LCARS theme complexity increases development time | Low | Use existing components, progressive enhancement | Open |
| ITSM-R5 | Dependency on external systems (Wazuh, Prometheus) | Medium | Graceful degradation when services unavailable | Open |

---

## 8. Decision Log

| Date | Decision | Rationale | Who |
|------|----------|-----------|-----|
| 2026-02-09 | Build into existing LCARS dashboard vs. standalone app | Leverage existing authentication, theme, and deployment | Helios |
| 2026-02-09 | 30-day rolling window for SLA calculations | Standard ITIL practice, balances recency with statistical significance | Helios |
| 2026-02-09 | Proxy Wazuh API instead of direct dashboard embedding | Better security, consistent UI experience, error handling | Helios |
| 2026-02-09 | Focus on operational metrics, not business intelligence | Align with operator needs, avoid scope creep | Helios |
| 2026-02-09 | Auto-refresh every 60 seconds | Balance freshness with system load | Helios |

---

## 9. Configuration Items

### Dashboard Components
| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| itsm-dashboard | Web Page | giggletits:8090/itsm | Helios | Development |
| sla-engine | Module | LCARS app/modules/sla.py | Helios | Development |
| wazuh-proxy | Module | LCARS app/modules/wazuh.py | Helios | Development |
| itsm-api | API Routes | LCARS app/api/itsm.py | Helios | Development |

### Data Sources
| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| qa-results | Directory | ~/.openclaw/workspace/data/qa-results/ | QA Framework | Live |
| wazuh-api | Service | https://192.168.10.143:55000 | Wazuh | Live |
| prometheus | Service | http://192.168.10.104:9090 | Infrastructure | Planned |
| lcars-app | Web App | giggletits:8090 | Helios | Live |

### Authentication & Access
| System | Endpoint | Credentials | Notes |
|--------|----------|-------------|-------|
| LCARS Dashboard | http://giggletits:8090 | admin / 4KXPu6XH8BbmLcG0AcQOoA | Existing auth |
| Wazuh API | https://192.168.10.143:55000 | wazuh-wui / wazuh-wui | Needs hardening |
| Prometheus | http://192.168.10.104:9090 | None | Local network only |

---

## 10. Definition of Done

- [ ] `/itsm` page renders in LCARS theme with live data
- [ ] SLA percentages calculated from QA sweep history (30-day rolling)
- [ ] Wazuh agent status displayed (active/disconnected/never connected)
- [ ] Wazuh security alert summary (24h, by severity)
- [ ] Fleet status showing all 5 servers with real-time UP/DOWN status
- [ ] Recent QA sweep results with PASS/WARN/FAIL counts
- [ ] Device inventory section with server count and network device estimates
- [ ] Auto-refresh every 60 seconds without user intervention
- [ ] No new dependencies beyond existing FastAPI application
- [ ] Error handling for unavailable data sources (graceful degradation)
- [ ] Page load time under 2 seconds on local network
- [ ] Mobile-responsive design for tablet viewing

---

*Good operations require good visibility. This dashboard provides the single pane of glass that transforms reactive firefighting into proactive service management.*

*— Helios, CTO · 2026-02-09*