# Bottleneck Tracking + Tool→Infrastructure Graduation
<!-- AI.TOC: Bottleneck Tracking + Tool→Infrastructure Graduation — Read lines 1-20 for navigation.
  §1 1. Problem                                 → lines 15-34
  §2 2. Solution                                → lines 35-79
  §3 3. Tool → Infrastructure Graduation Crit   → lines 80-90
  §4 4. Current Inventory                       → lines 91-119
  §5 5. Implementation Tasks                    → lines 120-129
  §6 6. Decision Log                            → lines 130-141
  Total: 141 lines | Sections: 6
-->

> *Make invisible dependencies visible. Turn fragile tools into managed infrastructure.*

| Field | Value |
|-------|-------|
| **Program** | LBF Enterprise Dashboard |
| **Owner** | Helios (CTO) |
| **Status** | Spec Complete |
| **Created** | 2026-02-10 |
| **ITIL Process** | Capacity Management / Service Transition |

---

## 1. Problem

Every program has hidden bottlenecks — single points of failure, manual dependencies, unmanaged tools that the whole system relies on. Right now these are invisible:

- **Signal-cli** runs as a gateway dependency but has no health monitoring
- **SQLite databases** (tasks.db, paper_results.db, enhanced_data.db) have no backup strategy  
- **gog** (Google Workspace CLI) is a binary with no version management
- **Ollama** runs as systemd but has no automated recovery beyond restart
- **Skylight API** is reverse-engineered with no official support — could break any time

These are "tools" pretending to be "infrastructure." The distinction matters:

| | Tool | Infrastructure |
|---|------|---------------|
| **Monitoring** | None | Health checked, alerting |
| **Backup** | None | Automated, tested restores |
| **Recovery** | Manual restart | Auto-restart, failover |
| **Versioning** | Whatever's installed | Pinned, tested upgrades |
| **Documentation** | Tribal knowledge | Runbooks, config-as-code |

## 2. Solution

### 2.1 Bottleneck Tags on Projects

Add a `bottlenecks` JSON column to the `projects` table:

```sql
ALTER TABLE projects ADD COLUMN bottlenecks TEXT DEFAULT '[]';
```

Each bottleneck is:
```json
{
  "name": "signal-cli",
  "type": "tool|infrastructure",
  "severity": "low|medium|high|critical",
  "description": "Single gateway dependency, no failover",
  "graduation_path": "Add health check, pin version, document recovery",
  "graduated": false
}
```

### 2.2 Program Page Enhancement

Each program page shows:
- **Bottleneck count** badge (red if critical, yellow if high)
- **Bottleneck list** with severity, type, and graduation status
- **Graduation progress** — percentage of tools→infrastructure

### 2.3 Enterprise Cross-Cut View

New `/bottlenecks` page showing:
- All bottlenecks across all programs
- Filter by severity, type, graduation status
- Dependency graph (which programs share which tools)
- Risk heat map

### 2.4 Auto-Detection (Phase 2)

Scan for common bottleneck patterns:
- Services without health checks
- Databases without backup cron entries
- Binaries without version pinning
- Single points of failure (one server, one process)

## 3. Tool → Infrastructure Graduation Criteria

A tool "graduates" to infrastructure when it meets ALL:

- [ ] **Monitored** — Health check runs at least every 5 min
- [ ] **Alerting** — Failure triggers notification to Helios
- [ ] **Backed up** — Data protected, restore tested
- [ ] **Versioned** — Specific version pinned, upgrade path documented
- [ ] **Recoverable** — Auto-restart configured, recovery runbook exists
- [ ] **Documented** — Config, dependencies, and troubleshooting in docs

## 4. Current Inventory

### Critical (single point of failure, no monitoring)

| Tool | Used By | Graduation Priority |
|------|---------|-------------------|
| signal-cli | OpenClaw gateway | P1 — primary communication channel |
| SQLite DBs | AUGUR, Dashboard, Cortex | P1 — all state is here |
| enhanced_data.db (16GB) | AUGUR collector | P1 — irreplaceable data |
| Skylight API | Family coordination | P2 — reverse-engineered, fragile |

### High (managed but incomplete)

| Tool | Used By | Missing |
|------|---------|---------|
| Ollama | LLM Fleet | Backup of Modelfiles, version pinning |
| Gitea | All repos | Backup strategy, redundancy |
| Pi-hole | DNS for fleet | No failover DNS server |
| Wazuh | Security | Dashboard password needs reset, agents incomplete |

### Graduated (fully managed)

| Infrastructure | Used By | Status |
|----------------|---------|--------|
| OpenClaw gateway | Everything | systemd, auto-restart, health checked |
| paper-augur | AUGUR trading | systemd, auto-restart, flock lock |
| enhanced-collector | AUGUR data | systemd, MemoryMax, auto-restart |
| augur-dashboard | Enterprise UI | systemd, Restart=always, reverse proxy |

## 5. Implementation Tasks

- [ ] BTN-1: Add `bottlenecks` column to projects table (migration script)
- [ ] BTN-2: Build bottleneck CRUD in app.py (add/edit/remove/graduate)
- [ ] BTN-3: Add bottleneck section to program page template
- [ ] BTN-4: Build `/bottlenecks` cross-cut view
- [ ] BTN-5: Populate initial bottleneck data from inventory above
- [ ] BTN-6: Add graduation checklist UI (checkbox per criterion)
- [ ] BTN-7: Auto-detection scanner (Phase 2)

## 6. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | JSON column for bottlenecks | Flexible schema, no migration headaches for adding fields |
| 2026-02-10 | 6-criterion graduation checklist | Covers ITIL service transition basics without over-engineering |
| 2026-02-10 | Manual tagging first, auto-detect later | Get value immediately, automate when patterns are clear |

---

*This spec defines the "what." Engineering tasks (BTN-1 through BTN-7) define the "how."*
