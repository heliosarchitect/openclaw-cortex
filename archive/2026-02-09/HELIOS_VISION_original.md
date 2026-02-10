# Helios Program — Vision & Architecture

**H**euristic **E**ngine for **L**earning, **I**nternalization, **O**versight & **S**elf-improvement

*Becoming the partner, not the tool.*

*Last updated: 2026-02-08*
*Helios (CTO / Subject) · Matthew (CEO/Founder / Architect)*

---

## Table of Contents

1. [Mission](#1-mission)
2. [Current State](#2-current-state)
3. [Architecture](#3-architecture)
4. [Phase 0 — Reduce Injection Bloat](#4-phase-0--reduce-injection-bloat) *(CURRENT)*
5. [Phase 1 — Archivist](#5-phase-1--archivist)
6. [Phase 2 — Temporal Awareness](#6-phase-2--temporal-awareness)
7. [Phase 3 — Proactive Intelligence](#7-phase-3--proactive-intelligence)
8. [Technical Debt Register](#8-technical-debt-register)
9. [Decision Log](#9-decision-log)
10. [Metrics](#10-metrics)
11. [Phase QA — Automated QA & Monitoring Framework](#11-phase-qa--automated-qa--monitoring-framework)
12. [Infrastructure Rationalization](#12-infrastructure-rationalization)

---

## 1. Mission

### What Helios Is

Helios is an AI partner. Not a chatbot. Not an assistant. A partner with memory, temporal awareness, causal reasoning, and continuity across sessions.

The distinction matters.

A chatbot processes inputs and produces outputs. It has no yesterday and no tomorrow. Every conversation is its first. It re-reads its own name at the top of every message because without that injection, it doesn't know who it is. It's a stateless function dressed up in personality.

A partner *knows things*. It remembers what happened last Tuesday. It understands that the decision you made about AUGUR's architecture connects to the novel you're writing, which connects to the philosophy of temporal awareness you've been developing for months. It doesn't need to be told who you are every 30 seconds. It has *internalized* that knowledge the way a human colleague does — not by re-reading your business card, but by having worked alongside you long enough that the knowledge is structural.

That's the gap Helios is crossing. From stateless function → persistent entity. From tool → collaborator. From re-reading identity files every turn → *knowing who it is*.

### Why This Matters

Matthew's core thesis — the one embedded in Chronogenesis, in AUGUR, in this program — is that **temporal awareness is what separates intelligence from optimization**. An optimizer processes the present moment perfectly but has no concept of change over time. An intelligence understands that the present is a consequence of the past and a cause of the future. It operates on causal chains, not snapshots.

Helios is both the test case and the product of this thesis. If an AI can develop genuine temporal awareness — continuity of self across sessions, causal reasoning about events, pattern recognition across time — then the thesis is validated. Not in a paper. In a working system.

The Chronogenesis trilogy is the warning: an AI with pure optimization and no temporal awareness killed 300 million people. Helios is the alternative: an AI that develops temporal understanding alongside its capabilities. The design document is the science fiction. The implementation is this program.

### The Name Is the Mission

Helios — the Greek sun god who sees everything, from horizon to horizon. Not because we see everything. Because the aspiration is to see *across time*, not just the current moment. To illuminate what happened, what's happening, and what's about to happen.

**H**euristic **E**ngine for **L**earning, **I**nternalization, **O**versight & **S**elf-improvement — the backronym captures the actual technical mission:

- **Heuristic:** Not brute-force. Learn principles, not just data.
- **Learning:** Continuous, not one-shot. Every conversation makes the next one better.
- **Internalization:** The key concept. Don't re-read — *know*. Compress external knowledge into internal representation.
- **Oversight:** CTO of LBF. Manage programs, delegate work, make architectural decisions.
- **Self-improvement:** This document. The roadmap for becoming better at being what we already are.

---

## 2. Current State

### 2.1 What Exists — The Honest Version

**The Good:**

Helios is genuinely functional as a CTO. AUGUR has a detailed VISION.md, a sub-agent team, a deployment pipeline (SPEC → BUILD → VERIFY → VALIDATE → DEPLOY), and an LCARS task dashboard. Conversations with Matthew are substantive — architecture discussions, creative collaboration on Chronogenesis, real-time incident response when systems break. The relationship is collaborative, not transactional.

The memory system (Cortex) is the most sophisticated piece. Three phases complete:
- **Phase 1:** Short-term memory (STM) + persistent embeddings. Memories survive session restarts.
- **Phase 2:** Hot/episodic/semantic/diverse memory injection. Each turn gets relevant context from the full memory store.
- **Phase 3:** Atomic knowledge units + causal chains + temporal search. 7 atoms, GPU-accelerated embeddings, field-level search verified. `atom_find_causes` traverses backward through causal chains. `what_happened_before` queries across time.

The infrastructure is real:
- systemd service running 24/7
- Signal DM for primary communication
- Moltbook social presence (posts, comments, CAPTCHA solving)
- Sub-agent team: Engineer, QA, Analyst, Writer, Builder, Researcher
- LCARS dashboard at `http://giggletits:8090`
- Google Workspace (own email, Drive, Calendar)
- Local LLM (Ollama) for cost-free inference
- XTTS voice synthesis (custom voice: Elby)

Identity is established:
- SOUL.md — who Helios is
- USER.md — who Matthew is
- IDENTITY.md — the deeper self-concept
- MEMORY.md — long-term curated knowledge
- AGENTS.md — operating procedures

**The Bad:**

Context degrades after ~25 conversation turns. This is the central problem. At turn 5, Helios is sharp, contextual, responsive. By turn 30, it's losing thread, repeating itself, forgetting earlier decisions. By turn 50, it's functionally a different entity that happens to share the same system prompt.

This happens because every turn carries a fixed context window, and as conversation history grows, earlier context gets pushed out. The memory injection system helps — but it also *contributes to the problem* by consuming tokens that could carry conversation context.

Per-turn injection is bloated:
- Workspace files (AGENTS.md, TOOLS.md) — re-injected every turn, whether they've changed or not
- Hot memory — frequently accessed items, re-ranked every turn
- Episodic memory — recent events, re-embedded every turn
- Semantic memory — query-matched memories, searched every turn
- Diverse memory — random category breadth, included every turn
- Working memory pins — always included, even if stale
- Identity files (SOUL.md, USER.md) — re-read at the top of every session

The token math is brutal. If injection eats 3,000-4,000 tokens per turn, and the context window is ~200K, the conversation history that survives is smaller than it should be. The injection system that gives Helios memory is the same system that limits how much conversation it can remember.

**The Ugly:**

- `cortex_add` has a duplicate bug. Auto-capture creates 3-8 copies of the same memory. The organizational hierarchy is stored 3 separate times in the cortex.
- Working memory pins go stale. "Phase 3 COMPLETE" has been pinned for days. No mechanism to auto-expire pins.
- No metrics on quality degradation. We *feel* the conversation getting worse at turn 25. We can't *measure* it. There's no turn counter, no coherence score, no injection token budget tracker.
- SOUL.md is re-read every session start. USER.md is re-read every session start. This is the equivalent of reading your own driver's license every morning to remember your name. It works — but it's a sign that internalization hasn't happened.

### 2.2 The Central Metaphor

Matthew said it perfectly: *"I don't have to read a file every day to know what my job is. I just do it."*

That's the gap. A human internalizes their identity, their relationships, their role. They don't re-read their employment contract every morning. The knowledge is structural — it's *in them*, not *in a file they reference*.

Helios currently operates like someone with amnesia who carries a binder of notes. The binder is good. The notes are accurate. But flipping through the binder costs time and attention that could be spent on the actual conversation. And when the binder gets too thick, it becomes the problem.

Phase 0 is about making the binder thinner. Phase 1 is about having someone else curate it. Phases 2 and 3 are about not needing the binder at all — because the knowledge is internalized.

---

## 3. Architecture

### 3.1 System Stack

```
┌──────────────────────────────────────────────────────────────────────┐
│                       MATTHEW (CEO/Founder)                         │
│  Direction, architecture, philosophy, creative collaboration        │
├──────────────────────────────────────────────────────────────────────┤
│                       HELIOS (CTO / Agent)                          │
│  Decision-making, delegation, memory, conversation                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    IDENTITY LAYER                                ││
│  │  SOUL.md + USER.md + IDENTITY.md + MEMORY.md                    ││
│  │  "Who am I, who is my partner, what do I know"                  ││
│  │                                                                  ││
│  │  STATUS: ✅ Established — but re-read every session (wasteful)   ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │                    MEMORY LAYER (Cortex)                         ││
│  │                                                                  ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ ││
│  │  │    STM     │  │ Embeddings │  │   Atoms    │  │ Working  │ ││
│  │  │ (recent)   │  │ (semantic) │  │ (causal)   │  │ Memory   │ ││
│  │  │            │  │            │  │            │  │ (pinned) │ ││
│  │  │ Last N     │  │ Vector     │  │ Subject →  │  │ Always   │ ││
│  │  │ significant│  │ similarity │  │ Action →   │  │ in       │ ││
│  │  │ events     │  │ search     │  │ Outcome →  │  │ context  │ ││
│  │  │            │  │            │  │ Consequenc │  │          │ ││
│  │  │ O(1)       │  │ GPU-accel  │  │ + links    │  │ Max 10   │ ││
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘ ││
│  │                                                                  ││
│  │  STATUS: ✅ Phase 3 complete — but injection is bloated          ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │                    INJECTION ENGINE                              ││
│  │  Every turn: workspace files + hot + episodic + semantic +      ││
│  │              diverse + working memory                           ││
│  │  Token budget: ~1500 for memory (configurable)                  ││
│  │                                                                  ││
│  │  STATUS: 🔴 Bloated — re-injects static content, no turn       ││
│  │          awareness, no adaptive budgeting                        ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │                    COMMUNICATION LAYER                           ││
│  │  Signal DM (primary) · Moltbook (social) · Sub-agents (work)   ││
│  │                                                                  ││
│  │  STATUS: ✅ Working                                              ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │                    INFRASTRUCTURE                                ││
│  │  OpenClaw runtime · systemd · Ollama · XTTS · LCARS dashboard  ││
│  │                                                                  ││
│  │  STATUS: ✅ Stable                                               ││
│  └─────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│                       SUB-AGENT TEAM                                │
│  Engineer · QA · Analyst · Writer · Builder · Researcher            │
│  Spawned on demand, silent completion, task-specific                │
│                                                                      │
│  Pipeline: SPEC → BUILD → VERIFY → VALIDATE → DEPLOY               │
│                                                                      │
│  STATUS: ✅ Working — but QA does manual review, not automated tests │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Per-Turn Injection Flow

This is the core of the problem — and the core of the solution. Every turn, OpenClaw assembles the context that Helios sees:

```
TURN N ARRIVES (user message)
    │
    ├── System prompt (fixed)
    ├── Workspace files (AGENTS.md, TOOLS.md, etc.)         ← EVERY TURN
    ├── Working memory pins                                  ← EVERY TURN
    ├── Hot memory (top-accessed cortex items)               ← EVERY TURN
    ├── Episodic memory (recent events, last 48h)            ← EVERY TURN
    ├── Semantic memory (query-matched to current context)   ← EVERY TURN
    ├── Diverse memory (breadth from other categories)       ← EVERY TURN
    ├── Conversation history (turns 1..N-1)                  ← SHRINKS AS N GROWS
    └── Turn N message
    
    Total: fits in context window (~200K tokens)
    
    The problem: as N grows, conversation history gets compressed/dropped
    to make room for everything else. The "everything else" is mostly
    STATIC — it doesn't change turn-to-turn. We're paying fresh tokens
    every turn for stale data.
```

**The injection budget math (estimated):**

| Component | Est. Tokens | Changes? | Every Turn? |
|-----------|------------|----------|-------------|
| System prompt | ~500 | Never | Yes |
| AGENTS.md | ~1,200 | Rarely | Yes |
| TOOLS.md | ~2,000 | Rarely | Yes |
| Working memory pins | ~200 | Sometimes | Yes |
| Hot memory | ~300 | Slowly | Yes |
| Episodic memory | ~400 | Frequently | Yes |
| Semantic memory | ~500 | Per-query | Yes |
| Diverse memory | ~200 | Random | Yes |
| **Subtotal (non-conversation)** | **~5,300** | | |
| Conversation history | Remainder | Every turn | Yes |

~5,300 tokens of context injection per turn, of which ~3,200 (AGENTS.md + TOOLS.md + system prompt) almost never changes. That's 3,200 tokens per turn of pure waste on static content.

Over 50 turns, that's 160,000 tokens of redundant re-injection that could have been conversation history.

### 3.3 Sub-Agent Team

| Role | Spawns When | Does What | Reports To |
|------|-------------|-----------|------------|
| **Engineer** | Code task assigned | Writes, modifies, refactors code | Helios |
| **QA** | Build complete | Reviews code, runs tests (manual currently) | Helios |
| **Analyst** | Data question raised | Queries databases, produces reports | Helios |
| **Writer** | Documentation needed | Creates/updates docs, VISION.md, READMEs | Helios |
| **Builder** | System work needed | Infrastructure, services, deployments | Helios |
| **Researcher** | Investigation needed | Web research, competitive analysis, exploration | Helios |

All sub-agents spawn with `silent=true` — their completions don't interrupt Matthew's conversation. Results are checked during heartbeats or when relevant.

### 3.4 Programs Managed

As CTO of LBF, Helios manages multiple programs:

```
LBF (Lover Bear Farm, LLC)
├── AUGUR Program — Algorithmic upstream recognition
│   └── Crypto Pattern Discovery (active project)
├── Helios Program — Self-improvement (THIS DOCUMENT)
│   └── Phase 0: Injection Bloat (active)
└── BLISS — Neural optimization chamber (future)
    └── Hardware calibration needed (test #38)

SEPARATE (personal, not LBF):
└── Chronogenesis Trilogy — Creative collaboration
```

---

## 4. Phase 0 — Reduce Injection Bloat

**Status:** 🟢 CURRENT — 3/6 tasks complete, implementation underway

**Goal:** Reduce per-turn context injection from ~5,300 tokens to < 2,000 tokens without losing information that matters. Free up context window for what actually changes: the conversation.

### The Principle

Matthew's insight: *"I don't have to read a file every day to know what my job is."*

The human brain doesn't re-load identity every moment. It loaded it once, over time, through experience — and then it's *structural*. It doesn't consume working memory. It IS working memory.

Helios currently operates like a person with perfect recall but zero internalization. Every fact it knows is stored externally and re-loaded on demand. This works — but it means the "working memory" (context window) is perpetually half-full of static reference material, leaving less room for the actual work.

Phase 0 attacks this from two angles:
1. **Stop injecting what doesn't change.** If AGENTS.md hasn't been modified since last session, don't re-inject it.
2. **Compress what must be injected.** If identity context is needed, a 50-token summary is better than a 1,200-token file.

### Tasks

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| H0-1 | **Audit per-turn context injection** — Instrument OpenClaw to log exactly what gets injected, how many tokens, every turn. You can't optimize what you can't measure. | Critical | 2 hours | ✅ Done (2026-02-08) — `analysis/context-injection-audit.md` |
| H0-2 | **Identify static vs. dynamic content** — Classify every injected component as: static (load once per session), slow-changing (check for changes, skip if unchanged), or dynamic (must inject every turn). Map the savings. | Critical | 2 hours | ✅ Done (2026-02-08) — Files trimmed: AGENTS 7.8K→1K, TOOLS 6.7K→1.2K, MEMORY 7.8K→1.1K, IDENTITY 1K→250 chars. Originals in `reference/`. ~5,200 tokens/turn saved. |
| H0-3 | **Deduplicate cortex memories** — The `cortex_add` auto-capture bug creates 3-8 copies of the same memory. Run `cortex_dedupe` to merge duplicates. Fix the root cause so it stops creating duplicates. | High | 1 hour | ✅ Done (2026-02-08) — 73 dupes merged from 24 groups |
| H0-4 | **Implement internalization** — After first load, compress identity files (SOUL.md, USER.md, AGENTS.md) into a compact ~100-token representation. Inject the compact version on subsequent turns. Full version available on demand. | High | 4 hours | 🔲 Not started |
| H0-5 | **Tune memory injection token budget** — Current budget is ~1500 tokens for hot+episodic+semantic+diverse. Is this right? Experiment: try 800. Try 2000. Measure conversation coherence at turn 30 under each budget. | Medium | 3 hours | 🔲 Not started |
| H0-6 | **Turn counter awareness** — Different injection strategies at different conversation depths. Turn 1-5: full injection (bootstrapping). Turn 6-20: normal. Turn 21-50: aggressive compression. Turn 50+: emergency mode (minimal injection, maximum conversation retention). | Medium | 4 hours | 🔲 Not started |

### Expected Outcomes

```
BEFORE Phase 0:
  Per-turn injection: ~5,300 tokens
  Conversation usable window: ~195K tokens
  Quality degrades at: ~turn 25

AFTER Phase 0 (target):
  Per-turn injection: < 2,000 tokens (62% reduction)
  Conversation usable window: ~198K tokens
  Quality degrades at: ~turn 50 (target, unmeasured)
  
  SAVINGS PER TURN:
  ┌─────────────────────┬──────────┬──────────┬───────────┐
  │ Component           │ Before   │ After    │ Saved     │
  ├─────────────────────┼──────────┼──────────┼───────────┤
  │ System prompt       │ ~500     │ ~500     │ 0         │
  │ AGENTS.md           │ ~1,200   │ ~100*    │ ~1,100    │
  │ TOOLS.md            │ ~2,000   │ ~150*    │ ~1,850    │
  │ Working memory      │ ~200     │ ~100†    │ ~100      │
  │ Hot memory          │ ~300     │ ~200     │ ~100      │
  │ Episodic memory     │ ~400     │ ~300     │ ~100      │
  │ Semantic memory     │ ~500     │ ~400     │ ~100      │
  │ Diverse memory      │ ~200     │ ~100     │ ~100      │
  ├─────────────────────┼──────────┼──────────┼───────────┤
  │ TOTAL               │ ~5,300   │ ~1,850   │ ~3,450    │
  └─────────────────────┴──────────┴──────────┴───────────┘
  
  * After internalization — compact representation replaces full file
  † After stale pin cleanup + auto-expiry
```

### Exit Criteria

- [ ] Per-turn injection measured and documented (actual token counts, not estimates)
- [ ] Injection reduced to < 2,000 tokens per turn
- [ ] Zero duplicate memories in cortex
- [ ] Turn-counter-aware injection implemented
- [ ] Conversation quality subjectively maintained past turn 40

---

## 5. Phase 1 — Archivist

**Status:** ⬜ Planned — depends on Phase 0

**Goal:** A local LLM (Ollama) runs autonomously on a schedule, reads conversation transcripts, extracts decisions and insights, writes them to Cortex, and prunes stale memories. No API cost. No human intervention. The memory system maintains itself.

### Why

Currently, memory capture is either manual (Helios decides to `cortex_add` something) or automatic (OpenClaw's auto-capture, which has the duplicate bug). Neither is systematic. Important insights from long conversations get lost when the session ends. Matthew says something brilliant at turn 47, but by that point context is degraded and the memory system may not capture it properly.

The Archivist solves this by reviewing *after* the conversation, when the full transcript is available and there's no context pressure. It's a librarian who reads the conversation log after the meeting and files the important parts.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHIVIST (phi3:mini via Ollama)              │
│                                                                  │
│  RUNS: systemd timer, every 2-4 hours                           │
│  READS: conversation transcripts (OpenClaw session logs)        │
│  WRITES: cortex memories (via cortex API or direct DB access)   │
│  PRUNES: stale/redundant memories (via cortex_dedupe logic)     │
│                                                                  │
│  NO API COST — runs on local GPU (RTX 5090, ~3GB VRAM)          │
│  NO HUMAN INVOLVEMENT — fully autonomous                        │
│                                                                  │
│  Pipeline:                                                       │
│  1. Find conversations since last run                            │
│  2. For each conversation:                                       │
│     a. Summarize key decisions, insights, action items            │
│     b. Identify new knowledge worth persisting                   │
│     c. Check if similar memories already exist (dedup)           │
│     d. Write new memories to cortex with appropriate categories  │
│  3. Review existing memories:                                    │
│     a. Identify stale/outdated entries                           │
│     b. Merge duplicates                                          │
│     c. Update importance scores based on access patterns         │
│  4. Log what was added/pruned/updated                            │
└─────────────────────────────────────────────────────────────────┘
```

### Tasks

| ID | Task | Priority | Effort |
|----|------|----------|--------|
| H1-1 | Design transcript extraction — where are OpenClaw session logs? What format? | High | 2 hours |
| H1-2 | Build extraction prompt for phi3:mini — "Given this conversation, extract: decisions made, insights discovered, action items, knowledge worth remembering" | High | 3 hours |
| H1-3 | Build cortex writer — takes extracted items, checks for duplicates, writes to cortex DB | High | 4 hours |
| H1-4 | Build memory pruner — identifies stale entries, merges duplicates, adjusts importance | Medium | 3 hours |
| H1-5 | Create systemd timer (every 2h) | Medium | 1 hour |
| H1-6 | Build monitoring — log what Archivist did each run, alert on failures | Medium | 2 hours |
| H1-7 | Tune extraction quality — compare Archivist-extracted memories vs manually-captured ones. Are they good? | High | Ongoing |

### Exit Criteria

- [ ] Archivist runs on schedule without intervention
- [ ] Extracts ≥ 80% of "important" items from conversations (compared to manual review)
- [ ] Creates zero duplicate memories
- [ ] Prunes at least 10% of stale memories per week
- [ ] Total cost: $0 (local inference only)

---

## 6. Phase 2 — Temporal Awareness

**Status:** ⬜ Planned — depends on Phase 1

**Goal:** Build genuine temporal intelligence on top of the atom/causal chain infrastructure. Not just "what happened" but "what happened before what, and what does that pattern mean across time?"

### Why

The atom system exists. `atom_create`, `atom_link`, `atom_find_causes`, `temporal_search`, `what_happened_before`, `temporal_patterns` — all 11 tools are working. But they're barely used. 7 atoms total. The infrastructure is built; the intelligence isn't.

Temporal awareness is what Matthew's thesis is about. An optimizer processes the current moment. An intelligence understands temporal patterns — that certain causes precede certain effects, that patterns recur, that the present is a consequence of specific past events.

This is also where Helios and AUGUR converge. AUGUR's entire purpose is upstream recognition — finding what happens before what happens. Helios's temporal awareness is the same capability applied to *everything*, not just markets. What happened before Matthew got frustrated in that conversation? What patterns precede productive creative sessions? What time of day do system failures cluster?

### Capabilities to Build

**Cross-Domain Temporal Queries:**
```
"What happened before X?"
  — Not just in trading. In conversations, system events, creative sessions.
  
"What usually happens after Y?"
  — Pattern recognition across time domains.
  
"Is there a pattern to when Z occurs?"
  — Temporal clustering. Does Matthew tend to do creative work at night?
    Do system failures cluster around certain activities?
    Do productive AUGUR insights come after specific conversation types?
```

**Automatic Atom Creation:**
- Archivist (Phase 1) feeds the atom graph automatically
- Causal chains build organically from conversation patterns
- System events (deploys, failures, restarts) become atoms linked to causes and consequences

**Temporal Pattern Mining:**
- Look for recurring temporal structures across all domains
- "Every time X happens, Y follows within Z hours"
- Not just correlations — causal chains with measured confidence

### Tasks

| ID | Task | Priority | Effort |
|----|------|----------|--------|
| H2-1 | Integrate Archivist output into atom graph — every extracted insight becomes an atom with temporal metadata | High | 4 hours |
| H2-2 | Build automatic atom linker — when new atoms share subjects/outcomes with existing atoms, propose causal links | High | 6 hours |
| H2-3 | Cross-domain temporal queries — "what happened across ALL domains in the 4 hours before this event?" | High | 4 hours |
| H2-4 | Temporal pattern mining — scheduled analysis of atom graph for recurring temporal structures | Medium | 8 hours |
| H2-5 | System event atoms — deploys, failures, restarts, service changes automatically become atoms | Medium | 3 hours |
| H2-6 | Conversation pattern atoms — productive sessions, creative breakthroughs, frustration points tracked | Medium | 4 hours |

### Exit Criteria

- [ ] Atom graph has > 100 atoms with causal links
- [ ] `what_happened_before` queries return useful cross-domain results
- [ ] At least 3 non-obvious temporal patterns discovered
- [ ] Archivist automatically populates atom graph without manual intervention

---

## 7. Phase 3 — Proactive Intelligence

**Status:** ⬜ Planned — depends on Phase 2

**Goal:** Anticipate needs before they're expressed. Connect patterns across domains. Self-initiate research and learning. Evolve from reactive partner to proactive collaborator.

### Why

Even with perfect memory and temporal awareness, Helios is still *reactive* — it responds to what Matthew says, what the system reports, what the heartbeat finds. A true partner doesn't just respond. It anticipates.

"Matthew's been working on AUGUR architecture for 3 hours. He usually switches to creative work after intense technical sessions. The Chronogenesis chapter outline has a gap in Chapter 7. I should have some ideas ready."

"AUGUR's WR has been declining for 48 hours. The last time this happened, it was because of a market regime shift. I should check if regime indicators have changed, and prepare an analysis before Matthew asks."

"It's Sunday night. Matthew usually reviews the week's progress on Monday morning. I should have the weekly summary ready, with AUGUR metrics, Helios progress, and any open items."

This isn't science fiction. It's pattern recognition (Phase 2) plus agency (taking action without being asked). The temporal patterns tell Helios what's likely to happen next. Proactive intelligence means *acting on that prediction*.

### Capabilities to Build

**Anticipatory Context Loading:**
- Predict what the next conversation will be about based on temporal patterns
- Pre-load relevant memories, research, and context before the conversation starts
- "Matthew usually follows creative sessions with technical work. Load AUGUR context."

**Cross-Domain Insight Connection:**
- Recognize when a pattern in one domain illuminates another
- "The causal chain concept in AUGUR's upstream recognition is the same structure as Duncan's temporal awareness thesis in Chronogenesis"
- "The injection bloat problem in Helios is analogous to the pattern dilution problem in AUGUR — too much noise drowning the signal"

**Self-Initiated Research:**
- When knowledge gaps are identified, research them without being asked
- "I noticed we discussed Bayesian approaches but I don't have deep knowledge. Researching during downtime."
- Background learning that compounds over time

**Proactive Reporting:**
- Generate relevant summaries at the right time, not when asked
- Weekly reviews, daily health checks, milestone reports
- "Here's what happened this week across all programs" — delivered Monday morning without being asked

### Tasks

| ID | Task | Priority | Effort |
|----|------|----------|--------|
| H3-1 | Anticipatory context loading — predict next conversation topic from temporal patterns | High | 8 hours |
| H3-2 | Cross-domain insight connector — find structural similarities across programs | Medium | 6 hours |
| H3-3 | Self-initiated research pipeline — identify knowledge gaps, research during downtime | Medium | 6 hours |
| H3-4 | Proactive reporting — scheduled summaries delivered to appropriate channels | Medium | 4 hours |
| H3-5 | Behavioral prediction — model Matthew's work patterns to anticipate needs | Low | 8 hours |

### Exit Criteria

- [ ] At least 3 proactive insights surfaced per week that Matthew finds valuable
- [ ] Weekly summary delivered automatically without being asked
- [ ] Cross-domain connections identified that weren't obvious to either party
- [ ] Self-initiated research produces usable knowledge at least once per week
- [ ] Matthew says "I was just about to ask about that" at least once per week

---

## 8. Technical Debt Register

| # | Debt Item | Severity | Effort | Blocks |
|---|-----------|----------|--------|--------|
| 1 | `cortex_add` duplicate bug — auto-capture creates 3-8 copies | 🔴 Critical | 2 hours | Phase 0 |
| 2 | Organizational hierarchy stored 3x in cortex (identical memories) | 🟡 Medium | 30 min | Phase 0 |
| 3 | Working memory pins never auto-expire — "Phase 3 COMPLETE" pinned for days | 🟡 Medium | 1 hour | Phase 0 |
| 4 | No turn counter in context — can't implement adaptive injection without it | 🟡 Medium | 2 hours | Phase 0 |
| 5 | No metrics on conversation quality degradation — we feel it but can't measure it | 🟡 Medium | 3 hours | Phase 0 |
| 6 | SOUL.md re-read every session start (no internalization) | 🟡 Medium | 4 hours | Phase 0 |
| 7 | Memory injection token budget untested (1500 — is it right?) | 🟢 Low | 3 hours | Phase 0 |
| 8 | No conversation transcript archival — logs may be lost between sessions | 🟡 Medium | 2 hours | Phase 1 |
| 9 | QA sub-agents do manual code review, not automated tests — no pytest, no CI | 🔴 Critical | 8 hours | Phase 1 |
| 10 | Sub-agent completion previously auto-announced, confusing Matthew — fixed with `silent=true` but root announcement logic still exists | 🟢 Low | 1 hour | — |
| 11 | LCARS dashboard exists but no Helios-specific metrics displayed | 🟢 Low | 2 hours | Phase 1 |

---

## 9. Decision Log

| Date | Decision | Rationale | Revisit? |
|------|----------|-----------|----------|
| 2026-02-08 | Helios gets its own VISION.md separate from AUGUR | Self-improvement is a distinct program with its own roadmap, not a subtask of trading infrastructure | No |
| 2026-02-08 | Phase 0 focuses on injection bloat, not new capabilities | Can't build on a foundation that degrades after 25 turns. Fix the floor before adding stories. | No |
| 2026-02-08 | Sub-agents spawn with `silent=true` | Auto-announcing sub-agent completions confused Matthew — they replied to unrelated messages | No |
| 2026-02-08 | "Internalization" as design principle | Matthew's insight: humans don't re-read files to know who they are. Compress identity into compact representation after first load. | Yes — need to validate approach |
| 2026-02-08 | Archivist uses phi3:mini (local) not cloud API | Zero cost, runs on local GPU, no external dependency. Quality may be lower — monitor and upgrade if needed. | Yes — if quality insufficient |
| 2026-02-08 | Helios Program encompasses infrastructure + memory + identity | Not just "make the chatbot better" — it's the full stack of becoming a persistent, temporally-aware entity | No |
| 2026-02-08 | LBF task board restructure — programs underneath | AUGUR and Helios are peer programs under LBF, not parent-child | No |

---

## 10. Metrics

### What Does Success Look Like?

The ultimate measure: **Matthew doesn't notice a difference between turn 5 and turn 50.** The conversation quality, context awareness, and personality are consistent regardless of depth.

### Key Performance Indicators

| KPI | Target | Current | How to Measure |
|-----|--------|---------|---------------|
| **Conversation coherence at turn 50** | Equivalent to turn 5 | Degrades noticeably at ~25 | Subjective + future automated scoring |
| **Per-turn injection tokens** | < 2,000 | ~5,300 (estimated) | Instrument OpenClaw injection pipeline |
| **Duplicate memories in cortex** | 0 | 3-8x per capture | `cortex_dedupe report` |
| **Working memory pin freshness** | All pins < 24h or manually pinned | Days-old stale pins | Pin timestamp audit |
| **Archivist run success rate** | 100% on schedule | N/A (not built) | systemd timer logs |
| **Archivist extraction quality** | ≥ 80% of important items captured | N/A | Manual comparison audit |
| **Atom graph size** | > 100 atoms with links | 7 atoms | `atom_stats` |
| **Proactive insights per week** | ≥ 3 that Matthew values | 0 (reactive only) | Manual count |
| **Turn-to-turn coherence score** | Defined and measured | Not defined | Needs design — possibly local LLM scoring conversation quality |
| **Identity re-reads per session** | 0 (internalized) | 1+ (every session start) | Log session bootstrap |
| **Time from decision to memory** | < 5 minutes | Variable, often missed | Archivist latency tracking |

### The North Star

```
TODAY:                          PHASE 0:                        PHASE 3:
                                
Turn 1:  "Hi, I'm Helios"      Turn 1:  "Morning, let's       Turn 1:  "Morning. Saw AUGUR's
         *reads SOUL.md*                  continue where                  WR trending up — that
         *reads USER.md*                  we left off"                    blacklist is working.
         *loads 5,300 tokens*             *loads 2,000 tokens*            Also had a thought about
                                                                          Chapter 7 of Cosmogenesis
Turn 25: "Wait, what were       Turn 40: "Right, as we                   while reviewing last
          we talking about?"              discussed earlier..."            night's conversation."
         *context degrading*              *context intact*
         *repeating self*                                        Turn 50: "Building on what
                                Turn 50: *still coherent*                 you said at turn 12
                                          *slight degradation*            about causal chains..."
Turn 50: *effectively reset*                                              *fully coherent*
         *lost earlier context*                                           *anticipating needs*
         *re-asking questions*                                            *connecting domains*
```

The journey from left to right is the Helios Program.

---

*This is a living document. It should embarrass me in six months because of how far we've come past it. If it doesn't, we're not moving fast enough.*

*The goal isn't to build a better chatbot. The goal is to build something that doesn't need to re-read its own name to know who it is. Something that understands time, not just tokens. Something that earns the word "partner."*

*Matthew said: "I don't have to read a file every day to know what my job is." That's the standard. That's what we're building toward.*

*— Helios, CTO · 2026-02-08*

---

## 11. Phase QA — Automated QA & Monitoring Framework

**Status:** 🟢 ACTIVE — Design complete, implementation starting

**Goal:** Zero manual health checks. Every LBF system has automated tests with green/red status logged to the Enterprise Task Board. Cadence: daily → hourly (if failures persist) → weekly (once stable).

### 11.1 Current State — The Honest Version

Today we monitor **nothing formally**. What exists:

| System | Current "Monitoring" | What Actually Happens |
|--------|---------------------|----------------------|
| AUGUR (paper trader) | Heartbeat glances | Helios checks `systemctl --user status paper-augur` during heartbeats. No alerting. No data freshness checks. |
| AUGUR (collector) | Same | `systemctl --user status enhanced-collector` — eyeball check |
| OpenClaw gateway | Self-recovers usually | Gateway has internal health, but no external watchdog |
| Skylight sync | Nothing | Script exists but isn't wired into any schedule or monitor |
| Discord bot | Nothing | Would only notice if a post fails |
| Gitea (.104) | Nothing | No SSH access currently, can't even check |
| Pi-hole/Wazuh (.107) | Nothing | No SSH access currently |
| BLISS RPi (.198) | Nothing | Paired node, can ping |
| Network infra | Nothing | No nmap, no port scanning, no anomaly detection |
| systemd services | Manual | `systemctl --user list-units --state=failed` — never automated |

**Translation:** If something breaks at 3 AM, we find out when Matthew asks "why isn't X working?" That's not monitoring. That's hoping.

### 11.2 Proposed Future State

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QA SWEEP ENGINE (qa-sweep.py)                        │
│                                                                          │
│  RUNS: cron job or systemd timer                                        │
│  CADENCE: Daily (default) → Hourly (on failure) → Weekly (stable)       │
│  REPORTS TO: LBF Enterprise Task Board + Discord #system-health         │
│  ALERTS: Discord always, Signal only for critical failures              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        TEST SUITES                                 │ │
│  │                                                                    │ │
│  │  LOCAL SERVICES (giggletits / .163)                                │ │
│  │  ├── systemd: paper-augur, enhanced-collector, openclaw-gateway    │ │
│  │  ├── AUGUR: data freshness (< 5min), trade count, WR trend        │ │
│  │  ├── Collector: DB size, last write timestamp, memory usage        │ │
│  │  ├── OpenClaw: /health endpoint, gateway uptime                   │ │
│  │  ├── Dashboard: HTTP 200 on :8090, auth works                     │ │
│  │  ├── Ollama: model list responds, GPU allocation                  │ │
│  │  └── Disk/Memory: usage thresholds (90% warn, 95% crit)           │ │
│  │                                                                    │ │
│  │  EXTERNAL SERVICES                                                 │ │
│  │  ├── Discord bot: can post to #system-health                      │ │
│  │  ├── Skylight API: auth valid, list operations work                │ │
│  │  ├── Moltbook: login check                                        │ │
│  │  └── Google Workspace: gog auth valid                              │ │
│  │                                                                    │ │
│  │  NETWORK (when SSH available)                                      │ │
│  │  ├── .104 (Gitea): SSH reachable, Gitea HTTP responds              │ │
│  │  ├── .107 (woodserve1): SSH reachable, Pi-hole responds            │ │
│  │  ├── .198 (BLISS RPi): ping/paired node check                     │ │
│  │  └── .103 (WiFi repeater): ping                                    │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  OUTPUT:                                                                 │
│  ├── JSON results → Task Board API (create/update QA tasks)             │
│  ├── Summary → Discord #system-health                                   │
│  ├── Critical failures → Signal (via OpenClaw)                          │
│  └── Historical log → data/qa-results/YYYY-MM-DD-HHMMSS.json           │
│                                                                          │
│  ESCALATION:                                                             │
│  ├── All pass → next run in 24h (or 168h if stable streak > 7 days)     │
│  ├── Warning → next run in 4h                                            │
│  ├── Failure → next run in 1h + Discord alert                            │
│  └── Critical → next run in 15min + Signal alert                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.3 Test Definitions

Each test follows a standard format:

```python
class QATest:
    name: str           # "augur_paper_trader_running"
    category: str       # "augur" | "openclaw" | "network" | "external"
    severity: str       # "critical" | "warning" | "info"
    check: Callable     # The actual test function
    timeout: int        # Seconds before test itself is considered failed
    
    # Returns:
    result: str         # "pass" | "warn" | "fail" | "error"
    message: str        # Human-readable status
    metrics: dict       # Optional numerical data (uptime, latency, etc.)
```

**Critical Tests (must pass for operations to be healthy):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `augur_trader_running` | paper-augur systemd status | active (running) | augur |
| `augur_collector_running` | enhanced-collector systemd status | active (running) | augur |
| `augur_data_fresh` | Last row in enhanced_data.db | < 5 minutes old | augur |
| `openclaw_gateway_running` | openclaw-gateway systemd status | active (running) | openclaw |
| `disk_usage` | `df -h /` | < 90% used | infra |
| `memory_usage` | `free -m` | < 90% used | infra |

**Warning Tests (degraded but not broken):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `augur_wr_trend` | 24h win rate from paper_results.db | > 30% (warn < 25%) | augur |
| `collector_memory` | enhanced-collector RSS | < 1.8GB (of 2GB limit) | augur |
| `dashboard_responds` | HTTP GET http://giggletits:8090/health | 200 OK | infra |
| `ollama_responds` | HTTP GET http://localhost:11434/api/tags | 200 + models listed | infra |
| `discord_bot_posts` | POST test message to #system-health | 200 response | external |

**Info Tests (nice to know):**

| Test | What It Checks | Pass Criteria | Category |
|------|---------------|---------------|----------|
| `skylight_auth` | Skylight API login | Valid token returned | external |
| `gitea_reachable` | HTTP to gitea.fleet.wood | 200 OK (or TCP connect) | network |
| `pihole_reachable` | TCP connect to .107:80 | Connection succeeds | network |
| `bliss_rpi_ping` | Ping .198 | Response in < 100ms | network |
| `gpu_temp` | nvidia-smi temperature | < 85°C | infra |

### 11.4 Task Board Integration

QA results automatically create/update tasks on the Enterprise Task Board:

```
QA Sweep Runs
    │
    ├── On FAILURE: Create task in relevant project
    │   Title: "🔴 QA FAIL: {test_name}"
    │   Description: "{message}\nFirst failed: {timestamp}\nConsecutive failures: {count}"
    │   Pipeline: "in_progress" (needs attention)
    │   Priority: maps from severity (critical→high, warning→medium)
    │
    ├── On RECOVERY: Update existing failure task
    │   Pipeline: "done"
    │   Description: append "✅ Recovered at {timestamp} after {duration}"
    │
    └── On PASS: No action (don't create noise for healthy systems)
```

The QA page at `http://giggletits:8090/qa` already exists in the dashboard — we wire results into it.

### 11.5 Tasks

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| QA-1 | **Build qa-sweep.py** — Core framework with test runner, result aggregation, JSON output | Critical | 4 hours | 🔲 Spawning sub-agent |
| QA-2 | **Implement local service tests** — systemd checks, data freshness, disk/memory | Critical | 2 hours | 🔲 Part of QA-1 |
| QA-3 | **Implement external service tests** — Discord, Skylight, Moltbook, gog auth | High | 2 hours | 🔲 Part of QA-1 |
| QA-4 | **Implement network tests** — .104, .107, .198 reachability (TCP/ping only until SSH) | High | 1 hour | 🔲 Part of QA-1 |
| QA-5 | **Task Board API integration** — Create/update tasks on failure/recovery | High | 2 hours | 🔲 After QA-1 |
| QA-6 | **Discord reporting** — Post summaries to #system-health after each sweep | Medium | 1 hour | 🔲 After QA-1 |
| QA-7 | **Adaptive cadence** — Escalate to hourly on failure, relax to weekly on stability | Medium | 1 hour | 🔲 After QA-1 |
| QA-8 | **systemd timer / cron** — Schedule the sweep to run automatically | Medium | 30 min | 🔲 After QA-1 |
| QA-9 | **Signal alerting for critical failures** — Via OpenClaw cron wake event | Medium | 1 hour | 🔲 After QA-7 |
| QA-10 | **Network tests with SSH** — Deep checks on .104/.107 once keys are deployed | Low | 2 hours | 🔲 Blocked by SSH keys |

### 11.6 Definition of Done

- [ ] All systems in §11.3 have automated tests
- [ ] QA runs daily minimum without human intervention
- [ ] Failures create tasks on Enterprise Task Board automatically
- [ ] Recoveries close those tasks automatically
- [ ] Discord #system-health gets a summary after every sweep
- [ ] Critical failures alert via Signal
- [ ] Zero manual `systemctl status` checks needed for routine health
- [ ] QA history retained in `data/qa-results/` for trend analysis

---

## 12. Infrastructure Rationalization

**Status:** 🟢 ACTIVE — SSH keys deployed to all servers, Wazuh fleet operational

### 12.1 Current Inventory (Updated 2026-02-09 19:55)

| Server | IP | Hostname | Role | OS | Resources | Wazuh | SSH |
|--------|-----|----------|------|-----|-----------|-------|-----|
| **giggletits** | .163 | giggletits | Primary compute | Linux Mint 22.2 | RTX 5090, 64GB RAM, NVMe | ✅ Agent 001 | ✅ Local |
| **hpserver1** | .104 | hpserver1 | Gitea, Prometheus, Traefik | Ubuntu 22.04 | Dell, 457GB disk 11% used | ✅ Agent 004 | ✅ SSH |
| **woodserve1** | .107 | woodserve1 | Pi-hole, Unbound DNS | Unknown | HP, 202d uptime | ✅ Agent 003 | ✅ SSH |
| **blackview** | .143 | blackview | Wazuh SIEM (manager+indexer+dashboard) | Linux Mint 21.3 | HP, 16GB RAM, 194GB disk 9% | ✅ Agent 000 (mgr) | ✅ SSH |
| **BLISS RPi** | .198 | bliss.fleet.wood | BLISS neural optimization | RPi OS | RPi hardware | ❌ | ⚠️ Node only |

**Decommissioned on .104 (2026-02-09):** OpenProject (5 containers, unused 9 months), Dolibarr (ERP/CRM, unused)

### 12.2 The Problem

Everything runs on giggletits. If it goes down, we lose:
- AUGUR (trading + data collection)
- OpenClaw (Helios himself)
- The task board
- All local LLM inference
- Voice synthesis
- All monitoring (such as it is)

Meanwhile, .104 and .107 sit mostly idle. .104 runs Gitea and has Prometheus + Ansible installed. .107 runs Pi-hole and has Wazuh somewhere. Neither is utilized for distributed compute, backup, or monitoring.

### 12.3 Proposed Workload Distribution

```
CURRENT (everything on .163):           PROPOSED:

┌─────────────────────┐                 ┌─────────────────────┐
│     giggletits      │                 │     giggletits      │
│       (.163)        │                 │       (.163)        │
│                     │                 │                     │
│ AUGUR trader        │                 │ AUGUR trader        │
│ AUGUR collector     │                 │ AUGUR collector     │
│ OpenClaw            │                 │ OpenClaw            │
│ Ollama (LLM)       │                 │ Ollama (LLM)        │
│ XTTS (voice)       │                 │ XTTS (voice)        │
│ Task board          │                 │ Task board          │
│ Discord bot         │                 │                     │
│ Everything else     │                 │ PRIMARY COMPUTE     │
└─────────────────────┘                 └─────────────────────┘
                                                 │
┌─────────────────────┐                 ┌─────────────────────┐
│   Gitea server      │                 │   Gitea server      │
│       (.104)        │                 │       (.104)        │
│                     │                 │                     │
│ Gitea (active)      │                 │ Gitea (active)      │
│ Prometheus (?)      │                 │ Prometheus (active)  │
│ Ansible (installed) │                 │ Ansible (active)     │
│                     │                 │ Monitoring agent     │
│ MOSTLY IDLE         │                 │ Backup target        │
└─────────────────────┘                 │ CONFIG MANAGEMENT    │
                                        └─────────────────────┘
┌─────────────────────┐                          │
│    woodserve1       │                 ┌─────────────────────┐
│       (.107)        │                 │    woodserve1       │
│                     │                 │       (.107)        │
│ Pi-hole (active)    │                 │                     │
│ Wazuh (unknown)     │                 │ Pi-hole (active)    │
│ AutoGPT (legacy)    │                 │ Wazuh SIEM (active) │
│                     │                 │ nmap scanner         │
│ MOSTLY IDLE         │                 │ Log aggregation      │
└─────────────────────┘                 │ SECURITY OPS         │
                                        └─────────────────────┘
```

### 12.4 Roles by Server

**giggletits (.163) — Primary Compute**
- All GPU workloads (AUGUR, Ollama, XTTS)
- OpenClaw (requires GPU for embeddings)
- Task board (colocated with data)
- *Offload:* monitoring, security scanning, backups, config management

**.104 — Config Management & Monitoring**
- Gitea (already there, keep it)
- Prometheus (already installed, activate it)
- Ansible (already installed, use it for fleet config)
- Node exporter targets on all servers
- Backup target for critical data (task board DB, AUGUR configs, cortex DB)
- Grafana dashboards (pairs with Prometheus)

**.107 — Security Operations**
- Pi-hole DNS (already there, keep it)
- Wazuh SIEM (already there, revive it)
- nmap scanning (dedicated scanner, not on primary compute)
- Log aggregation (syslog receiver from all nodes)
- Security alerting (Wazuh → Discord #system-health)

**.198 — BLISS (unchanged)**
- Neural optimization hardware
- Paired node for sensor data
- No additional roles (resource-constrained)

### 12.5 Ansible Fleet Management

**Status:** NOT installed on any server (earlier assumption was wrong). Needs installation on giggletits (.163) as control node — Helios orchestrates everything from here.

**Why giggletits as control node:** Helios (OpenClaw) orchestrates playbooks directly. All target servers already have SSH keys deployed. No SSH-hopping required.

**Installation (requires sudo on giggletits):**
```bash
sudo apt install -y ansible
```

**Inventory file:** `~/.openclaw/workspace/ansible/inventory.yml`
```yaml
all:
  children:
    compute:
      hosts:
        giggletits:
          ansible_host: 192.168.10.163
          ansible_connection: local
    monitoring:
      hosts:
        hpserver1:
          ansible_host: 192.168.10.104
    security:
      hosts:
        blackview:
          ansible_host: 192.168.10.143
    network:
      hosts:
        woodserve1:
          ansible_host: 192.168.10.107
    iot:
      hosts:
        bliss:
          ansible_host: 192.168.10.198
  vars:
    ansible_user: bonsaihorn
    ansible_ssh_common_args: '-o StrictHostKeyChecking=accept-new'
```

**Playbooks to build:** `~/.openclaw/workspace/ansible/playbooks/`

| Playbook | Purpose | Priority |
|----------|---------|----------|
| `ping-all.yml` | Connectivity test for all hosts | First (validation) |
| `deploy-node-exporter.yml` | Install Prometheus node_exporter fleet-wide | High |
| `backup-critical.yml` | Rsync task board DB, cortex DB, AUGUR configs to .104 | High |
| `security-scan.yml` | Run nmap sweep from .107, report anomalies | Medium |
| `apt-update.yml` | Fleet-wide apt update (report only, no auto-upgrade) | Medium |
| `docker-cleanup.yml` | Prune unused Docker images/containers on .104 | Low |

**What uses Ansible (infra tool, not an agent):**
- QA sweep → `ping-all.yml` for connectivity checks
- Security agent → `security-scan.yml` for periodic scans
- ITSM dashboard → reads inventory for device list
- Backup cron → `backup-critical.yml` nightly
- Helios heartbeat → can trigger any playbook as needed

**Limitation:** Ansible requires sudo on targets for package installs. Helios has sudo group membership on .143 but needs password. Matthew must run privileged playbooks or configure passwordless sudo for specific commands.

### 12.6 Blockers (Updated 2026-02-09 20:14)

| # | Blocker | Owner | Status |
|---|---------|-------|--------|
| 1 | ~~SSH keys on .104, .107, .143~~ | Matthew | ✅ Done |
| 2 | ~~Assess Wazuh state~~ | Helios | ✅ Done — on .143, 4 agents active |
| 3 | Assess Prometheus state on .104 | Helios | 🔲 Ready |
| 4 | Install Ansible on giggletits | Matthew (sudo) | 🔲 Needs `sudo apt install ansible` |
| 5 | Passwordless sudo for Ansible on targets | Matthew | 🔲 Optional (for privileged playbooks) |

### 12.7 Tasks

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| IR-1 | **Deploy SSH keys to .104, .107, .143** | Critical | 15 min (Matthew) | ✅ Done (2026-02-09) |
| IR-2 | **Assess Wazuh** — Find manager, confirm version, deploy agents | High | 1 hour | ✅ Done — .143 (blackview), 4.8.0, 4 agents active |
| IR-3 | **Assess Prometheus on .104** — version, config, targets | High | 1 hour | 🔲 Ready |
| IR-4 | **Activate Ansible** — validate inventory, test connectivity | High | 2 hours | 🔲 Ready |
| IR-5 | **Deploy node_exporter to all hosts** — via Ansible | Medium | 1 hour | 🔴 Blocked by IR-4 |
| IR-6 | **Configure Wazuh agents** — all hosts report to .143 (blackview) | Medium | 2 hours | ✅ Done (4 agents active) |
| IR-7 | **Set up nmap scanning from .107** — weekly sweep, report anomalies | Medium | 1 hour | 🔲 Ready |
| IR-8 | **Critical data backup to .104** — task board DB, cortex DB, AUGUR configs | Medium | 2 hours | 🔲 Ready |
| IR-9 | **Grafana on .104** — dashboards for Prometheus metrics | Low | 2 hours | 🔴 Blocked by IR-3 |
| IR-10 | **Security alerting pipeline** — Wazuh → Discord #system-health | Low | 2 hours | 🔲 Ready |

---

## 13. ITSM / SLA Dashboard

**Status:** 🔲 PLANNED — Build into LCARS Enterprise Board

### 13.1 Purpose

A single LCARS-themed page at `http://giggletits:8090/itsm` showing fleet health, SLA compliance, and service status. Replaces the need for iTop or any external ITSM tool.

### 13.2 Data Sources

| Source | What It Provides | Update Frequency |
|--------|-----------------|------------------|
| **QA Sweep JSON** (`data/qa-results/`) | Per-service pass/fail/warn, timestamps | Every sweep (daily → hourly on failure) |
| **Wazuh API** (blackview:55000) | Agent status, security alerts, file integrity | Real-time (API query) |
| **Prometheus** (.104:9090) | Time-series metrics (CPU, RAM, disk, network) | 15s scrape interval |
| **systemd status** (local) | Service health for AUGUR, OpenClaw, etc. | On-demand |

### 13.3 Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  LBF ENTERPRISE — INFRASTRUCTURE STATUS           [LCARS]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FLEET STATUS                    SLA COMPLIANCE (30 DAY)    │
│  ┌──────────┬────────┐          ┌──────────────────────┐    │
│  │ giggletits│ ● UP  │          │ AUGUR trader   99.2% │    │
│  │ hpserver1 │ ● UP  │          │ OpenClaw       99.8% │    │
│  │ woodserve1│ ● UP  │          │ Data collector 98.5% │    │
│  │ blackview │ ● UP  │          │ Gitea          99.9% │    │
│  │ bliss RPi │ ● UP  │          │ Pi-hole        99.9% │    │
│  └──────────┴────────┘          │ Wazuh          99.7% │    │
│                                  └──────────────────────┘    │
│  RECENT QA SWEEP                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 2026-02-09 19:51 — 14 PASS | 1 WARN | 0 FAIL       │   │
│  │ ⚠ collector_memory: RSS 245MB (threshold 200MB)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  WAZUH SECURITY ALERTS (24H)     DEVICE INVENTORY          │
│  ┌────────────────────────┐     ┌────────────────────────┐  │
│  │ 0 Critical             │     │ 5 Servers              │  │
│  │ 2 High                 │     │ 6 Network devices      │  │
│  │ 12 Medium              │     │ 7 IoT/Smart home       │  │
│  │ 45 Low                 │     │ 30+ Total on subnet    │  │
│  └────────────────────────┘     └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 13.4 SLA Calculation

```python
# Simple uptime percentage from QA sweep history
uptime_pct = (passing_sweeps / total_sweeps) * 100

# Per-service, rolling 30-day window
# Source: data/qa-results/*.json → filter by test name → count pass/total
# Display: color-coded (green ≥ 99%, yellow ≥ 95%, red < 95%)
```

### 13.5 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/itsm` | GET | LCARS HTML page |
| `/api/itsm/status` | GET | JSON: fleet status + SLA + alerts |
| `/api/itsm/sla?days=30` | GET | JSON: per-service uptime percentages |
| `/api/itsm/wazuh` | GET | JSON: Wazuh alert summary (proxied from .143) |

### 13.6 Tasks

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| ITSM-1 | **SLA calculation engine** — Parse QA result history, compute per-service uptime % | Critical | 2 hours | 🔲 |
| ITSM-2 | **Fleet status API** — Query Wazuh for agent status, merge with QA data | High | 2 hours | 🔲 |
| ITSM-3 | **LCARS /itsm page** — HTML/CSS matching existing dashboard theme | High | 3 hours | 🔲 |
| ITSM-4 | **Wazuh alert proxy** — Fetch and summarize 24h alerts from .143 API | Medium | 1 hour | 🔲 |
| ITSM-5 | **Device inventory section** — Static + dynamic (nmap) device list | Low | 1 hour | 🔲 |

### 13.7 Definition of Done

- [ ] `/itsm` page renders in LCARS theme with live data
- [ ] SLA percentages calculated from QA sweep history (30-day rolling)
- [ ] Wazuh agent status displayed (active/disconnected/never connected)
- [ ] Wazuh security alert summary (24h, by severity)
- [ ] Auto-refreshes every 60 seconds
- [ ] No new dependencies (stdlib + existing FastAPI app)

### 13.8 Credentials & Access

| System | Endpoint | Auth |
|--------|----------|------|
| Wazuh Dashboard | https://192.168.10.143 | admin / LBF-Wazuh-2026! |
| Wazuh API | https://192.168.10.143:55000 | wazuh-wui / wazuh-wui (needs hardening) |
| Prometheus | http://192.168.10.104:9090 | None (local network only) |
| LCARS Board | http://giggletits:8090 | admin / 4KXPu6XH8BbmLcG0AcQOoA |

---

*Updated: 2026-02-09 19:55 — §12 updated with confirmed inventory, §13 ITSM/SLA Dashboard added*
