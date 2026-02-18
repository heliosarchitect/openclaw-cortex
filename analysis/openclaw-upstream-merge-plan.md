# OpenClaw Upstream Merge Plan
*Analysis Date: 2026-02-12 20:16 EST*

## Executive Summary

Our fork is **49 commits ahead** and **927 commits behind** upstream OpenClaw. We have **39 files** with potential merge conflicts, including **19 critical security fixes** we're missing.

**Risk:** Medium to High — security vulnerabilities and core stability fixes pending.
**Timeline:** 2-3 hours with Nova for systematic merge.
**Strategy:** Selective cherry-pick + manual conflict resolution.

## Gap Analysis

### Our Custom Code (49 commits, 100 files)
- **extensions/cortex/** — Full Python backend (brain.db, atoms, embeddings, SYNAPSE)
- **src/agents/workspace.ts** — H0-4 file internalization (hash caching)
- **Config/defaults** — Model routing, opus-4-6 defaults
- **Tests** — 75 new tests for brain.db, concurrent ops, MCP integration

### Upstream Changes We're Missing (927 commits)
- **Security:** 19 fixes (auth bypass, injection hardening, webhook validation)
- **Stability:** 341 bug fixes (session management, memory leaks, tool reliability)
- **Features:** 56 new features (Discord improvements, media handling, cron enhancements)

### High-Conflict Files (39 overlapping)
**CRITICAL (core agent logic):**
- `src/agents/workspace.ts` — Our H0-4 vs upstream session changes
- `src/agents/model-selection.ts` — Our routing vs upstream model logic
- `src/agents/tools/*.ts` — Our tool mods vs upstream tool fixes

**MEDIUM (config/integration):**
- `.env.example` — Our vars vs upstream vars
- `README.md` — Our docs vs upstream docs
- `extensions/*/index.ts` — Plugin compatibility

## Security Exposure

**IMMEDIATE RISKS:**
1. **Browser auth bypass** — `fix(browser): require auth on control HTTP` (9230a2ae1)
2. **Webhook auth bypass** — BlueBubbles loopback proxy trust (f836c385f) 
3. **Session transcript tampering** — Path resolution hardening (4199f9889)
4. **Signal validation bypass** — E.164 hardening (4543c401b)
5. **Untrusted web tool execution** — Transcript hardening (da55d70fb)

## Merge Strategy

### Phase 1: Security Hot-Fixes (30 min)
Cherry-pick security fixes to a `security-patches` branch:
```bash
git checkout -b security-patches
git cherry-pick 9230a2ae1  # browser auth
git cherry-pick 4199f9889  # transcript hardening  
git cherry-pick 113ebfd6a  # hook auth hardening
git cherry-pick da55d70fb  # web tool hardening
git cherry-pick 4543c401b  # Signal validation
# ... (14 more security fixes)
```

### Phase 2: Core Stability (60 min)
Target critical stability fixes:
- Session management improvements
- Memory leak fixes
- Tool reliability patches
- Discord/media handling fixes

### Phase 3: Feature Integration (90 min)
Selective feature pulls:
- Cron enhancements (if compatible with our cron jobs)
- New tool capabilities
- Performance improvements

### Phase 4: Conflict Resolution
**workspace.ts:** Merge our H0-4 hash caching with upstream session fixes
**model-selection.ts:** Integrate our routing with upstream model logic
**extensions:** Ensure plugin compatibility

## Pre-Merge Checklist

- [ ] **Backup current state** — `git tag pre-upstream-merge-$(date +%Y%m%d)`
- [ ] **Test suite baseline** — Run full test suite, record passing tests
- [ ] **Service health** — Verify AUGUR, brain.db, cortex all operational
- [ ] **Gitea sync** — Push current state to our Gitea before merging

## Success Criteria

1. **Security:** All 19 security fixes applied without breaking our features
2. **Functionality:** brain.db, cortex, SYNAPSE, H0-4 still operational
3. **Stability:** Test suite passes (>=current pass rate)
4. **Performance:** No regression in token usage or response time

## Rollback Plan

If merge fails:
1. `git reset --hard pre-upstream-merge-YYYYMMDD`
2. Force push to restore known-good state
3. File upstream incompatibility issues in Gitea
4. Plan incremental mini-merges instead

## Recommendation

**Execute now.** The security exposure alone justifies immediate action. Our custom code is cleanly isolated in `extensions/cortex/` and should merge with minimal conflict. The risk of staying behind is higher than the merge complexity.

**Next Step:** Spawn Nova with this plan for execution.