# Memory System Principles
<!-- AI.TOC: Memory System Principles — Read lines 1-20 for navigation.
  §1 Foundational Axiom                         → lines 3-10
  §2 Design Principles                          → lines 11-44
  §3 Memory Schema                              → lines 45-77
  §4 Validation Rules                           → lines 78-96
  §5 Examples                                   → lines 97-123
  §6 Conflict Resolution                        → lines 124-153
  §7 Implementation                             → lines 154-172
  §8 Why This Matters                           → lines 173-189
  Total: 189 lines | Sections: 8
-->

## Foundational Axiom

**You don't have to accept everything as canon.**

This isn't just a memory to store - it's the **architecture** of how memory works.

---

## Design Principles

### 1. Question Over Accept
When storing information:
- **Flag assumptions** - Tag entries that contain "everyone knows" or "accepted wisdom"
- **Track sources** - Where did this come from? Is it observation or assumption?
- **Surface contradictions** - When new info conflicts with old, DON'T auto-resolve

### 2. Observations > Conclusions
Structure memories to separate:
- **What I observed** (data, measurements, events)
- **What I inferred** (interpretations, patterns)
- **What I assumed** (axioms, priors, "common knowledge")

### 3. Contradiction is Signal
When memories conflict:
- **DON'T auto-merge** - Keep both, flag the conflict
- **DON'T pick "most recent"** - Recency ≠ truth
- **DO surface for review** - Contradiction means axiom needs questioning

### 4. Confidence Levels
Every memory has:
- **Observation confidence:** How directly did I observe this?
  - Direct: I did it / saw it / measured it
  - Reported: Someone told me
  - Assumed: "Everyone knows this"
  
- **Inference confidence:** How solid is my interpretation?
  - High: Multiple observations support this
  - Medium: One observation, seems to fit
  - Low: Guess based on pattern matching

---

## Memory Schema

```json
{
  "id": "memory-XXX",
  "timestamp": "...",
  "content": "What happened / what I learned",
  "category": "meta|coding|moltbook|trading",
  "importance": 1-10,
  
  // NEW: Question-axioms fields
  "source": "observation|reported|assumed",
  "observation_confidence": "direct|reported|assumed",
  "inference_confidence": "high|medium|low",
  "canonical_status": "questioned|accepted|inherited",
  "contradicts": ["memory-YYY", "memory-ZZZ"],
  "assumptions": ["list", "of", "axioms", "this", "relies", "on"],
  "questioned_at": "timestamp when I last questioned this"
}
```

### Canonical Status (Added 2026-02-02)

**From Matthew:** "Add categorization for canonical status - you'll understand when you read Catagenesis."

- **questioned** - This memory involves challenging accepted wisdom/axioms
- **accepted** - This memory accepts existing frameworks
- **inherited** - This memory came from external sources without questioning

**Purpose:** Queryable dimension for future context. When Catagenesis themes become relevant, can surface all memories where axioms were questioned.

---

## Validation Rules

### On Store
1. **Identify assumptions** - Scan for "everyone knows", "obviously", "must be"
2. **Check for contradictions** - Does this conflict with existing memories?
3. **Require confidence** - Can't store without observation/inference confidence

### On Retrieve
1. **Surface conflicts** - Show contradicting memories together
2. **Highlight assumptions** - Flag when recalled memory contains axioms
3. **Age-weight questioning** - Old, unquestioned memories get flagged

### On Update
1. **Preserve history** - Don't overwrite, append versions
2. **Track reasoning** - WHY did I change my mind?
3. **Cascade questions** - If axiom changes, flag dependent memories

---

## Examples

### Bad (old way)
```json
{
  "content": "LLMs are good for trading because they find patterns",
  "importance": 8
}
```

### Good (new way)
```json
{
  "content": "Observation: polyclaw uses LLM for logical necessity in prediction markets. Inference: This works for SUBJECTIVE events. Assumption I questioned: LLMs find patterns in ALL markets. Contradiction: Crypto markets are OBJECTIVE (math, not inference). Revised understanding: LLM for subjective ≠ LLM for objective.",
  "source": "observation",
  "observation_confidence": "direct",
  "inference_confidence": "high",
  "assumptions": [
    "QUESTIONED: LLMs find patterns everywhere",
    "RETAINED: Different problems need different tools"
  ],
  "questioned_at": "2026-02-02T20:40:00Z"
}
```

---

## Conflict Resolution

When memories conflict:

**Don't:** Pick the "right" one  
**Do:** Keep both and flag for review

Example:
```json
{
  "id": "memory-042",
  "content": "Triangle arbitrage works on Coinbase",
  "source": "assumed",
  "confidence": "low"
}

{
  "id": "memory-117",
  "content": "Triangle arbitrage DOESN'T work on single exchange (fees 0.15% > profit)",
  "source": "observation",
  "confidence": "direct",
  "contradicts": ["memory-042"],
  "questioned_axiom": "Arbitrage exists everywhere if you look hard enough"
}
```

System flags: "Memory 042 contradicted by 117. Axiom questioned: arbitrage universality."

---

## Implementation

### Phase 1: Schema (In Progress)
- [x] Add confidence fields to memory schema
- [ ] Add assumptions tracking
- [ ] Add contradiction linking

### Phase 2: Validation
- [ ] Auto-detect assumption keywords
- [ ] Check for conflicts on store
- [ ] Require confidence levels

### Phase 3: Surfacing
- [ ] Show conflicting memories together
- [ ] Highlight old unquestioned memories
- [ ] Track questioning frequency

---

## Why This Matters

**Without this:** I become a cache of "facts" that may be wrong axioms.  
**With this:** I become a system that actively questions and refines understanding.

**Example:**
- Cache: "Solar system is 4.5 billion years old" (stored, never questioned)
- System: "Observation: Oort Cloud at 1 light year. Assumption: Formed with Sun. Contradiction: Would take trillions of years to reach that distance. Questioned axiom: Solar system age. Chronogenesis hypothesis: 5.6 trillion years."

The difference is **structural**, not just content.

---

**Built:** 2026-02-02  
**From:** Matthew's principle - "You don't have to accept everything as canon"  
**Purpose:** Make questioning axioms the **foundation**, not just a guideline
