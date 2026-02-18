# BC/DR — Business Continuity & Disaster Recovery
<!-- AI.TOC: BC/DR — Business Continuity & Disaster Recovery — Read lines 1-20 for navigation.
  §1 What's Backed Up                           → lines 9-29
  §2 Backup Schedule                            → lines 30-38
  §3 Backup Destinations                        → lines 39-58
  §4 RPO / RTO Targets                          → lines 59-71
  §5 Restore Procedures                         → lines 72-138
  §6 Monitoring                                 → lines 139-148
  §7 Scripts Reference                          → lines 149-159
  §8 Manual Recovery Contact                    → lines 160-165
  Total: 165 lines | Sections: 8
-->

**System:** Helios (OpenClaw) + brain.db  
**Last Updated:** 2026-02-12  
**Owner:** Matthew / Helios

---

## What's Backed Up

| Asset | Size | Location | Format |
|-------|------|----------|--------|
| brain.db | ~14MB | `~/.openclaw/workspace/memory/brain.db` | SQLite WAL, 8 tables + FTS5 |
| brain.db JSON export | ~11MB | Portable JSON with base64-encoded embeddings | JSON |
| Workspace | ~30MB | `~/.openclaw/workspace/` | tar.gz |
| Cortex Python | ~50KB | `~/Projects/helios/extensions/cortex/python/` | tar.gz |

### Tables in brain.db (8 data tables)
- `messages` (88 rows) — Synapse inter-agent messages
- `threads` (22) — Conversation threads
- `read_receipts` (64) — Message read tracking
- `acks` (5) — Message acknowledgments
- `stm` (2,887) — Short-term memory entries
- `atoms` (96) — Atomic knowledge units
- `causal_links` (31) — Causal chain connections
- `embeddings` (2,987) — Vector embeddings for semantic search

---

## Backup Schedule

| Job | Script | Frequency | Cron |
|-----|--------|-----------|------|
| Brain backup | `~/bin/brain-backup-cron` | Every 6 hours | `0 */6 * * *` |
| Full Helios backup | `~/bin/helios-full-backup` | Daily 3 AM | `0 3 * * *` |

---

## Backup Destinations

### 1. Local (giggletits — 192.168.10.163)
- **Path:** `/tmp/brain_backups/` (brain), `/tmp/helios_backups/` (full)
- **Retention:** 7 brain backups, 3 full backups
- **Purpose:** Fast restore, immediate access

### 2. Remote (hpserver1 — 192.168.10.104:2222)
- **Path:** `~/backups/brain/`, `~/backups/helios/`
- **Retention:** 30 brain backups, 14 full backups
- **Purpose:** Survives local disk failure, 390GB available
- **Access:** `ssh -p 2222 hpserver1`

### 3. Google Drive (heliosarchitectlbf@gmail.com)
- **Folder:** `Helios-Backup` (ID: `1hOKp5XvyT68lPpkANxxZooySV7Z74Tu9`)
- **Upload tool:** `gog drive upload`
- **Purpose:** Off-site, survives LAN-wide failure

---

## RPO / RTO Targets

| Metric | Target | Achievable |
|--------|--------|------------|
| **RPO** (max data loss) | 6 hours | 6h (brain backup interval) |
| **RTO** (time to restore) | 15 minutes | ~5 min (JSON import) |

- Worst case data loss: 6 hours of STM/atom writes
- Full workspace restore from hpserver1: ~2 minutes (rsync over LAN)
- Full workspace restore from Google Drive: ~10 minutes (download + extract)

---

## Restore Procedures

### Quick Restore: brain.db from hot backup
```bash
# Stop OpenClaw
openclaw gateway stop

# Copy from local backup
cp /tmp/brain_backups/brain_YYYYMMDD_HHMMSS.db ~/.openclaw/workspace/memory/brain.db

# Or from hpserver1
scp -P 2222 hpserver1:~/backups/brain/brain_YYYYMMDD_HHMMSS.db ~/.openclaw/workspace/memory/brain.db

# Restart
openclaw gateway start
```

### Full Restore: brain.db from JSON export
```bash
# Stop OpenClaw
openclaw gateway stop

# Remove corrupted DB
rm ~/.openclaw/workspace/memory/brain.db*

# Import from JSON (creates fresh DB with schema + FTS5)
python3 ~/Projects/helios/extensions/cortex/python/brain_backup.py import \
    /tmp/brain_backups/brain_backup_YYYYMMDD_HHMMSS.json \
    --target ~/.openclaw/workspace/memory/brain.db

# Restart
openclaw gateway start
```

### Full Restore: from hpserver1
```bash
# Brain only
scp -P 2222 hpserver1:~/backups/brain/brain_YYYYMMDD_HHMMSS.db ~/.openclaw/workspace/memory/brain.db

# Full workspace
scp -P 2222 hpserver1:~/backups/helios/helios_full_YYYYMMDD_HHMMSS.tar.gz /tmp/
cd /
tar -xzf /tmp/helios_full_YYYYMMDD_HHMMSS.tar.gz
```

### Full Restore: from Google Drive
```bash
# List available backups
gog drive list --parent 1hOKp5XvyT68lPpkANxxZooySV7Z74Tu9 --account heliosarchitectlbf@gmail.com

# Download specific backup
gog drive download <FILE_ID> --output /tmp/brain_backup.json

# Import
python3 ~/Projects/helios/extensions/cortex/python/brain_backup.py import \
    /tmp/brain_backup.json \
    --target ~/.openclaw/workspace/memory/brain.db
```

### Verify Restore
```bash
~/bin/brain-restore-test
# Should show 15/15 PASS
```

---

## Monitoring

- **Log file:** `/tmp/brain-backup.log`
- **Check last run:** `tail -20 /tmp/brain-backup.log`
- **Verify cron:** `crontab -l | grep -i backup`
- **Check remote copies:** `ssh -p 2222 hpserver1 "ls -la ~/backups/brain/ | tail -5"`
- **Check Drive:** `gog drive list --parent 1hOKp5XvyT68lPpkANxxZooySV7Z74Tu9 --account heliosarchitectlbf@gmail.com`

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `~/bin/brain-backup-cron` | JSON export + hot backup + rsync + Drive upload + rotation |
| `~/bin/helios-full-backup` | Brain backup + workspace tar + rsync + Drive upload |
| `~/bin/brain-restore-test` | Export → import → compare rows → FTS5 test → integrity check |
| `~/Projects/helios/extensions/cortex/python/brain_backup.py` | Core export/import engine |

---

## Manual Recovery Contact

- **Matthew** — system owner, full SSH access to all hosts
- **Helios** — can run restore procedures via OpenClaw CLI
- **hpserver1** — accessible via `ssh -p 2222 hpserver1` (key auth)
