# Helios/Cortex Memory System — Version Forensics

## Current State
**VERSION**: v0.3.0 (Self-Improvement Sprint)  
**DEPLOYMENT**: Production active on OpenClaw workspace  
**LAST COMMIT**: Feature branch with 7 critical bug fixes  
**DATE**: 2026-02-14  

## Active Features with Behavioral Signatures

### FEATURE: "Brain.db Direct Memory Access" (v0.3.0)
**ADDED IN**: v0.3.0 (2026-02-14)

**BEHAVIORAL SIGNATURE**:
- Log pattern: `brain.db` direct SQLite operations vs `stm.json` file operations
- Tool call sequence: cortex_* tools → brain_api.py → SQLite transactions
- Response pattern: Memory operations return transaction IDs, not file timestamps
- Failure mode: **7 CODE PATHS SILENTLY FAILED** when writing to empty stm.json

**IMPLEMENTS**:
- Changes to: All cortex mutation tools (update, edit, move, dedup)
- Adds decision branch: SQLite transactions vs JSON file operations  
- Modifies priority: Database consistency over file-based memory

**DEBUGGING HOOKS**:
- If you see `brain.db` in logs → new system active
- If `stm.json` operations → **BUG**: old broken code path
- Rollback test: Check `ls -la ~/.openclaw/workspace/memory/stm.json` (should be 2 bytes: "{}")

**KNOWN BUG (FIXED)**: Cortex Tools Silent Failure
- **Root cause**: 7 code paths still writing to empty `stm.json` after brain.db migration
- **Impact**: Memory mutations were no-ops for days (dedup, update, edit, move)
- **Fix**: All tools now use `brain_api.py` directly
- **Log signature**: `grep "stm.json" ~/.openclaw/logs/` shows no recent writes

**ROLLBACK PLAN**:
- Revert commits `f22cf50`, `78f7ad7` 
- Side effects: Breaks memory persistence, returns to file-based system
- Fallback behavior: v0.2.0 JSON-based memory (functional but not scalable)

**INTERACTS WITH**:
- Depends on: brain_api.py SQLite interface
- Conflicts with: Legacy extensions reading stm.json
- Modifies behavior of: All memory tools, conversation summarizer, self-reflection

---

### FEATURE: "Automated Memory Hygiene" (v0.3.0)
**ADDED IN**: v0.3.0 (2026-02-14)

**BEHAVIORAL SIGNATURE**:
- Log pattern: Daily 4 AM EST cron job with deduplication stats
- Tool call sequence: `cortex_dedupe → cortex_prune → memory_stats`
- Response pattern: "Pruned X duplicates, Y memories remain" in cron logs
- Failure mode: Memory pollution accumulation if cron fails

**IMPLEMENTS**:
- Changes to: Daily maintenance cron at 4 AM EST
- Adds decision branch: Automated cleanup vs manual memory management
- Modifies priority: Proactive hygiene over reactive cleanup

**DEBUGGING HOOKS**:
- If you see 4 AM cron activity → feature active
- If memory count keeps growing → cron not running or failing
- Check: `crontab -l | grep memory` shows hygiene schedule

**ROLLBACK PLAN**:
- Remove from crontab: `crontab -e` and delete memory hygiene line
- Side effects: Manual memory cleanup required
- Fallback behavior: v0.2.0 manual deduplication when needed

---

### FEATURE: "GitHub Release Monitor" (v0.3.0)
**ADDED IN**: v0.3.0 (2026-02-14)

**BEHAVIORAL SIGNATURE**:
- Log pattern: 4-hourly polling of 9 repos (OpenClaw, n8n, Ansible, etc.)
- Tool call sequence: GitHub API → release check → Signal notification if new
- Response pattern: "New release: [repo] v[version]" messages
- Failure mode: Notification spam if release detection logic breaks

**IMPLEMENTS**:
- Changes to: Replaces Releasebot dependency with direct GitHub API
- Adds decision branch: Self-hosted monitoring vs third-party service
- Modifies priority: Real-time release awareness over periodic manual checks

**DEBUGGING HOOKS**:
- If you see GitHub API calls in logs → feature active  
- If no release notifications for >24h → monitor might be broken
- Check: `ps aux | grep release-monitor` for running process

**ROLLBACK PLAN**:
- Disable cron job and return to Releasebot
- Side effects: Dependency on external service returns
- Fallback behavior: Manual release checking or Releasebot notifications

---

### FEATURE: "Workspace File Organization" (v0.3.0)
**ADDED IN**: v0.3.0 (2026-02-14)

**BEHAVIORAL SIGNATURE**:
- Log pattern: Files moved from root to `analysis/`, `scripts/`, `reports/` directories
- Tool call sequence: File categorization → directory creation → bulk move operations
- Response pattern: "Organized 50 files into proper directory structure"
- Failure mode: Files in wrong directories, broken relative paths

**IMPLEMENTS**:
- Changes to: Workspace directory structure organization
- Adds decision branch: Categorized storage vs flat file structure
- Modifies priority: Organized workspace over convenience of root-level files

**DEBUGGING HOOKS**:
- If you see organized directory structure → feature active
- If files reappear in root → organization not maintained
- Check: `find ~/.openclaw/workspace -maxdepth 1 -type f | wc -l` (should be <10)

**ROLLBACK PLAN**:
- Move files back to workspace root from subdirectories
- Side effects: Cluttered workspace but simpler file access
- Fallback behavior: v0.2.0 flat file organization

---

## Feature Interaction Map

```
Brain.db Migration (v0.3.0) ←─── ALL Memory Operations
    ↓                              ↓
Memory Hygiene (v0.3.0) ──→ Automated Dedup ──→ Clean STM
    ↓                              ↓
File Organization (v0.3.0) ──→ Structured Workspace
    ↓
GitHub Monitor (v0.3.0) ──→ Release Notifications

AMPLIFIES: Brain.db + Hygiene = Reliable memory operations
CONFLICTS: File Organization + Legacy scripts = Broken relative paths
GATES: Brain.db fixes enable all other memory features
```

## Rollback Sequence (v0.3.0 → v0.2.0)

**IMMEDIATE** (If memory system breaks):
1. Check `~/.openclaw/workspace/memory/brain.db` exists and has data
2. Verify `stm.json` is empty (`{}` only)
3. Restart OpenClaw gateway if memory tools fail

**SYSTEMATIC ROLLBACK**:
1. **Disable Memory Hygiene** → Remove from cron: `crontab -e`
2. **Disable GitHub Monitor** → Kill cron job
3. **Flatten File Organization** → Move files back to workspace root  
4. **Revert to stm.json** → Restore commits before brain.db migration

**VERIFICATION**:
- Test memory operations: `cortex_add`, `cortex_stm`, `cortex_dedupe`
- Confirm file paths still work in scripts
- Verify cron jobs removed from `crontab -l`

## Bug Fix Chain Documentation

### BUG: Cortex Tools Silent Failure (CRITICAL - FIXED)
**DISCOVERED**: v0.3.0 sprint  
**IMPACT**: 7 code paths writing to empty stm.json, memory mutations were no-ops for days  

**ROOT CAUSE ANALYSIS**:
1. **Migration Issue**: brain.db migration only updated READ paths in TypeScript
2. **Write Operations**: cortex_update, cortex_edit, cortex_move, cortex_dedupe still used stm.json
3. **Detection**: stm.json remained "{}" despite mutation commands
4. **Evidence**: Memory corruption and pollution continued despite "fixes"

**FIX DESCRIPTION**:
- Migrated all cortex tools to use brain_api.py directly
- Updated TypeScript bridge methods to call brain.db
- Added pre-commit hook to prevent stm.json writes
- Verified all tools now return transaction confirmations

**DEBUGGING PATH**:
```bash
# Check if bug is present
ls -la ~/.openclaw/workspace/memory/stm.json
# Should show 2 bytes: "{}"

# Verify brain.db is active
sqlite3 ~/.openclaw/workspace/memory/brain.db ".tables"
# Should show: embeddings, stm, atoms, etc.

# Test memory operations
echo "Test memory" | cortex_add content="test"
# Should return transaction ID, not file timestamp
```

**VERIFICATION**:
- Before: Memory tools returned success but stm.json unchanged
- After: Memory tools return SQLite transaction IDs and data persists
- Log change: No more stm.json write operations in logs

**REGRESSION RISKS**:
- Might break: Legacy extensions still expecting stm.json
- Watch for: Extensions failing to load memory
- Monitor: brain.db file size should grow with new memories

---

### BUG: Extension Memory Access (MEDIUM - FIXED)
**DISCOVERED**: v0.3.0 sprint  
**IMPACT**: conversation-summarizer and self-reflection reading empty data  

**ROOT CAUSE**: Extensions still calling deprecated loadSTMDirect() reading stm.json
**FIX**: Migrated extensions to use brain_api interface

**DEBUGGING PATH**:
```bash
# Check extension logs
tail ~/.openclaw/logs/extension-*.log

# Verify brain_api usage
grep -r "loadSTMDirect" ~/.openclaw/extensions/
# Should return no results after fix
```

---

### BUG: Memory Category Pollution (LOW - FIXED)
**DISCOVERED**: v0.3.0 sprint  
**IMPACT**: 334 duplicate memories, api_filter_test pollution  

**ROOT CAUSE**: Testing activities created memory pollution
**FIX**: Pruned duplicates, cleaned test categories, improved categorization

**VERIFICATION**:
- Before: 1,700+ memories with many duplicates
- After: 1,370 clean memories  
- Tool: `cortex_dedupe report` shows <1% similarity matches

---

## Production Incident Response

### Memory Operations Failing
**SYMPTOMS**: cortex_add, cortex_update returning errors or no effect
**LOG SIGNATURE**: `sqlite3.OperationalError` or stm.json write attempts
**IMMEDIATE ACTION**: Restart OpenClaw gateway, verify brain.db exists
**ESCALATION**: If brain.db corrupt, restore from backup

### Cron Jobs Failing  
**SYMPTOMS**: Memory growing unchecked, no release notifications
**LOG SIGNATURE**: Cron daemon errors in `/var/log/syslog`
**ACTION**: Check `crontab -l`, test individual cron commands
**FALLBACK**: Disable automated hygiene, return to manual cleanup

### File Organization Breaks Scripts
**SYMPTOMS**: Scripts can't find files, broken relative paths  
**LOG SIGNATURE**: "No such file or directory" errors
**ACTION**: Update script paths or move files back to root
**ROLLBACK**: Flatten workspace back to v0.2.0 structure

### Extensions Not Loading Memory
**SYMPTOMS**: Conversation summarizer, self-reflection report empty memory
**LOG SIGNATURE**: Extensions calling loadSTMDirect() unsuccessfully
**ACTION**: Verify extensions using brain_api.py interface
**ROLLBACK**: Restore stm.json-based memory system

## Forensic Queries (6 months from now)

```bash
# Find which version introduced a behavior
git log --oneline --grep="brain.db"  
git log --oneline --grep="stm.json"

# Verify memory system health
sqlite3 ~/.openclaw/workspace/memory/brain.db "SELECT COUNT(*) FROM stm;"
ls -la ~/.openclaw/workspace/memory/stm.json  # Should be 2 bytes

# Check automated hygiene
crontab -l | grep -i memory
tail ~/.openclaw/logs/cron-memory-hygiene.log

# Verify file organization
find ~/.openclaw/workspace -maxdepth 1 -type f | wc -l  # Should be <10
ls -la ~/.openclaw/workspace/*/  # Should show organized subdirs

# Debug extension memory access  
grep -r "brain_api\|loadSTMDirect" ~/.openclaw/extensions/
tail ~/.openclaw/logs/extension-*.log

# Check for silent failures
grep "stm.json" ~/.openclaw/logs/helios.log | tail -10  # Should be empty
```

## Memory System Health Check

```bash
#!/bin/bash
# Quick health check script for Helios memory system

echo "=== MEMORY SYSTEM HEALTH CHECK ==="

# 1. Brain.db status
echo "Brain.db size: $(du -h ~/.openclaw/workspace/memory/brain.db | cut -f1)"
echo "STM records: $(sqlite3 ~/.openclaw/workspace/memory/brain.db 'SELECT COUNT(*) FROM stm;')"

# 2. stm.json should be empty  
STM_SIZE=$(stat -c%s ~/.openclaw/workspace/memory/stm.json)
if [ $STM_SIZE -eq 2 ]; then
    echo "✓ stm.json properly empty"
else  
    echo "✗ stm.json not empty ($STM_SIZE bytes) - BUG PRESENT"
fi

# 3. Cron jobs active
echo "Memory hygiene cron: $(crontab -l | grep -c memory)"
echo "GitHub monitor cron: $(crontab -l | grep -c github)"

# 4. File organization
ROOT_FILES=$(find ~/.openclaw/workspace -maxdepth 1 -type f | wc -l)
echo "Root files: $ROOT_FILES (should be <10)"

echo "=== END HEALTH CHECK ==="
```

---

*Generated by Helios VERSION_FORENSICS framework — searchable, greppable, debuggable.*  
*When memory breaks: run health check first, then grep this file.*