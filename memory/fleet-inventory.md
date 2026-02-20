# LBF Homelab Fleet Inventory & Network Map

**Generated:** 2026-02-16 19:17 EST  
**Source:** Automated discovery via system inspection  
**Status:** Active Production Fleet

## Executive Summary

The LBF (Luke's Bot Farm) homelab consists of 5 physical hosts running on a single 192.168.10.0/24 subnet with centralized DNS (Pi-hole), security monitoring (Wazuh), and reverse proxy (Traefik). All hosts are hardened with SSH on port 2222 and managed via Ansible.

---

## Network Topology

### Primary Network
- **Subnet:** 192.168.10.0/24
- **Gateway:** 192.168.10.1
- **DNS:** 192.168.10.107 (woodserve1/Pi-hole)
- **DHCP:** Managed by router at 192.168.10.1

### Docker Networks (giggletits only)
- **Docker Default:** 172.17.0.0/16 (bridge: docker0)
- **Custom Bridge:** 172.18.0.0/16 (bridge: br-ed2422f76155)

---

## Fleet Hosts

### 1. giggletits (192.168.10.163) 🖥️
**Current Host** | **Role:** Compute & AI Services  
**Hardware:** x86_64, Ethernet (enp6s0), WiFi disabled  
**SSH:** bonsaihorn@192.168.10.163:2222  
**Connection:** Local (ansible_connection: local)

**Services Running:**
- **AUGUR Trading Suite:**
  - augur-continuous-miner.service (Signal Mining)
  - augur-dashboard.service (Task Board)
  - augur-pipeline.service (Paper Trading)
  - augur-regime-detector.service (LLM Detection)
  - augur-signal-tracker.service (Real-Time Validation)
  - augur-v4-executor.service (Live Trading)
  - augur-v4-scanner.service (Signal Scanner)
  - paper-augur.service (Paper Trading)
- **AI & Knowledge Systems:**
  - brain-api.service (FastAPI for brain.db)
  - cortex-embeddings.service (GPU embeddings)
  - helios-avatar.service (Display Server) - Port 8089
  - helios-monitor.service (Self-Monitoring)
  - Ollama (LLM inference) - Port 11434 (LAN only)
- **Infrastructure:**
  - openclaw-gateway.service (Ports 18789, 18792)
  - nova-wake.service (SYNAPSE listener)
  - enhanced-collector.service (Order Book Data)
  - Traefik (Docker) - Port 443 (HTTPS proxy)

**Open Ports:**
- 2222/tcp: SSH (hardened)
- 8089/tcp: Helios Avatar
- 8090/tcp: LCARS Dashboard  
- 8091/tcp: Helios WebSocket
- 9090/tcp: Service (possibly metrics)
- 11434/tcp: Ollama (LAN only)
- 443/tcp: Traefik HTTPS

---

### 2. hpserver1 (192.168.10.104) 🖥️
**Role:** Services Hub (Git, Metrics, Proxy)  
**Aliases:** gitea.fleet.wood, lbf.fleet.wood  
**SSH:** bonsaihorn@192.168.10.104:2222  
**Git SSH:** git@gitea.fleet.wood (with identity files)

**Services:**
- **Gitea** (Git server) - Port 3000 (LAN), 443 (HTTPS via Traefik)
- **Prometheus** (Metrics) - Port 9090 (LAN only)
- **Traefik** (Reverse Proxy) - Ports 80/443

**SSH Access:**
- Main: `ssh hpserver1` (port 2222)
- Git: `ssh gitea.fleet.wood` (Helios identity)
- Git: `ssh gitea-claude` (Claude identity)

---

### 3. woodserve1 (192.168.10.107) 🥧
**Role:** DNS & Network Services  
**Alias:** pi.hole  
**SSH:** bonsaihorn@192.168.10.107:2222

**Services:**
- **Pi-hole** (DNS filtering) - Port 80/443 (LAN only)
- **Unbound** (Recursive DNS resolver)
- **Wazuh Agent** (Security monitoring)

**Network Function:**
- Primary DNS server for entire fleet
- DNS filtering and ad blocking
- Local DNS resolution for .fleet.wood domains

---

### 4. bliss (192.168.10.198) 🍓
**Role:** IoT & Services  
**Dual SSH Access:** Port 22 (direct) & 2222 (hardened)  
**SSH:** bonsaihorn@192.168.10.198 or pantrypi (port 2222)

**Services:**
- **Bliss** (Media/IoT service)
- **Wazuh Agent** (Security monitoring)

**Special Configuration:**
- Supports legacy SSH algorithms (for older devices)
- KexAlgorithms: +diffie-hellman-group1-sha1
- HostKeyAlgorithms: +ssh-dss
- Ciphers: +aes256-cbc

---

### 5. blackview (192.168.10.143) 🛡️
**Role:** Security Operations Center  
**SSH:** bonsaihorn@192.168.10.143:2222

**Services:**
- **Wazuh Manager** (Central security management)
- **Wazuh Indexer** (Log indexing and storage)
- **Wazuh Dashboard** - Port 443

**Security Ports:**
- 443/tcp: Wazuh Dashboard
- 1514/tcp: Agent event collection (LAN)
- 1515/tcp: Agent enrollment (LAN)
- 55000/tcp: Wazuh API (LAN only)

---

## Traefik Routing Configuration

**Location:** `/home/bonsaihorn/Projects/traefik/config/dynamic.yml`

### Active Routes:
1. **Helios Services** (on giggletits):
   - `/ws` → http://host.docker.internal:8091 (WebSocket)
   - `/` → http://host.docker.internal:8089 (Avatar, fallback)

2. **FT-991A Ham Radio**:
   - `radio.fleet.wood` → http://radio.fleet.wood:8000
   - **Status:** Route configured, backend may be offline

### TLS Configuration:
- All routes use TLS (self-signed certificates)
- Accessible via HTTPS on port 443

---

## Service Dependencies & Data Flow

### DNS Resolution:
```
Client → woodserve1 (Pi-hole) → Unbound → Upstream DNS
```

### Security Monitoring:
```
All Hosts → blackview (Wazuh Manager) → Dashboard
```

### AI/Trading Services:
```
Data Collectors → brain.db → AUGUR Pipeline → Trading Execution
              → cortex → embeddings → Helios Avatar
```

### Code & Deployment:
```
Development → gitea (hpserver1) → Ansible → Fleet Deployment
```

---

## Fleet Management

### Ansible Control:
- **Inventory:** `/home/bonsaihorn/.ansible/inventory/hosts.yml`
- **Controller:** giggletits (local connection)
- **SSH:** All hosts use port 2222 with key-based auth
- **Privilege Escalation:** sudo on all targets

### SSH Key Management:
- **User Key:** bonsaihorn@gmail.com (Ed25519)
- **Git Keys:** Separate identity files for Helios/Claude Gitea access
- **Distribution:** Authorized keys managed via Ansible

### Security Posture:
- **SSH Hardening:** Port 2222, no root/password auth, fail2ban
- **Monitoring:** Wazuh agents on all hosts → centralized dashboard
- **Firewall:** UFW rules per host, mostly LAN-restricted services
- **Updates:** Managed via Ansible playbooks

---

## Gaps & Unknown Elements

### Network Discovery Gaps:
1. **Radio Box Status:** `radio.fleet.wood` route configured but backend status unknown
2. **Router Details:** Gateway at 192.168.10.1 not directly accessible
3. **Mobile Devices:** Android/IoT devices may exist but not inventoried
4. **Network Storage:** No NAS or shared storage detected

### Service Gaps:
1. **Monitoring:** Prometheus target configuration unknown
2. **Backups:** Backup strategy and storage not documented
3. **Certificate Management:** Self-signed cert generation/renewal process
4. **Log Aggregation:** Besides Wazuh, no centralized logging visible

### Documentation Gaps:
1. **Hardware Specs:** CPU, RAM, storage per host unknown
2. **Service Versions:** Specific versions of services not captured
3. **Performance Baselines:** No performance metrics documented
4. **Disaster Recovery:** Recovery procedures not documented

---

## Network Map

```
Internet
    |
192.168.10.1 (Gateway/Router)
    |
192.168.10.0/24 LAN
    |
    ├── 192.168.10.107 - woodserve1 (Pi-hole DNS)
    ├── 192.168.10.104 - hpserver1 (Gitea, Services)
    ├── 192.168.10.143 - blackview (Wazuh Security)
    ├── 192.168.10.163 - giggletits (AI/Trading, Current Host)
    ├── 192.168.10.198 - bliss (IoT)
    └── radio.fleet.wood - Ham Radio (IP TBD)

Docker Networks (giggletits only):
├── 172.17.0.0/16 (docker0)
└── 172.18.0.0/16 (br-ed2422f76155)
    └── Traefik Container
```

---

## Quick Access Commands

```bash
# SSH to hosts
ssh giggletits          # local (current host)
ssh hpserver1           # 192.168.10.104:2222
ssh woodserve1          # 192.168.10.107:2222  
ssh bliss               # 192.168.10.198:2222
ssh blackview           # 192.168.10.143:2222
ssh pantrypi            # 192.168.10.198:2222 (legacy access)

# Git access
ssh gitea.fleet.wood    # Helios account
ssh gitea-claude        # Claude account

# Service URLs
https://gitea.fleet.wood/           # Gitea (via Traefik)
https://192.168.10.143/             # Wazuh Dashboard
http://192.168.10.107/              # Pi-hole Admin
https://radio.fleet.wood/           # Ham Radio (if online)

# Ansible management
cd ~/.ansible
ansible-playbook playbooks/site.yml  # Deploy to all hosts
ansible all -m ping                   # Test connectivity
```

---

*This document serves as the authoritative reference for the LBF homelab fleet. Update via Ansible inventory changes and re-run discovery as needed.*