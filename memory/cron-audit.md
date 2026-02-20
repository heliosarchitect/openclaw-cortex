# OpenClaw Cron Jobs Audit Report
**Date:** 2026-02-16 19:17 EST  
**Audit Type:** Full audit and cleanup recommendations  
**Total Jobs Found:** 30 jobs  

## Executive Summary
- **Active Jobs:** 16 enabled, 14 disabled
- **Schedule Types:** 19 cron expressions, 7 one-time "at" jobs, 4 repeating "every" jobs
- **Major Issues:** 4 clear duplicates, 9 expired one-time jobs, several with questionable relevance
- **Recommendations:** Remove 9 expired jobs, disable 3 redundant jobs, consolidate 2 duplicates

## Job Inventory Table

| Name | Status | Schedule | Type | Last Run | Next Run | Priority | Notes |
|------|--------|----------|------|----------|----------|----------|--------|
| AUGUR Trading Day Start - 9:00 AM | ✅ Active | 0 9 * * 1-5 | cron | 2026-02-15 | 2026-02-17 | **HIGH** | Core trading functionality |
| AUGUR Trading Day End - 6:00 PM | ✅ Active | 0 18 * * 1-5 | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Core trading functionality |
| Cortex Nightly Maintenance | ✅ Active | 0 2 * * * | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Memory management |
| Cortex Weekly Deep Review | ✅ Active | 0 2 * * 0 | cron | 2026-02-16 | 2026-02-23 | **HIGH** | Weekly maintenance |
| Email Check | ❌ Disabled | every 30min | every | 2026-02-13 | - | LOW | Should be conditional |
| World Events Monitor | ❌ Disabled | every 30min | every | 2026-02-13 | - | LOW | Resource intensive |
| Proactive Work Rotation | ❌ Disabled | every 15min | every | 2026-02-13 | - | LOW | Too frequent |
| End of Day Reflection & Commit | ✅ Active | 0 23 * * * | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Important workflow |
| helios-nightly-backup | ✅ Active | 0 3 * * * | cron | 2026-02-16 | 2026-02-17 | **CRITICAL** | BC/DR essential |
| Cancel 1Password Reminder | ✅ Active | at specific time | at | - | 2026-02-21 | MEDIUM | One-time reminder |
| Night Shift Productivity | ❌ Disabled | 0 23,1,3,5,7 * * * | cron | 2026-02-12 | - | LOW | **EXPIRED PURPOSE** |
| Weekly QA Redundancy Scrub | ✅ Active | 0 4 * * 0 | cron | 2026-02-16 | 2026-02-23 | **HIGH** | Infrastructure health |
| augur-daily-report | ✅ Active | 0 18 * * 1-5 | cron | 2026-02-16 | 2026-02-17 | **HIGH** | **DUPLICATE SCHEDULE** with Trading Day End |
| augur-db-backup | ✅ Active | 0 19 * * * | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Data backup |
| self-improvement-session | ❌ Disabled | 0 4 11 2 * | cron | 2026-02-11 | - | LOW | **EXPIRED** (Feb 11 only) |
| AUGUR Signal Miner | ✅ Active | 45 18 * * 1-5 | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Core functionality |
| AUGUR Signal Update for Matthew | ❓ Expired | at specific time | at | - | - | LOW | **EXPIRED** (Feb 12) |
| Blitz Sprint — 60s Heartbeat | ❌ Disabled | every 60s | every | - | - | LOW | **EXPIRED** (Feb 12 sprint) |
| AUGUR EOD Analysis | ✅ Active | 0 23 * * * | cron | 2026-02-16 | 2026-02-17 | **HIGH** | **DUPLICATE SCHEDULE** with End of Day |
| augur-eod-analysis-DISABLED | ❌ Disabled | every 4h | every | 2026-02-14 | - | LOW | **LABELED AS DUPLICATE** |
| brain-embed-pending | ❌ Disabled | every 15min | every | - | - | LOW | **DEPRECATED** (old brain system) |
| SYNAPSE poll (Nova collab) | ❌ Disabled | every 60s | every | 2026-02-12 | - | LOW | **EXPIRED** (Feb 12 collab) |
| Disable Nova SYNAPSE poll | ❓ Expired | at specific time | at | - | - | LOW | **EXPIRED** (Feb 12) |
| SYNAPSE Poll (Nova active) | ❌ Disabled | every 5min | every | 2026-02-12 | - | LOW | **EXPIRED** (Feb 12 collab) |
| morning-improvements-proposal | ❌ Disabled | at specific time | at | 2026-02-13 | - | LOW | **EXPIRED** (Feb 13) |
| Conditional Email Check | ❌ Disabled | every 30min | every | - | - | LOW | **REDUNDANT** with Email Check |
| ai-model-watch | ✅ Active | every 1h | every | 2026-02-16 | 2026-02-16 | MEDIUM | Model monitoring |
| memory-hygiene | ✅ Active | 0 4 * * * | cron | 2026-02-16 | 2026-02-17 | **HIGH** | Memory cleanup |
| gateway-restart-reminder | ❌ Disabled | at specific time | at | 2026-02-14 | - | LOW | **EXPIRED** (Feb 14) |
| context-window-monitor | ❌ Disabled | every 30min | every | 2026-02-14 | - | LOW | **NOT NEEDED** (manual monitoring) |
| benchy-check-30min | ❌ Disabled | at specific time | at | 2026-02-16 | - | LOW | **EXPIRED** (print finished) |
| RC Frame Print - Halfway Check | ❌ Disabled | at specific time | at | 2026-02-16 | - | LOW | **EXPIRED** (print finished) |
| RC Frame Print - Completion Check | ❌ Disabled | at specific time | at | 2026-02-16 | - | LOW | **EXPIRED** (print finished) |

## Critical Issues Found

### 1. **Duplicate Schedules (Schedule Conflicts)**
- **AUGUR Trading Day End (18:00)** vs **augur-daily-report (18:00)** vs **AUGUR Signal Miner (18:45)**
  - All three fire within 45 minutes on weekdays
  - Risk of resource conflicts and race conditions
- **End of Day Reflection (23:00)** vs **AUGUR EOD Analysis (23:00)**
  - Both fire at same time daily
  - Both are I/O intensive

### 2. **Expired One-Time Jobs (9 jobs)**
Should be **REMOVED** immediately:
- `AUGUR Signal Update for Matthew` (Feb 12, 2026)
- `Disable Nova SYNAPSE poll` (Feb 12, 2026)
- `morning-improvements-proposal` (Feb 13, 2026)
- `gateway-restart-reminder` (Feb 14, 2026)
- `benchy-check-30min` (Feb 16, 2026)
- `RC Frame Print - Halfway Check` (Feb 16, 2026)
- `RC Frame Print - Completion Check` (Feb 16, 2026)
- `self-improvement-session` (Feb 11 only, recurring disabled)
- `Blitz Sprint — 60s Heartbeat` (Feb 12 sprint, disabled)

### 3. **Deprecated/Redundant Jobs (3 jobs)**
Should be **DISABLED** or removed:
- `brain-embed-pending`: Uses old brain system, replaced by Cortex
- `Conditional Email Check`: Redundant with main `Email Check` job
- `augur-eod-analysis-DISABLED`: Already labeled as duplicate

### 4. **Resource Intensive Disabled Jobs**
Currently disabled but may cause issues if re-enabled:
- `Proactive Work Rotation` (every 15min): Too frequent
- `Night Shift Productivity` (every 2h overnight): High token usage
- `World Events Monitor` (every 30min): API heavy

## Schedule Analysis

### Peak Activity Windows
- **18:00-19:00 Weekdays:** 3 AUGUR jobs + daily report + database backup
- **23:00 Daily:** 2 jobs (EOD reflection + AUGUR analysis)
- **02:00-04:00 Nightly:** 4 maintenance jobs spread across timeframe

### Recommendations for Schedule Optimization
1. **Stagger 18:00 jobs:** Move AUGUR Signal Miner to 17:45, Daily Report to 18:30
2. **Separate 23:00 jobs:** Move AUGUR EOD Analysis to 23:30
3. **Spread nightly maintenance:** Current 2AM-4AM spread is good

## Missing Jobs Assessment

### Potentially Missing Jobs
1. **Git commit check:** Weekly check for uncommitted workspace changes
2. **Service health check:** Hourly systemd service status check
3. **Disk space monitor:** Daily check for low disk space
4. **Log rotation:** Weekly cleanup of large log files

### Jobs That Are Working Well
- **AUGUR ecosystem:** Core trading jobs are properly scheduled and active
- **Backup strategy:** Both database and full system backups covered
- **Memory management:** Cortex maintenance is comprehensive

## Specific Recommendations

### IMMEDIATE ACTIONS (Safe to execute)
1. **REMOVE** all 9 expired one-time jobs
2. **DISABLE** the 3 deprecated/redundant jobs
3. **CLEAN UP** job descriptions with outdated references

### SCHEDULE ADJUSTMENTS NEEDED
1. **Move AUGUR Signal Miner:** 18:45 → 17:45 (before market close rush)
2. **Move augur-daily-report:** 18:00 → 18:30 (after trading day end)
3. **Move AUGUR EOD Analysis:** 23:00 → 23:30 (avoid collision)

### CONFIGURATION IMPROVEMENTS
1. **Add timeout limits** to jobs missing explicit timeouts
2. **Standardize model usage:** Most jobs don't specify model, defaulting to Opus
3. **Add retry logic** for critical backup jobs

## Resource Impact Analysis

### High Resource Jobs (Monitor closely)
- `Weekly QA Redundancy Scrub`: 17+ seconds runtime
- `AUGUR Signal Miner`: 2+ minutes, high CPU
- `augur-daily-report`: 2+ minutes runtime
- `augur-db-backup`: 57 seconds with network I/O

### Low Resource Jobs (Efficient)
- Most systemEvent jobs: 5-13ms runtime
- Memory hygiene: 13ms runtime
- Backup jobs: 9-13ms (excluding data transfer)

## Conclusion

The cron job system has grown organically and needs pruning. **16 active jobs is reasonable**, but **9 expired jobs** should be removed immediately. The **schedule conflicts at 18:00 and 23:00** need resolution to prevent race conditions.

**Priority 1:** Remove expired jobs  
**Priority 2:** Fix schedule conflicts  
**Priority 3:** Consider adding missing health monitoring jobs

**System Health:** Despite the clutter, core functionality (AUGUR trading, backups, memory management) is well covered and running reliably.