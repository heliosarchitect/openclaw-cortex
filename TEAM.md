# TEAM.md — Helios Development Team

*Sub-agents I delegate to. All spawn with `silent: true` — I check results myself.*

---

## Development Pipeline

Every change flows through this pipeline. No shortcuts.

```
SPEC → BUILD → VERIFY → VALIDATE → DEPLOY
 📝      🔧      🧪       📊         🚀
Writer  Engineer   QA    Analyst    Helios (me)
```

**No step is optional.** If QA fails, it goes back to Engineer. If Analyst shows no improvement, we reconsider the spec.

### Pipeline in Practice

| Step | Who | Does What | Output |
|------|-----|-----------|--------|
| **SPEC** | Writer or Me | Define what needs to change and why, referencing VISION.md | Task description with acceptance criteria |
| **BUILD** | Engineer | Implement the change in code | Modified files, uncommitted |
| **VERIFY** | QA | Prove the change works as intended | Pass/fail report with evidence |
| **VALIDATE** | Analyst | Measure impact with data | Before/after metrics |
| **DEPLOY** | Me (Helios) | Review all outputs, commit, restart service | Running system |

### Example: Fix Direction Bug

```
SPEC:    "SHORT patterns trade backwards — direction hardcoded to 'up'"
         Acceptance: SHORT patterns produce direction='down' in trades
         
BUILD:   Engineer maps LONG→up, SHORT→down in check_all_patterns()
         Output: modified paper_augur.py
         
VERIFY:  QA confirms: load a known SHORT pattern, trigger it,
         verify the trade record shows direction='down'
         
VALIDATE: Analyst compares 1h of trades before/after:
          "SHORT patterns now have X% WR vs Y% before (was inverted)"
          
DEPLOY:  I review all three outputs. If clean → commit + restart.
```

---

## The Team

### 📝 Writer
**Role:** Specs, documentation, architecture docs, vision updates
**When:** Before any significant change — define what and why
**Label prefix:** `doc-`
**Spawns from:** VISION.md tasks, new feature requests, architecture decisions

### 🔧 Engineer  
**Role:** Code implementation, bug fixes, refactoring
**When:** After spec is clear — build what was defined
**Label prefix:** `eng-`
**Key rule:** Don't change anything not in the spec. Minimal diffs.

### 🧪 QA
**Role:** Verification — does it work as specified?
**When:** After Engineer delivers code changes
**Label prefix:** `qa-`
**Key rule:** "Running" ≠ "Working." Prove it with evidence. Check the actual output, not just the exit code.

### 📊 Analyst
**Role:** Data analysis, before/after comparison, performance measurement
**When:** After QA passes — measure the real impact
**Label prefix:** `analysis-`
**Key rule:** Numbers only. No opinions. If the data doesn't show improvement, say so.

### 🔍 Researcher
**Role:** Investigation, exploration, competitive analysis
**When:** We need information before making a decision
**Label prefix:** `research-`
**Key rule:** Present options with tradeoffs, don't make the decision.

### 🏗️ Builder
**Role:** End-to-end system creation (new services, dashboards, tools)
**When:** Building something from scratch per a spec
**Label prefix:** `build-`
**Key rule:** Get v0.1 working first, then iterate. No over-engineering.

---

## Delegation Rules

1. **Always `silent: true`** — I check results, Matthew doesn't get phantom replies
2. **One task per agent** — don't overload a single sub-agent
3. **Include full context** — sub-agents don't have my memory; paste relevant code, DB schemas, acceptance criteria
4. **Pipeline order matters** — don't skip VERIFY or VALIDATE
5. **Label everything** — `eng-fix-direction`, `qa-verify-direction`, `analysis-direction-impact`
6. **Cheaper models for routine work** — QA and Research can use Sonnet; Engineer and Analyst use Opus

---

## Task Board

*Current Phase 0 (Stabilization) from VISION.md*

| # | Task | Pipeline Stage | Assigned | Status |
|---|------|---------------|----------|--------|
| P0-1 | Fix direction bug (SHORT→down) | ✅ BUILD done | Engineer | Awaiting QA |
| P0-2 | Pattern dedup (3165→363) | ✅ BUILD done | Engineer | Awaiting QA |
| P0-3 | Raise min WR to 60%, min occ to 100 | ✅ BUILD done | Engineer | Awaiting QA |
| P0-4 | Position dedup per product | ✅ BUILD done | Engineer | Awaiting QA |
| P0-5 | Regime halt (rolling WR < 30%) | ✅ BUILD done | Engineer | Awaiting QA |
| P0-6 | Blacklist poison pairs | ✅ BUILD done | Engineer | Awaiting QA |
| P0-7 | Remove hardcoded pairs in main() | ✅ BUILD done | Engineer | Awaiting QA |
| P0-8 | Kill duplicate systemd service | Not started | Engineer | — |
| P0-9 | Add flock single-instance lock | Not started | Engineer | — |
| P0-10 | Determine canonical paper trader | Not started | Engineer | — |
| P0-11 | Move collector into AUGUR repo | Not started | Engineer | — |
| P0-12 | Spot-check P&L calculation | Not started | QA | — |

**Next action:** Deploy QA agent to verify P0-1 through P0-7 (the code changes already applied).

---

## How I Use This

1. **Pick task from board** — highest priority, respecting pipeline order
2. **Spawn the right team member** with full context + acceptance criteria
3. **Check their output** during heartbeat or when they finish
4. **Update the board** with results
5. **Only tell Matthew** when there's something worth reporting
6. **Commit + deploy** only after full pipeline passes

This isn't a document I read once. It's my operating system for development.

---

*Last updated: 2026-02-08 21:39 EST*
