# Turn Counter Usage Guide (H0-6)

## Overview

The turn counter tracks conversation depth per session, enabling adaptive context strategies. As a conversation deepens, less static context injection is needed — the model has already internalized it.

## Quick Start

```bash
# Increment and get current turn (call once per agent turn)
turn-counter "agent:main:main" 

# Check turn without incrementing
turn-counter "agent:main:main" --get

# Reset counter (new conversation or manual reset)
turn-counter "agent:main:main" --reset

# Set to specific value (e.g., after context window reset)
turn-counter "agent:main:main" --set 15
```

## Agent Integration

Call via `exec` at the start of each turn:

```
exec: turn-counter "agent:main:main"
```

The session ID should match the OpenClaw session identifier. For sub-agents, use their session ID (e.g., `agent:main:subagent:<uuid>`).

## Adaptive Strategy Tiers

### Turns 1–10: **Full Boot** (Cold Start)
- Load complete identity context (SOUL.md, AGENTS.md, USER.md)
- Full semantic memory injection
- All working memory pins active
- Cortex STM retrieval at maximum depth
- *Rationale: Model needs full grounding, hasn't internalized anything yet*

### Turns 11–30: **Warm Cruise**
- Reduce static file injection (skip TOOLS.md if no tool-heavy task)
- Rely on internalized identity from earlier turns
- Semantic memory: only inject if topic shifts
- Working memory: keep pins, reduce verbose context
- *Rationale: Core identity is internalized, focus tokens on task context*

### Turns 31–50: **Lean Mode**
- Minimal static injection (AGENTS.md safety rules only)
- Aggressive summarization of earlier conversation
- Cortex retrieval only on explicit recall need
- Consider trimming low-priority semantic memories
- *Rationale: Deep in conversation, context window is precious*

### Turns 50+: **Reset Advisory**
- Suggest proactive context reset to the user
- Dump all session learnings to Cortex before reset
- Run pre-reset sweep (AGENTS.md protocol)
- Pin critical in-progress items to working memory for next session
- *Rationale: Context window degradation is real — better to reset clean*

## Integration with H0-5 (Budget Tuning)

The turn counter feeds directly into context budget decisions:

```
Turn Count → Budget Tier → Token Allocation
  1-10     → full_boot   → max static + max semantic
  11-30    → warm_cruise  → reduced static, normal semantic  
  31-50    → lean_mode    → minimal static, selective semantic
  50+      → reset_advisory → trigger pre-reset sweep
```

When H0-5 budget tuning is implemented, the turn counter value will be one of the inputs to the budget calculator. The budget calculator can then dynamically adjust:

1. **Static file inclusion** — which workspace files to inject
2. **Semantic memory depth** — how many memories to retrieve
3. **Diverse context breadth** — whether to include cross-category memories
4. **Hot memory threshold** — minimum access count for inclusion

## File Locations

- **Script:** `~/bin/turn-counter`
- **Counter files:** `/tmp/helios-turn-count-<hash>` (auto-cleaned on reboot)
- **Timestamp files:** `/tmp/helios-turn-ts-<hash>` (idempotency tracking)

## Idempotency

The counter uses a timestamp guard — calling it twice within the same second returns the same count without double-incrementing. This prevents accidental double-counting if the agent retries a tool call.

## Session Detection

The counter is keyed by session ID. When OpenClaw starts a new session, the old `/tmp/` files from the previous session remain but are harmless (different session ID = different counter file). Files are cleaned up naturally on system reboot since they live in `/tmp/`.

For explicit cleanup: `turn-counter <session_id> --reset`
