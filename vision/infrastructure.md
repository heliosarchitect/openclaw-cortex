# Infrastructure Rationalization — Vision Document
<!-- AI.TOC: Infrastructure Rationalization — Vision Document — Read lines 1-20 for navigation.
  §1 Table of Contents                          → lines 17-31
  §2 1. Purpose & Scope                         → lines 32-67
  §3 2. Current State                           → lines 68-117
  §4 3. Target State                            → lines 118-185
  §5 4. Architecture                            → lines 186-302
  §6 5. Service Level Targets                   → lines 303-315
  §7 6. Tasks & Milestones                      → lines 316-356
  §8 7. Risks & Blockers                        → lines 357-369
  §9 8. Decision Log                            → lines 370-382
  §10 9. Configuration Items                     → lines 383-421
  §11 10. Definition of Done                     → lines 422-441
  Total: 441 lines | Sections: 11
-->

> *Distribute workloads across available servers, eliminate single points of failure, and establish proper configuration management across the LBF fleet.*

| Field | Value |
|-------|-------|
| **Program** | Infrastructure Rationalization |
| **Parent** | LBF / Helios Operations |
| **Owner** | Helios & Matthew |
| **Status** | Active |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-10 |
| **ITIL Process** | Service Design · Service Transition |

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

Rationalize the LBF server fleet by distributing workloads appropriately, eliminating single points of failure, and implementing proper configuration management with Ansible.

### Why

Everything runs on giggletits (.163). If it goes down, we lose:
- AUGUR (trading + data collection)
- OpenClaw (Helios himself)
- The task board
- All local LLM inference
- Voice synthesis
- All monitoring

Meanwhile, .104 and .107 sit mostly idle. .104 runs Gitea and has Prometheus + Ansible installed. .107 runs Pi-hole. Neither is utilized for distributed compute, backup, or monitoring.

### Scope

- **In scope:**
  - Workload redistribution across giggletits (.163), hpserver1 (.104), woodserve1 (.107), blackview (.143)
  - Ansible fleet configuration management
  - Wazuh SIEM deployment and agent management
  - Backup strategy for critical data
  - Network monitoring and security scanning
  - SSH key deployment and access management

- **Out of scope:**
  - Hardware upgrades or procurement
  - Network topology changes (router, switches)
  - BLISS RPi modifications (resource-constrained)
  - Cloud migration or hybrid deployments

---

## 2. Current State

### Server Inventory (Updated 2026-02-09 19:55)

| Server | IP | Hostname | Role | OS | Resources | Wazuh | SSH |
|--------|-----|----------|------|-----|-----------|-------|-----|
| **giggletits** | .163 | giggletits | Primary compute | Linux Mint 22.2 | RTX 5090, 64GB RAM, NVMe | ✅ Agent 001 | ✅ Local |
| **hpserver1** | .104 | hpserver1 | Gitea, Prometheus, Traefik | Ubuntu 22.04 | Dell, 457GB disk 11% used | ✅ Agent 004 | ✅ SSH |
| **woodserve1** | .107 | woodserve1 | Pi-hole, Unbound DNS | Unknown | HP, 202d uptime | ✅ Agent 003 | ✅ SSH |
| **blackview** | .143 | blackview | Wazuh SIEM (manager+indexer+dashboard) | Linux Mint 21.3 | HP, 16GB RAM, 194GB disk 9% | ✅ Agent 000 (mgr) | ✅ SSH |
| **BLISS RPi** | .198 | bliss.fleet.wood | BLISS neural optimization | RPi OS | RPi hardware | ❌ | ⚠️ Node only |

### The Problem

```
CURRENT UTILIZATION:

giggletits (.163) — OVERLOADED
├── AUGUR trader + collector
├── OpenClaw runtime
├── Ollama LLM inference
├── XTTS voice synthesis
├── LCARS task board
├── Discord bot
└── Everything else
UTILIZATION: ~80% CPU, ~60% GPU, ~70% RAM

hpserver1 (.104) — UNDERUTILIZED
├── Gitea (active)
├── Prometheus (installed, not active)
├── Traefik (active)
└── Decommissioned: OpenProject (5 containers), Dolibarr ERP
UTILIZATION: ~10% CPU, ~15% RAM, ~11% disk

woodserve1 (.107) — UNDERUTILIZED  
├── Pi-hole (active)
├── Unbound DNS (active)
└── Legacy: AutoGPT remnants
UTILIZATION: ~5% CPU, ~20% RAM

blackview (.143) — NEW DEPLOYMENT
├── Wazuh manager + indexer + dashboard
└── Fresh deployment, version 4.8.0
UTILIZATION: ~15% CPU, ~25% RAM
```

**Single Point of Failure:** giggletits going down = total service interruption.

---

## 3. Target State

### Proposed Workload Distribution

```
giggletits (.163) — PRIMARY COMPUTE
├── AUGUR trader + collector (requires GPU)
├── OpenClaw runtime (requires GPU for embeddings)
├── Ollama LLM inference (requires GPU)
├── XTTS voice synthesis (requires GPU)
├── LCARS task board (colocated with data)
└── GPU-intensive workloads only

hpserver1 (.104) — CONFIG MANAGEMENT & MONITORING
├── Gitea (existing, keep)
├── Prometheus (activate with exporters)
├── Ansible control node → moved to giggletits
├── Grafana dashboards (pairs with Prometheus)
├── Backup target (critical data: task board DB, cortex DB, AUGUR configs)
└── CONFIGURATION & MONITORING HUB

woodserve1 (.107) — SECURITY OPERATIONS
├── Pi-hole DNS (existing, keep)
├── nmap security scanning (network sweeps)
├── Log aggregation (syslog receiver)
├── Security alerting pipeline
└── NETWORK SECURITY OPS

blackview (.143) — CENTRALIZED SIEM
├── Wazuh manager + indexer + dashboard (existing)
├── Fleet-wide log collection
├── Security event correlation
├── Compliance reporting
└── SECURITY INTELLIGENCE

bliss (.198) — UNCHANGED
├── BLISS neural optimization
├── Paired node sensor data
└── No additional roles (resource-constrained)
```

### Role Specialization

**giggletits (.163) — Primary Compute**
- All GPU workloads (AUGUR, OpenClaw, Ollama, XTTS)
- Task board (colocated with data)
- *Offload:* monitoring, security scanning, backups, config management

**hpserver1 (.104) — Config Management & Monitoring**
- Gitea (already there, keep it)
- Prometheus (already installed, activate it)
- Backup target for critical data
- Grafana dashboards

**woodserve1 (.107) — Security Operations**
- Pi-hole DNS (already there, keep it)
- nmap scanning (dedicated scanner)
- Log aggregation (syslog receiver)
- Security alerting

**blackview (.143) — SIEM Hub**
- Wazuh SIEM (already operational)
- Fleet-wide agent management
- Security event correlation
- Compliance reporting

---

## 4. Architecture

### Ansible Fleet Management

**Status:** Needs installation on giggletits (.163) as control node.

**Why giggletits as control node:** Helios (OpenClaw) orchestrates playbooks directly. All target servers already have SSH keys deployed. No SSH-hopping required.

**Installation required:**
```bash
sudo apt install -y ansible
```

**Inventory Structure:** `~/.openclaw/workspace/ansible/inventory.yml`
```yaml
all:
  children:
    compute:
      hosts:
        giggletits:
          ansible_host: 192.168.10.163
          ansible_connection: local
    monitoring:
      hosts:
        hpserver1:
          ansible_host: 192.168.10.104
    security:
      hosts:
        blackview:
          ansible_host: 192.168.10.143
    network:
      hosts:
        woodserve1:
          ansible_host: 192.168.10.107
    iot:
      hosts:
        bliss:
          ansible_host: 192.168.10.198
  vars:
    ansible_user: bonsaihorn
    ansible_ssh_common_args: '-o StrictHostKeyChecking=accept-new'
```

### Wazuh SIEM Architecture

**Status:** ✅ Operational on blackview (.143)

- **Manager:** blackview:1514 (agent communication)
- **Dashboard:** https://192.168.10.143 (admin/LBF-Wazuh-2026!)
- **API:** https://192.168.10.143:55000 (wazuh-wui/wazuh-wui)
- **Active Agents:** 4 (giggletits, hpserver1, woodserve1, blackview)

### Backup Strategy

**Critical Data Locations:**
- Task board database: `~/.openclaw/workspace/data/tasks.db`
- Cortex database: `~/.openclaw/cortex/`
- AUGUR configurations: `~/Projects/augur-trading/config/`
- OpenClaw workspace: `~/.openclaw/workspace/`

**Backup Target:** hpserver1 (.104) `/backup/` directory
**Method:** rsync via Ansible playbook
**Schedule:** Daily (via cron/systemd timer)

### Monitoring & Alerting Stack

**Philosophy:** Push-based alerting — services alert when they break, we don't discover failures during conversations.

#### Prometheus (hpserver1 .104)
- **Status:** Installed, self-scraping only — needs full activation
- **Port:** 9090
- **Scrape targets needed:**
  - `node_exporter` on all 4 servers (CPU, RAM, disk, network)
  - Custom AUGUR exporter on giggletits (service health, trade P&L, miner progress, signal count)
  - OpenClaw process metrics (uptime, session count)
  - Systemd service state (enhanced-collector, augur-live-v3, augur-continuous-miner, augur-pipeline)
- **Retention:** 15 days local storage
- **Config:** `/etc/prometheus/prometheus.yml` on .104

#### Alertmanager (hpserver1 .104)
- **Status:** Planned
- **Alert routes:**
  - **Critical** (service down, disk >90%) → Signal via OpenClaw webhook + Discord #system-health
  - **Warning** (high CPU, memory pressure) → Discord #system-health only
  - **Info** (service restart, config reload) → Discord #system-health only
- **Alert rules:**
  - `augur_service_down` — any AUGUR systemd service inactive for >60s
  - `node_disk_full` — disk usage >85% (warning), >95% (critical)
  - `node_memory_pressure` — available RAM <10%
  - `collector_stale` — no new data in enhanced_data.db for >5 min
  - `trade_loss_limit` — daily P&L exceeds -$50 threshold

#### Grafana (hpserver1 .104)
- **Status:** Planned
- **Port:** 3000
- **Data Source:** Prometheus
- **Dashboards:**
  - Fleet Overview (all server CPU/RAM/disk/network)
  - AUGUR Trading (positions, P&L, signal fire rate, maker fill rate)
  - Service Health (systemd states, uptime, restart frequency)
  - Security (Wazuh agent status, alert counts)

#### Custom AUGUR Metrics Exporter
- **Location:** giggletits, runs as systemd service
- **Port:** 9101 (Prometheus scrape target)
- **Metrics exposed:**
  - `augur_v3_positions_open` — current open positions count
  - `augur_v3_daily_pnl` — today's P&L in USD
  - `augur_v3_trades_total` — total trades today (with labels: won/lost)
  - `augur_v3_maker_fill_rate` — % of orders filling as maker
  - `augur_miner_batch_current` / `augur_miner_batch_total` — mining progress
  - `augur_miner_signals_inserted` — total signals in DB
  - `augur_pipeline_wr` — paper trader win rate
  - `augur_collector_rows_total` — enhanced_data.db row count

---

## 5. Service Level Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Fleet SSH Connectivity | 100% | Ansible ping playbook |
| Wazuh Agent Connectivity | 100% active agents | Wazuh manager API |
| Backup Completion Rate | 100% scheduled backups | rsync exit codes + log analysis |
| Prometheus Scrape Success | > 95% | Prometheus metrics |
| Single Point of Failure Elimination | 0 critical services only on giggletits | Service inventory audit |
| Configuration Drift | 0 unmanaged changes | Ansible compliance reporting |

---

## 6. Tasks & Milestones

### Phase 1 — Foundation
**Status:** 🟢 ACTIVE — SSH and Wazuh complete

- [x] IR-1: **Deploy SSH keys to .104, .107, .143** — 15 min (Matthew)
- [x] IR-2: **Assess Wazuh** — Find manager, confirm version, deploy agents
- [x] IR-6: **Configure Wazuh agents** — all hosts report to .143
- [ ] IR-3: **Deploy Prometheus on .104** — Docker container, scrape all fleet node_exporters
- [ ] IR-3a: **Deploy node_exporter fleet-wide** — giggletits, .104, .107, .143
- [ ] IR-4: **Activate Ansible** — install on giggletits, validate inventory, test connectivity

### Phase 2 — Monitoring & Configuration
**Status:** ⬜ Planned — after Phase 1

- [ ] IR-5: **Deploy node_exporter to all hosts** — via Ansible
- [ ] IR-8: **Critical data backup to .104** — task board DB, cortex DB, AUGUR configs
- [ ] IR-9: **Grafana on .104** — dashboards for Prometheus metrics
- [ ] IR-7: **Set up nmap scanning from .107** — weekly sweep, report anomalies

### Phase 3 — Security & Alerting
**Status:** ⬜ Planned — after Phase 2

- [ ] IR-10: **Security alerting pipeline** — Wazuh → Discord #system-health
- [ ] IR-11: **Fleet configuration compliance** — Ansible playbooks for standard configs
- [ ] IR-12: **Network anomaly detection** — nmap baseline + change detection
- [ ] IR-13: **Automated remediation** — Ansible playbooks for common fixes

### Ansible Playbooks to Build

| Playbook | Purpose | Priority |
|----------|---------|----------|
| `ping-all.yml` | Connectivity test for all hosts | First (validation) |
| `deploy-node-exporter.yml` | Install Prometheus node_exporter fleet-wide | High |
| `backup-critical.yml` | Rsync critical data to .104 | High |
| `security-scan.yml` | Run nmap sweep from .107, report anomalies | Medium |
| `apt-update.yml` | Fleet-wide apt update (report only) | Medium |
| `docker-cleanup.yml` | Prune unused Docker images/containers on .104 | Low |

---

## 7. Risks & Blockers

| ID | Risk/Blocker | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| IR-R1 | Ansible requires sudo on targets for package installs | High | Configure passwordless sudo for specific commands, or manual privileged operations | Open |
| IR-R2 | Wazuh version mismatch (manager 4.8.0, some components 4.14.2) | Medium | Audit all components, standardize versions | Mitigated |
| IR-R3 | Prometheus configuration loss during activation | Medium | Backup existing config before changes | Open |
| IR-R4 | SSH key rotation breaks automation | Medium | Document key management process, test recovery procedures | Open |
| IR-R5 | Network segmentation breaks inter-server communication | Medium | Firewall rule documentation, connectivity testing | Open |
| IR-R6 | Disk space on backup target (.104) insufficient | Low | Monitor usage, implement rotation policy | Open |

---

## 8. Decision Log

| Date | Decision | Rationale | Who |
|------|----------|-----------|-----|
| 2026-02-09 | SSH keys deployed to all servers first | Unblocks all other automation work | Matthew |
| 2026-02-09 | Wazuh SIEM centralized on blackview (.143) | Dedicated security appliance, adequate resources | Helios |
| 2026-02-09 | Ansible control node on giggletits, not .104 | Helios orchestrates directly, avoids SSH hopping | Helios |
| 2026-02-09 | GPU workloads remain on giggletits | Only server with adequate GPU (RTX 5090) | Helios |
| 2026-02-09 | Backup target on hpserver1 (.104) | Underutilized capacity, good connectivity | Helios |
| 2026-02-09 | Decommission OpenProject and Dolibarr on .104 | Unused for 9 months, consuming resources | Helios |

---

## 9. Configuration Items

### Servers
| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| giggletits | Server | 192.168.10.163 | Matthew | Live |
| hpserver1 | Server | 192.168.10.104 | Matthew | Live |
| woodserve1 | Server | 192.168.10.107 | Matthew | Live |
| blackview | Server | 192.168.10.143 | Matthew | Live |
| bliss.fleet.wood | Server | 192.168.10.198 | Matthew | Live |

### Services
| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| wazuh-manager | Service | blackview:1514 | Helios | Live |
| wazuh-dashboard | Service | https://192.168.10.143 | Helios | Live |
| gitea | Service | https://gitea.fleet.wood:443 | Matthew | Live |
| prometheus | Service | hpserver1:9090 | Helios | Planned |
| pi-hole | Service | http://192.168.10.107:80 | Matthew | Live |
| grafana | Service | hpserver1:3000 | Helios | Planned |

### Configuration Management
| CI Name | Type | Location | Owner | Status |
|---------|------|----------|-------|--------|
| ansible-inventory | Config | ~/.openclaw/workspace/ansible/inventory.yml | Helios | Development |
| ssh-keys | Config | ~/.ssh/ on all servers | Matthew | Live |
| wazuh-agents | Config | /var/ossec/etc/ossec.conf | Helios | Live |
| prometheus-config | Config | /etc/prometheus/prometheus.yml | Helios | Planned |

### Network Credentials
| System | Endpoint | Credentials |
|--------|----------|-------------|
| Wazuh Dashboard | https://192.168.10.143 | admin / LBF-Wazuh-2026! |
| Wazuh API | https://192.168.10.143:55000 | wazuh-wui / wazuh-wui |
| Prometheus | http://192.168.10.104:9090 | None (local network) |
| Grafana | http://192.168.10.104:3000 | admin / <to-be-set> |

---

## 10. Definition of Done

- [ ] Ansible installed on giggletits with working inventory for all servers
- [ ] All servers have SSH connectivity with deployed keys
- [ ] Wazuh SIEM operational with all servers as active agents
- [ ] Prometheus active on .104 with node_exporter on all servers
- [ ] Grafana dashboards showing fleet health metrics
- [ ] Critical data backup pipeline operational (.163 → .104 nightly)
- [ ] nmap security scanning operational from .107
- [ ] Security alerting pipeline (Wazuh → Discord) functional
- [ ] Zero services only available on giggletits (eliminate SPOF)
- [ ] Configuration compliance monitoring with Ansible
- [ ] All infrastructure changes managed through Ansible playbooks
- [ ] Backup/restore procedures tested and documented

---

*Infrastructure is only as strong as its weakest link. Distributed systems require distributed thinking.*

*— Helios, CTO · 2026-02-09*