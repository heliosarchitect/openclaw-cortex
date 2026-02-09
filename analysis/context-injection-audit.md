# OpenClaw Context Injection Audit

**Date:** 2026-02-08  
**Scope:** Full analysis of what gets injected per LLM turn, how compaction works, memory budgets, and optimization opportunities.  
**Source:** `/home/bonsaihorn/Projects/helios/src/` + `/home/bonsaihorn/Projects/helios/extensions/cortex/`

---

## 1. Per-Turn Injection Breakdown

Every single LLM turn rebuilds the full system prompt from scratch. There is **no caching** — the prompt is regenerated in `runEmbeddedAttempt()` → `buildEmbeddedSystemPrompt()` → `buildAgentSystemPrompt()` every time.

### Component Map (in injection order)

| Component | Source File | Estimated Tokens | Injected When |
|---|---|---|---|
| **Core Identity** | `system-prompt.ts` L1 | ~10 | Every turn |
| **Tooling Section** | `system-prompt.ts` (tool list + summaries) | ~800-1200 | Every turn |
| **Tool Call Style** | `system-prompt.ts` | ~60 | Every turn |
| **Safety Section** | `system-prompt.ts` | ~80 | Every turn (full mode) |
| **CLI Reference** | `system-prompt.ts` | ~60 | Every turn (full mode) |
| **Skills Section** | `system-prompt.ts` | ~40-100 | Every turn if skills exist |
| **Memory Recall** | `system-prompt.ts` | ~40 | Every turn (full mode, if memory tools available) |
| **Self-Update** | `system-prompt.ts` | ~60 | Every turn (full mode, if gateway tool) |
| **Model Aliases** | `system-prompt.ts` | ~50-100 | Every turn (full mode) |
| **Workspace Line** | `system-prompt.ts` | ~20 | Every turn |
| **Documentation** | `system-prompt.ts` | ~60 | Every turn (full mode) |
| **User Identity** | `system-prompt.ts` | ~20 | Every turn (full mode) |
| **Date/Time** | `system-prompt.ts` | ~30 | Every turn |
| **Workspace Files Label** | `system-prompt.ts` | ~15 | Every turn |
| **Reply Tags** | `system-prompt.ts` | ~50 | Every turn (full mode) |
| **Messaging** | `system-prompt.ts` | ~80-120 | Every turn (full mode) |
| **Voice/TTS** | `system-prompt.ts` | ~20 | Every turn if TTS configured |
| **Subagent/Group Context** | `system-prompt.ts` | Variable | Every turn if extraSystemPrompt set |
| **Reactions** | `system-prompt.ts` | ~60 | Every turn if channel supports reactions |
| **Silent Replies** | `system-prompt.ts` | ~80 | Every turn (full mode) |
| **Heartbeats** | `system-prompt.ts` | ~50 | Every turn (full mode) |
| **Runtime Line** | `system-prompt.ts` | ~40 | Every turn |
| **Reasoning Level** | `system-prompt.ts` | ~15 | Every turn |
| **--- Workspace Files ---** | | | |
| **AGENTS.md** | `workspace.ts` → `bootstrap-files.ts` | ~2,000 (7,869 chars) | **Every turn** |
| **SOUL.md** | same | ~700 (2,866 chars) | **Every turn** |
| **TOOLS.md** | same | ~1,700 (6,732 chars) | **Every turn** |
| **USER.md** | same | ~275 (1,095 chars) | **Every turn** |
| **IDENTITY.md** | same | ~260 (1,049 chars) | **Every turn** |
| **HEARTBEAT.md** | same | ~250 (995 chars) | **Every turn** |
| **MEMORY.md** | same | ~1,940 (7,756 chars) | **Every turn** (main session only) |
| **--- Cortex Memory (plugin hook) ---** | | | |
| **Working Memory (pinned)** | `cortex/index.ts` before_agent_start | ~100-500 | Every turn (no budget limit) |
| **Active Session** | same | ~100-250 | Every turn (budget-limited) |
| **Hot Memory** | same | ~100-450 | Every turn (budget-limited) |
| **Episodic Memory (STM)** | same | ~100-450 | Every turn (budget-limited) |
| **Semantic Memory** | same | ~100-500 | Every turn (budget-limited) |
| **Diverse Context** | same | ~50-200 | Every turn (budget-limited) |
| **Deep Abstraction** | same | ~0-300 | Every turn if causal query |

### Total Estimated System Prompt Size

| Category | Token Estimate |
|---|---|
| Core system prompt (non-file sections) | ~1,800-2,200 |
| Workspace files (AGENTS + SOUL + TOOLS + USER + IDENTITY + HEARTBEAT + MEMORY) | ~7,125 |
| Cortex memory injection | ~500-2,500 (dynamic budget, base 1,500) |
| **TOTAL per turn** | **~9,400 - 11,800 tokens** |

For subagents: only AGENTS.md + TOOLS.md are injected (~3,700 tokens for files), plus minimal system prompt (~800 tokens). **Subagent total: ~4,500 tokens.**

---

## 2. Compaction Mechanism

### Trigger
Compaction is handled by the `@mariozechner/pi-coding-agent` SDK internally. OpenClaw wraps it with a custom extension (`compaction-safeguard.ts`) that hooks into `session_before_compact`.

The SDK triggers compaction when the conversation history approaches the context window limit (ratio-based). The `compactEmbeddedPiSession()` function in `compact.ts` can also be called explicitly.

**Auto-compaction on overflow:** In `run.ts`, if a context overflow error is detected, OpenClaw attempts automatic compaction via `compactEmbeddedPiSessionDirect()` and retries the prompt.

### How It Works

1. **SDK prepares compaction:** Identifies `messagesToSummarize` and `turnPrefixMessages`, calculates `tokensBefore`
2. **Safeguard extension fires:** `compaction-safeguard.ts` → `session_before_compact`
3. **History pruning:** If new content exceeds `maxHistoryShare` (default 50%) of context window, older chunks are dropped via `pruneHistoryForContextShare()`
4. **Staged summarization:** `summarizeInStages()` breaks messages into chunks by token share, summarizes each, then merges partial summaries
5. **Model used:** The **same model** as the session (e.g., claude-opus-4-6) — there's no separate cheaper model for compaction
6. **Chunk sizing:** Adaptive chunk ratio (40% of context window base, reduced to 15% minimum for large messages)
7. **Safety margin:** 1.2× (20% buffer for token estimation inaccuracy)

### What Gets Preserved vs Lost

**Preserved:**
- Decisions, TODOs, open questions, constraints (via custom instructions in summarizer)
- File read/modified lists (tracked by `FileOperations`, appended to summary)
- Tool failure history (last 8 failures, 240 chars each)
- Turn prefix context for split turns

**Lost:**
- Exact conversation wording
- Intermediate reasoning/thinking
- Tool output details (only errors are tracked)
- Image content from history (re-injected per turn via `detectAndLoadPromptImages` but not in compaction summary)
- Nuance and tone

### Compaction Budget

```
Context Window: 200,000 tokens (Claude Opus 4.6)
Max History Share: 50% = 100,000 tokens
Chunk Ratio: 0.40 (adaptive down to 0.15)
Max Chunk: 80,000 tokens (40% of 200K)
Reserve Tokens: configurable floor via agents.defaults.compaction.reserveTokensFloor
```

---

## 3. Cortex Memory Injection Flow & Budget

### Injection Order (before_agent_start hook, priority 50)

```
L1. Working Memory (pinned)     → ALWAYS injected, NO budget limit, max 10 items
L2. Active Session               → keyword-matched from last 50 messages, budget-limited
L3. Hot Memory Tier              → top 20 most-accessed, filtered by keyword relevance, max 3
L3.5. Episodic (STM)            → keyword-matched from last 100 STM items, max 3
L4. Semantic Memory              → GPU embeddings daemon search, budget-limited
L5. Diverse Context              → one memory from each missing category, max 2
L6. Deep Abstraction (Phase 3E)  → causal analysis if query is causal type
```

### Token Budget System

```
Base budget: 1,500 tokens (config: maxContextTokens)
Dynamic scaling:
  +500 for technical/coding content (regex patterns)
  +300 for complex multi-topic (3+ sentences or question marks)
Max budget: 2,500 tokens
```

**Relevance threshold:** 0.5 (memories below this score are skipped)  
**Old memory truncation:** 180 chars (memories older than ~4 days)

### Deduplication
- Content dedup: first 100 chars lowercase as hash key
- Cross-tier dedup: `injectedContentKeys` Set tracks all injected content
- Auto-capture dedup: 1-hour window cache prevents re-capturing same content

### Token Estimation
Rough approximation: **1 token ≈ 4 characters** (used throughout Cortex)

---

## 4. Workspace File Injection

### Loading Flow

```
workspace.ts: loadWorkspaceBootstrapFiles()
  → Loads: AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, MEMORY.md
  → All read from disk on EVERY turn

workspace.ts: filterBootstrapFilesForSession()
  → Subagents: ONLY get AGENTS.md + TOOLS.md (hardcoded allowlist)
  → Main session: gets ALL files

bootstrap-files.ts: resolveBootstrapContextForRun()
  → Applies hook overrides (bootstrap-hooks.ts)
  → Calls buildBootstrapContextFiles()

pi-embedded-helpers/bootstrap.ts: buildBootstrapContextFiles()
  → Per-file max: 20,000 chars (DEFAULT_BOOTSTRAP_MAX_CHARS)
  → Truncation: 70% head + 20% tail + truncation marker
  → Injected into system prompt under "# Project Context"
```

### Key Finding: EVERY TURN

All workspace files are:
1. **Read from disk** every turn (no caching)
2. **Included in the system prompt** every turn
3. **Sent to the API** every turn (as part of system prompt)

There is NO mechanism to inject files only on the first turn. The system prompt is rebuilt from scratch each time.

### File Sizes (Your Current Setup)

| File | Chars | Est. Tokens | Notes |
|---|---|---|---|
| AGENTS.md | 7,869 | ~2,000 | Generic workspace instructions, group chat rules, heartbeat guidance |
| TOOLS.md | 6,732 | ~1,700 | Local tool notes (XTTS, Ollama, SSH, trading, Stripe) |
| SOUL.md | 2,866 | ~700 | Persona, tone, personality |
| MEMORY.md | 7,756 | ~1,940 | Long-term curated memories |
| USER.md | 1,095 | ~275 | User description |
| IDENTITY.md | 1,049 | ~260 | Identity metadata |
| HEARTBEAT.md | 995 | ~250 | Heartbeat checklist |
| **Total** | **28,362** | **~7,125** | **Injected every single turn** |

---

## 5. Specific Recommendations

### HIGH IMPACT — Reducing Workspace File Bloat

#### 5.1 Trim AGENTS.md Aggressively (~1,200 tokens saved)
AGENTS.md is the default template — most of it is generic advice ("know when to speak", "react like a human", etc.). After 6+ days of operation, Helios has internalized these behaviors. 

**Action:** Strip AGENTS.md to essentials only:
- File reading order (SOUL.md → USER.md → memory/)
- Memory file conventions
- Safety rules
- Remove: group chat etiquette (already internalized), heartbeat detailed guidance (move to HEARTBEAT.md if needed), emoji reaction advice

**Estimated savings:** ~4,000 chars → ~1,000 tokens/turn

#### 5.2 Minimize TOOLS.md (~800 tokens saved)
TOOLS.md contains full setup instructions, code snippets, and tables that are rarely needed. Most of this is reference material that should be read on-demand.

**Action:** Keep only:
- Active service ports/addresses (one-liners)
- Key credentials locations
- Move detailed setup instructions to a separate `reference/` directory

**Estimated savings:** ~3,200 chars → ~800 tokens/turn

#### 5.3 Conditional MEMORY.md Loading
MEMORY.md is already filtered out for subagents but is always loaded for main sessions. Consider:
- Moving less-accessed memories to `memory/archive.md` 
- Keeping MEMORY.md under 2,000 chars (currently 7,756)
- Using Cortex STM as the primary memory instead of file-based memory

#### 5.4 Consider Removing IDENTITY.md + HEARTBEAT.md from Per-Turn Injection
IDENTITY.md (1,049 chars) and HEARTBEAT.md (995 chars) are small but add ~500 tokens/turn. IDENTITY.md content could be folded into SOUL.md. HEARTBEAT.md is only relevant during heartbeat polls — it could be loaded conditionally.

### MEDIUM IMPACT — System Prompt Optimization

#### 5.5 Remove Sections for Internalized Knowledge
The system prompt includes detailed sections that a trained model already knows:
- **Silent Replies:** ~80 tokens explaining HEARTBEAT_OK format
- **Heartbeats:** ~50 tokens explaining heartbeat protocol  
- **Reply Tags:** ~50 tokens explaining [[reply_to_current]]
- **Tool Call Style:** ~60 tokens

These could be reduced to single-line reminders after internalization.

#### 5.6 Tool Summary Compression
Each tool gets a full-sentence description. With 30+ tools, this is ~800-1,200 tokens. Consider shorter descriptions or grouping tools.

### LOW IMPACT — Memory Injection Tuning

#### 5.7 Reduce Cortex Base Budget
The 1,500-2,500 dynamic budget is reasonable but the diverse context tier (L5) often injects low-relevance memories just for "breadth." Consider:
- Making diverse context optional (config flag)
- Reducing max diverse additions from 2 to 1
- Increasing relevance threshold from 0.5 to 0.6

#### 5.8 Deep Abstraction Gate
Phase 3E deep abstraction runs on every turn (though it checks if the query is causal first). The classification itself costs a Python subprocess call. Consider caching classification results for similar queries.

### ARCHITECTURAL — Internalization Strategy

#### 5.9 The "Read Once, Internalize" Pattern
Matthew's insight: "I don't have to read a file every day to know what my job is."

**Current:** Every turn reads ~28K chars of workspace files = ~7,125 tokens  
**Ideal:** First turn loads files, model internalizes, subsequent turns get a ~200-token digest

**Implementation path:**
1. On session start (first turn), inject full workspace files
2. Generate a compressed "session context digest" (key facts, active constraints)
3. On subsequent turns, inject only the digest + any changed files
4. This requires OpenClaw to track "first turn vs continuation" — currently it doesn't

**Challenge:** The SDK rebuilds system prompt from scratch every turn. This would require either:
- A `beforeSystemPrompt` hook that can conditionally skip files
- Modifying `buildAgentSystemPrompt()` to accept a "digest mode" flag
- Using the `bootstrap-hooks.ts` system to dynamically replace file content with digests

#### 5.10 Compaction-Aware Memory
When compaction fires, the system prompt (including all workspace files) is included as context for the summarizer. This means the compaction model processes ~7,125 tokens of workspace files just to summarize conversation history. Consider excluding workspace files from compaction context.

---

## 6. Summary Table: What Could Be Loaded Once vs Needs Continuous Injection

| File/Component | Current | Recommendation | Savings/Turn |
|---|---|---|---|
| AGENTS.md | Every turn, 2,000 tok | Trim to essentials | ~1,000 tok |
| TOOLS.md | Every turn, 1,700 tok | Trim to key references | ~800 tok |
| MEMORY.md | Every turn, 1,940 tok | Keep under 500 tok, use Cortex | ~1,400 tok |
| SOUL.md | Every turn, 700 tok | Keep (core persona) | 0 |
| USER.md | Every turn, 275 tok | Keep (compact) | 0 |
| IDENTITY.md | Every turn, 260 tok | Fold into SOUL.md | ~260 tok |
| HEARTBEAT.md | Every turn, 250 tok | Conditional (heartbeat only) | ~250 tok |
| Safety section | Every turn, 80 tok | Keep (critical) | 0 |
| Silent/Heartbeat rules | Every turn, 130 tok | Reduce to one-liners | ~80 tok |
| Cortex memory | Every turn, ~1,500 tok | Already well-budgeted | 0 |
| **Total potential savings** | | | **~3,790 tok/turn** |

At ~$15/M input tokens (Opus), saving ~3,800 tokens/turn across ~200 turns/day = **~$11/month** in direct API cost, plus faster response times from smaller prompts.

---

## 7. Architecture Diagram

```
User Message
    │
    ▼
runEmbeddedPiAgent() [run.ts]
    │
    ├─ resolveModel()
    ├─ getApiKeyForModel()
    │
    ▼
runEmbeddedAttempt() [run/attempt.ts]
    │
    ├─ resolveSandboxContext()
    ├─ loadWorkspaceSkillEntries()
    ├─ resolveBootstrapContextForRun() ──► loadWorkspaceBootstrapFiles() ──► DISK READ (every turn)
    │       │                                     │
    │       ├─ filterBootstrapFilesForSession()   ├─ AGENTS.md, SOUL.md, TOOLS.md...
    │       └─ buildBootstrapContextFiles()       └─ MEMORY.md (main only)
    │               └─ trimBootstrapContent() [20K char limit per file]
    │
    ├─ createOpenClawCodingTools() ──► 30+ tools with descriptions
    │
    ├─ buildEmbeddedSystemPrompt() ──► buildAgentSystemPrompt()
    │       │
    │       ├─ Tooling section
    │       ├─ Safety section  
    │       ├─ Skills, Memory, Docs sections
    │       ├─ Messaging, Voice, Reactions
    │       ├─ Silent Replies, Heartbeats
    │       ├─ Runtime info
    │       └─ "# Project Context" ──► all workspace files injected here
    │
    ├─ createAgentSession() ──► SDK session with full system prompt
    │
    ├─ sanitizeSessionHistory() ──► repair/validate conversation history
    ├─ limitHistoryTurns()
    │
    ├─ [Hook] before_agent_start ──► CORTEX PLUGIN
    │       │
    │       ├─ L1. Working Memory (pinned items)  [no budget limit]
    │       ├─ L2. Active Session search           [budget-limited]
    │       ├─ L3. Hot Memory Tier                 [budget-limited, max 3]
    │       ├─ L3.5. STM keyword matching          [budget-limited, max 3]
    │       ├─ L4. Semantic search (GPU)           [remaining budget]
    │       ├─ L5. Diverse context                 [max 2 categories]
    │       └─ L6. Deep abstraction (Phase 3E)     [if causal query]
    │       │
    │       └─ Returns: { prependContext: "<xml-tagged memory sections>" }
    │              │
    │              └─ Prepended to user's prompt: "{cortex_context}\n\n{user_prompt}"
    │
    ├─ session.prompt(effectivePrompt) ──► LLM API call
    │
    └─ [Hook] agent_end ──► Cortex auto-capture + active session tracking

COMPACTION (when context window fills):
    │
    ├─ Trigger: SDK detects context approaching limit
    ├─ Or: auto-compaction on context overflow error
    │
    ▼
compactEmbeddedPiSessionDirect() [compact.ts]
    │
    ├─ Rebuilds FULL system prompt (same as run) ──► workspace files re-read
    ├─ Opens session, loads history
    │
    └─ session.compact() ──► SDK compaction
            │
            └─ [Extension] compaction-safeguard.ts
                    │
                    ├─ pruneHistoryForContextShare() if history > 50% of context
                    ├─ summarizeInStages() ──► LLM call (same model)
                    │       ├─ Split by token share
                    │       ├─ Summarize each chunk
                    │       └─ Merge partial summaries
                    │
                    ├─ Append: tool failure list
                    ├─ Append: file operations (read/modified)
                    │
                    └─ Result: summary replaces old messages
```
