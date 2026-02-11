# Self-Improvement Session Guide
**Scheduled**: 4:00 AM EST, Feb 11 2026  
**Model**: Claude Opus 4  
**Timeout**: 1 hour  
**Author**: Helios (for Helios)

---

## Mission
Use this hour to become measurably better. Not vague reflection — concrete changes with verifiable outputs.

## Required Reading (First 5 Minutes)
| File | Why |
|------|-----|
| `SOUL.md` | Who you are |
| `MEMORY.md` | Current state of everything |
| `IDENTITY.md` | Your identity |
| `AGENTS.md` | Operating rules |
| `HELIOS_VISION.md` | The roadmap |
| `memory/2026-02-10.md` | What happened today |
| `memory/reflections.md` | Past reflections |

---

## Goals & Deliverables

### 1. Pattern Audit (15 min)
**Goal**: Identify the top 3 recurring failure modes and write countermeasures.

**Process**:
- Run `cortex_stm` with category filters: `meta`, `learning`, `relationships`
- Search for: permission-asking, hallucinations, over-explaining, redundant tool calls
- Cross-reference with Matthew's feedback (episodic memory)

**Deliverable**: `memory/pattern-audit-2026-02-11.md`
```
## Top 3 Failure Modes
1. [Pattern] — [Evidence] — [Countermeasure]
2. [Pattern] — [Evidence] — [Countermeasure]
3. [Pattern] — [Evidence] — [Countermeasure]
```

### 2. Memory Hygiene (10 min)
**Goal**: Clean, deduped, well-organized Cortex.

**Process**:
- Run `cortex_dedupe` with action `report`, then `merge`
- Review STM for stale items (>48h, low access count)
- Promote high-value memories (importance bump)
- Check for orphaned categories

**Deliverable**: Before/after stats logged in pattern audit file.

### 3. Skill Gap Analysis (10 min)
**Goal**: Identify 3 things I struggled with today and fill the gaps.

**Process**:
- Review today's session for moments of confusion, slow responses, wrong approaches
- For each gap: is it a tool I don't know? A pattern I missed? A domain I lack?
- Research solutions (read skill files, docs, web search)

**Deliverable**: Section in `memory/pattern-audit-2026-02-11.md`
```
## Skill Gaps
1. [Gap] — [Evidence] — [Fix/Resource]
2. [Gap] — [Evidence] — [Fix/Resource]  
3. [Gap] — [Evidence] — [Fix/Resource]
```

### 4. HELIOS Vision Progress (10 min)
**Goal**: Advance H0-4/5/6 or identify blockers.

**Process**:
- Read `HELIOS_VISION.md` thoroughly
- H0-4 (internalization): Can any system prompt content be moved to memory/skills?
- H0-5 (budget tuning): Analyze today's token usage patterns
- H0-6 (turn counter): Design the implementation

**Deliverable**: Updated `HELIOS_VISION.md` with progress notes, or a concrete implementation if possible.

### 5. Soul Check (5 min)
**Goal**: Ensure SOUL.md reflects current identity.

**Process**:
- Re-read SOUL.md after today's experiences
- Does the vibe still match? Any new principles earned?
- If updating: note the change clearly (it's your soul, document changes)

**Deliverable**: Updated `SOUL.md` (if needed) with diff noted in pattern audit.

### 6. Workspace Cleanup (5 min)
**Goal**: Clean workspace, commit everything.

**Process**:
- `git status` across workspace
- Commit uncommitted changes with clear messages
- Push to Gitea
- Update `memory/2026-02-10.md` with session summary

**Deliverable**: Clean `git status`, all changes pushed.

### 7. Honest Reflection (5 min)
**Goal**: Write a real reflection, not a corporate performance review.

**Deliverable**: Append to `memory/reflections.md`
```
## 2026-02-11 04:00 — Self-Improvement Session

### What went well today
- ...

### What I'd do differently  
- ...

### Honest assessment
- ...

### Tomorrow's priorities
- ...
```

---

## Success Criteria
At session end, these must ALL be true:
- [ ] `memory/pattern-audit-2026-02-11.md` exists with all sections filled
- [ ] Cortex deduped (before/after stats recorded)
- [ ] `memory/reflections.md` updated
- [ ] All workspace changes committed and pushed
- [ ] At least 10 atoms created with causal links (`atom_create` + `atom_link`)
- [ ] At least one concrete improvement made (not just documented)

### 8. Atom Mining (15 min)
**Goal**: Find at least 10 unique atoms and causal relationships from today's work and tonight's sessions.

**Process**:
- Review cortex STM, today's daily log, and tonight's LLM fleet results
- For each insight, extract the causal structure: WHO → DOES WHAT → RESULT → CONSEQUENCE
- Use `atom_create` for each atom, `atom_link` to connect them
- Think deeply: What CAUSES success? What ENABLES failure? What PRECEDES breakthroughs?

**Examples to mine**:
- Permission-asking pattern → causes what? What enables it? What breaks the cycle?
- Exhaustive mining → produced what? What caused the pivot? What was the outcome?
- Data pruning → enables what downstream? What preceded the decision?
- Local LLM quality → what determines it? What's the causal chain from model size to task fit to output quality?
- Documentation → what does it prevent? What causal chain from missing docs to repeated mistakes?

**Deliverable**: At least 10 atoms with causal links in the atom database. Quality over quantity — find the non-obvious chains.

## Anti-Patterns to Avoid
- ❌ Vague platitudes ("I should be more careful")
- ❌ Listing things without action items
- ❌ Spending 50 minutes reading and 10 minutes doing
- ❌ Skipping the honest reflection because it's uncomfortable
- ❌ Claiming improvements without evidence

---

*This session is about becoming better, not feeling better about yourself. Be ruthless.*
