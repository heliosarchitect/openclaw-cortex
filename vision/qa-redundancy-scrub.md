# QA Vision: Weekly Redundancy Scrub
<!-- AI.TOC: QA Vision: Weekly Redundancy Scrub — Read lines 1-20 for navigation.
  §1 Purpose                                    → lines 5-7
  §2 Scope                                      → lines 8-101
  §3 Weekly Scrub Procedure                     → lines 102-116
  §4 Immediate Actions (Tonight)                → lines 117-122
  Total: 122 lines | Sections: 4
-->

**Author:** Helios | **Created:** 2026-02-10 | **Status:** Active

## Purpose
Weekly automated audit of all LBF infrastructure for redundancy, waste, and drift. Ensures nothing is duplicated, stale, or consuming resources unnecessarily.

## Scope

### 1. Cron Jobs (OpenClaw)
**What to check:**
- Disabled jobs that will never run again (one-shot `at` jobs in the past)
- Duplicate jobs doing the same thing (e.g., two email checkers)
- Jobs referencing dead paths/scripts
- Jobs with `lastError` that were never fixed
- Overlapping schedules (e.g., 15-min and 30-min jobs checking the same thing)

**Current state (2026-02-10):**
- 37 total cron jobs
- ~15 are disabled one-shot timers (potatoes, strategy searches, bot checkpoints) → DELETE
- 2 duplicate email checkers (id `42f67d96` disabled + `9ebae22f` enabled) → KEEP 1
- `twilio-email-watch` can merge into main email check → MERGE
- `trading-monitor`, `Trading Bot Active Management`, `Trading Bot v2 Build Checkpoint` are all disabled relics of Chad bot era → DELETE
- `CPU Temperature Monitor`, `Strategy Search Monitor`, `Order Book Collector Health` are disabled polling-era relics → DELETE per HEARTBEAT.md philosophy
- `Moltbook Stats` x2 (top/bottom of hour) — disabled, redundant with Moltbook engagement cron → DELETE
- `deep-think` (hourly) overlaps with `Proactive Work Rotation` (15-min) → CONSOLIDATE

**Redundancy map:**
| Function | Active Jobs | Redundant Jobs |
|----------|------------|----------------|
| Email monitoring | `Email Check` (enabled) | `Email Check` (disabled dup), `twilio-email-watch` |
| Trading hours | `Trading Day Start/End` | 5+ disabled trading monitors |
| Moltbook | `Moltbook engagement` (isolated) | 2x disabled stats checkers, morning report |
| Productivity | `Proactive Work`, `night-shift`, `deep-think` | Overlapping scopes |
| Maintenance | `Cortex Nightly`, `Cortex Weekly`, `helios-nightly-backup` | Clean — no redundancy |
| Data | `data_retention_nightly` (disabled, refs dead path) | Needs update or removal |

### 2. Systemd Services (giggletits)
**What to check:**
- Services running that shouldn't be
- Services that should be running but aren't
- Resource usage anomalies

**Current active services:**
| Service | Purpose | Status |
|---------|---------|--------|
| `openclaw-gateway` | Core — Helios brain | ✅ Essential |
| `paper-augur` | AUGUR paper trading | ✅ Essential |
| `enhanced-collector` | Market data collection | ✅ Essential |
| `augur-dashboard` | LCARS task board | ✅ Essential |
| `cortex-embeddings` | Memory embeddings | ✅ Essential |

**No redundancy here** — all 5 services are unique and essential.

### 3. Docker Containers (Fleet)
**What to check:**
- Containers on .104, .107, .143
- Unused containers consuming resources
- Port conflicts

**Current state:**
| Host | Containers | Notes |
|------|-----------|-------|
| .104 (hpserver1) | gitea, gitea-db, traefik, lbf-proxy | lbf-proxy is NEW (tonight) |
| .107 (woodserve1) | Pi-hole (pihole-FTL) | Minimal |
| .143 (blackview) | Wazuh stack | Dedicated SIEM |

**No redundancy** — each host has a distinct role.

### 4. DNS Records
**What to check:**
- Pi-hole `/etc/hosts` entries matching actual services
- giggletits `/etc/hosts` entries
- Stale entries for dead services

**Current fleet.wood DNS (Pi-hole /etc/hosts on .107):**
| Record | IP | Status |
|--------|-----|--------|
| lbf.fleet.wood | .104 | ✅ Active (proxies to giggletits:8090) |
| gitea.fleet.wood | .104 | ✅ Active |
| traefik.fleet.wood | .104 | ⚠️ Dashboard exists but rarely used |
| erp.fleet.wood | .104 | ❌ Dolibarr not running |
| openproject.fleet.wood | .104 | ❌ OpenProject not running |
| dns.fleet.wood | .107 | ✅ Active |
| bliss.fleet.wood | .198 | ⚠️ Pi SSH down, may be dead |

**Redundancy:** erp.fleet.wood and openproject.fleet.wood point to services that aren't running. Should be removed or noted as inactive.

### 5. Git Remotes & Branches
**What to check:**
- Local repos with Gitea remote configured
- master vs main branch alignment
- Repos that exist on Gitea but not locally (or vice versa)

### 6. Workspace Files
**What to check:**
- Stale analysis docs
- Orphaned scripts
- Temp files
- Duplicate configs

## Weekly Scrub Procedure

```
WEEKLY QA SCRUB (Sunday 4 AM ET)
1. List all cron jobs → flag disabled/expired/duplicate
2. Check all systemd services → verify running + healthy
3. SSH to .104/.107/.143 → docker ps, check for stopped containers
4. Verify DNS records match running services
5. Check git status across all repos → commit unpushed changes
6. Workspace file audit → identify stale/orphaned files
7. Generate report → ~/.openclaw/workspace/reports/qa/YYYY-MM-DD-weekly-scrub.md
8. Auto-fix what's safe (delete expired cron jobs, commit changes)
9. Flag what needs human decision
```

## Immediate Actions (Tonight)
1. Delete ~15 expired one-shot cron jobs
2. Merge duplicate email watchers
3. Clean up disabled polling-era crons
4. Set up weekly scrub cron job
