# LBF Infrastructure Security — Vision Document
<!-- AI.TOC: LBF Infrastructure Security — Vision Document — Read lines 1-20 for navigation.
  §1 Table of Contents                          → lines 17-31
  §2 1. Purpose & Scope                         → lines 32-53
  §3 2. Current State                           → lines 54-112
  §4 3. Target State                            → lines 113-126
  §5 4. Architecture                            → lines 127-172
  §6 5. Service Level Targets                   → lines 173-186
  §7 6. Tasks & Milestones                      → lines 187-216
  §8 7. Risks & Blockers                        → lines 217-228
  §9 8. Decision Log                            → lines 229-239
  §10 9. Configuration Items                     → lines 240-256
  §11 10. Definition of Done                     → lines 257-272
  Total: 272 lines | Sections: 11
-->

> *Fleet-wide security hardening, monitoring, and compliance for all LBF servers.*

| Field | Value |
|-------|-------|
| **Program** | Infrastructure Security & Compliance |
| **Parent** | LBF / Helios Operations |
| **Owner** | Helios (CTO) / Matthew (Founder) |
| **Status** | Active |
| **Created** | 2026-02-09 |
| **Last Updated** | 2026-02-09 |
| **ITIL Process** | Information Security Management / Service Operation |

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
Establish baseline security hardening, continuous vulnerability monitoring, and compliance enforcement across all LBF network servers. Managed by Ansible for consistency and auditability. Monitored by Wazuh SIEM for real-time threat detection.

### Why
Current state assessment (2026-02-09) reveals **zero hardening** across the fleet:
- All SSH configs are default (root login, password auth, no timeouts)
- No audit logging on any server
- No firewall rules on any server
- No intrusion prevention (fail2ban) anywhere
- No password policy enforcement
- Wazuh SCA scores: 12-42% compliance

This is a home lab, but it runs production services (Gitea, Pi-hole DNS, AUGUR trading, OpenClaw). One compromised node gives lateral access to everything.

### Scope
- **In scope:** giggletits (.163), hpserver1 (.104), woodserve1 (.107), blackview (.143)
- **Out of scope:** IoT devices, printers, WiFi repeaters, BLISS RPi (.198)

---

## 2. Current State

*Vulnerability assessment performed 2026-02-09 20:35 EST via Wazuh SCA + manual scan.*

### 2.1 Fleet Security Posture

| Server | IP | OS | Wazuh Agent | SCA Score | auditd | ufw | fail2ban | auto-updates |
|--------|----|----|-------------|-----------|--------|-----|----------|-------------|
| giggletits | .163 | Mint 22.2 | ✅ 001 active | 12.5% (2/16) | ❌ inactive | ❌ unknown | ❌ inactive | ❌ not installed |
| hpserver1 | .104 | Ubuntu 22.04 | ✅ 004 active | 41.7% (75/180) | ❌ inactive | ❌ unknown | ❌ inactive | ✅ installed |
| woodserve1 | .107 | Ubuntu 22.04 | ✅ 003 active | 42.7% (76/178) | ❌ inactive | ❌ unknown | ❌ inactive | ✅ installed |
| blackview | .143 | Mint 21.3 | ✅ 000 active | 12.5% (2/16) | ❌ inactive | ❌ unknown | ❌ inactive | ❌ not installed |

### 2.2 SSH Configuration (all servers identical)

| Setting | Current | Required |
|---------|---------|----------|
| Port | 22 (default) | Non-standard (e.g., 2222) |
| PermitRootLogin | yes (default) | no |
| PasswordAuthentication | yes (default) | no |
| PubkeyAuthentication | yes (default) | yes (explicit) |
| MaxAuthTries | 6 (default) | 4 |
| LoginGraceTime | 120s (default) | 60s |
| X11Forwarding | yes (explicit) | no |
| AllowTcpForwarding | yes (default) | no |
| ClientAliveInterval | 0 (default) | 300 |
| ClientAliveCountMax | 3 (default) | 3 |
| PermitEmptyPasswords | yes (default) | no |
| Banner | none | /etc/issue.net |

### 2.3 Exposed Services (nmap)

| Server | Open Ports | Services |
|--------|-----------|----------|
| hpserver1 (.104) | 22, 80, 443 | SSH, Traefik HTTP/S (Gitea behind reverse proxy) |
| woodserve1 (.107) | 22, 53, 80, 443 | SSH, Pi-hole DNS, Pi-hole web |
| blackview (.143) | 22, 443, 1514, 1515, 55000 | SSH, Wazuh dashboard, agent enrollment, API |
| giggletits (.163) | 22, 8090, 11434, + many | SSH, LCARS dashboard, Ollama, AUGUR services |

### 2.4 Critical Findings

| ID | Finding | Severity | Affected | Status |
|----|---------|----------|----------|--------|
| SEC-1 | SSH allows root login | 🔴 Critical | All 4 servers | Open |
| SEC-2 | SSH allows password authentication | 🔴 Critical | All 4 servers | Open |
| SEC-3 | No audit logging (auditd) | 🔴 Critical | All 4 servers | Open |
| SEC-4 | No host firewall | 🔴 Critical | All 4 servers | Open |
| SEC-5 | No intrusion prevention (fail2ban) | 🟡 High | All 4 servers | Open |
| SEC-6 | No password policy | 🟡 High | All 4 servers | Open |
| SEC-7 | X11 forwarding enabled | 🟡 Medium | All 4 servers | Open |
| SEC-8 | No SSH access restrictions (AllowUsers) | 🟡 Medium | All 4 servers | Open |
| SEC-9 | CUPS running unnecessarily | 🟢 Low | giggletits | Open |
| SEC-10 | No SSH banner | 🟢 Low | All 4 servers | Open |
| SEC-11 | Wazuh API using default credentials | 🔴 Critical | blackview | Open |
| SEC-12 | Stale Wazuh agent 002 (disconnected) | 🟢 Low | blackview | Open |
| SEC-13 | No automatic security updates | 🟡 High | giggletits, blackview | Open |

---

## 3. Target State

All servers reach **CIS Level 1 compliance** (adapted for home lab):
- SSH key-only auth, no root login, hardened timeouts
- Host firewalls with default-deny, explicit allow rules per server role
- auditd logging all privileged operations
- fail2ban protecting SSH
- Unattended security updates on all servers
- Wazuh SCA scores > 80%
- All findings from §2.4 resolved to Closed or Accepted Risk
- Ansible enforces configuration drift detection — any manual change triggers alert

---

## 4. Architecture

### 4.1 Components

```
┌─────────────────────────────────────────────────┐
│                ANSIBLE CONTROLLER                │
│           giggletits (192.168.10.163)            │
│                                                  │
│  ~/.ansible/                                     │
│  ├── inventory/hosts.yml                         │
│  ├── playbooks/                                  │
│  │   ├── hardening.yml      (SSH, users, sudo)   │
│  │   ├── firewall.yml       (ufw per-role)       │
│  │   ├── audit.yml          (auditd rules)       │
│  │   ├── monitoring.yml     (fail2ban, updates)   │
│  │   └── site.yml           (runs all)           │
│  ├── roles/                                      │
│  │   ├── common/            (baseline all hosts)  │
│  │   ├── wazuh-manager/     (blackview only)      │
│  │   ├── gitea-server/      (hpserver1 only)      │
│  │   └── dns-server/        (woodserve1 only)     │
│  └── group_vars/                                  │
│      ├── all.yml            (fleet-wide settings)  │
│      └── servers.yml        (server-specific)      │
└───────────────┬─────────────────────────────────┘
                │ SSH (key-based)
    ┌───────────┼───────────┬───────────┐
    ▼           ▼           ▼           ▼
 .104        .107        .143        .163
hpserver1  woodserve1  blackview  giggletits
 (Gitea)   (Pi-hole)   (Wazuh)   (Compute)
```

### 4.2 Dependencies
- Ansible installed on giggletits
- SSH key-based access to all servers (✅ already working)
- sudo access on remote hosts (⚠️ needs `NOPASSWD` for ansible user, or Matthew runs with `-K`)

### 4.3 Integration Points
- **Wazuh**: Monitors compliance post-hardening, SCA re-scans validate Ansible changes
- **LCARS Dashboard**: ITSM page shows fleet status, SCA scores, security findings
- **Discord #system-health**: Critical security events auto-posted via wazuh-alerts.py

---

## 5. Service Level Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| SCA Compliance Score | > 80% all servers | Wazuh SCA scan (daily) |
| SSH Hardening | 100% CIS checks pass | Wazuh SCA unix_audit |
| Firewall Coverage | 100% servers with default-deny | Ansible fact check |
| Audit Coverage | 100% servers with auditd active | Wazuh agent monitoring |
| Patch Latency | < 48h for critical CVEs | unattended-upgrades + Wazuh vuln detector |
| Configuration Drift | 0 unauthorized changes/week | Ansible `--check` mode runs |
| Mean Time to Remediate (MTTR) | < 4h critical, < 24h high | Incident log |

---

## 6. Tasks & Milestones

### Phase 1 — Immediate Hardening (Week 1)
- [ ] Install Ansible on giggletits
- [ ] Create Ansible inventory (`~/.ansible/inventory/hosts.yml`)
- [ ] **SEC-1/SEC-2**: SSH hardening playbook (key-only, no root, timeouts)
- [ ] **SEC-3**: Install and configure auditd on all servers
- [ ] **SEC-4**: Configure ufw with per-server rules
- [ ] **SEC-5**: Install and configure fail2ban (SSH jail)
- [ ] **SEC-11**: Change Wazuh API password from default
- [ ] **SEC-13**: Enable unattended-upgrades on giggletits + blackview
- [ ] Run Wazuh SCA re-scan to validate improvements

### Phase 2 — Policy & Monitoring (Week 2)
- [ ] **SEC-6**: Implement password policy (PAM configuration)
- [ ] **SEC-7/SEC-8**: SSH AllowUsers + disable X11/TCP forwarding
- [ ] **SEC-10**: Deploy SSH warning banner
- [ ] **SEC-12**: Remove stale Wazuh agent 002
- [ ] Configure Wazuh vulnerability detector module
- [ ] Create Ansible drift-detection cron (weekly `--check` run)
- [ ] Wire drift alerts to Discord #system-health

### Phase 3 — Continuous Compliance (Ongoing)
- [ ] Monthly SCA review
- [ ] Quarterly Ansible playbook audit
- [ ] Annual password rotation enforcement
- [ ] Update hardening baseline when CIS benchmarks update

---

## 7. Risks & Blockers

| ID | Risk/Blocker | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| R-1 | No sudo access from Helios | High | Matthew runs playbooks with `-K`, or configures NOPASSWD for ansible tasks | Open |
| R-2 | SSH port change could lock out access | High | Test on one server first; keep console access path documented | Open |
| R-3 | Firewall rules could break services | High | Whitelist all known services before enabling default-deny | Open |
| R-4 | Ansible not installed on controller | Medium | `sudo apt install ansible` on giggletits | Open |
| R-5 | bonsaihorn not in docker group on .107 | Low | `sudo usermod -aG docker bonsaihorn` | Open |

---

## 8. Decision Log

| Date | Decision | Rationale | Who |
|------|----------|-----------|-----|
| 2026-02-09 | Use Ansible over per-server scripts | Fleet consistency, auditability, drift detection, ITIL alignment | Matthew/Helios |
| 2026-02-09 | Run Ansible from giggletits, not .104 | Controller should be on primary compute; .104 is a target, not controller | Helios |
| 2026-02-09 | Start with SSH hardening before firewall | SSH is network-facing attack surface; firewall is defense-in-depth | Helios |
| 2026-02-09 | Defer SSH port change to Phase 2 | Risk of lockout; harden auth first, then move port | Helios |

---

## 9. Configuration Items

| CI Name | Type | Location | Owner | Role | Status |
|---------|------|----------|-------|------|--------|
| giggletits | Server | 192.168.10.163 | Matthew | Compute + Ansible Controller | Live |
| hpserver1 | Server | 192.168.10.104 | Matthew | Gitea / Prometheus / Traefik | Live |
| woodserve1 | Server | 192.168.10.107 | Matthew | Pi-hole DNS / Unbound | Live |
| blackview | Server | 192.168.10.143 | Matthew | Wazuh Manager / Indexer / Dashboard | Live |
| Wazuh Manager | Application | 192.168.10.143 | Helios | SIEM Manager | Live |
| Wazuh Dashboard | Application | https://192.168.10.143 | Helios | SIEM UI | Live |
| Ansible | Tool | giggletits:~/.ansible/ | Helios | Configuration Management | Planned |
| fail2ban | Service | All servers | Helios | Intrusion Prevention | Planned |
| auditd | Service | All servers | Helios | Audit Logging | Planned |
| ufw | Service | All servers | Helios | Host Firewall | Planned |

---

## 10. Definition of Done

- [x] Security assessment completed with findings documented
- [ ] All 🔴 Critical findings (SEC-1 through SEC-4, SEC-11) remediated
- [ ] All 🟡 High findings (SEC-5, SEC-6, SEC-13) remediated
- [ ] Wazuh SCA scores > 80% on all servers
- [ ] Ansible playbooks in version control (Gitea)
- [ ] Weekly drift detection running
- [ ] Security alerts flowing to Discord #system-health
- [ ] Document reviewed and accepted by Matthew (the "seasoned IT security professional" test)

---

*Template version: 1.0 — Based on ITIL 4 Information Security Management*
*LBF standard. Managed by Helios, reviewed by Matthew.*
