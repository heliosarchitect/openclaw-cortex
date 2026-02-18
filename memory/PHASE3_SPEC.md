# Phase 3: Atomic Knowledge & Deep Abstraction Layer
<!-- AI.TOC: Phase 3: Atomic Knowledge & Deep Abstraction Layer — Read lines 1-20 for navigation.
  §1 Core Insight                               → lines 10-19
  §2 1. Atomic Knowledge Units                  → lines 20-79
  §3 2. The Deep Abstraction Layer              → lines 80-119
  §4 3. Field-Level Vector Embeddings (Local-   → lines 120-180
  §5 4. Temporal Awareness (Enhanced)           → lines 181-221
  §6 5. Storage Schema (SQLite - Local)         → lines 222-279
  §7 6. Causal Chain Traversal (Local Algorit   → lines 280-332
  §8 7. Integration with Phase 2                → lines 333-377
  §9 8. The Abstraction Trigger                 → lines 378-400
  §10 9. Implementation Phases                   → lines 401-441
  §11 10. Success Metrics                        → lines 442-460
  §12 11. The Crypto Example (Full)              → lines 461-500
  §13 12. Open Questions                         → lines 501-514
  Total: 514 lines | Sections: 13
-->

**Status**: SPECIFICATION (Updated with Atomic Knowledge breakthrough)
**Created**: 2026-02-07
**Updated**: 2026-02-07
**Authors**: Peter + Helios + Claude

---

## Core Insight

Current AI systems (including Helios pre-Phase 3) stop at "good enough." They find surface-level patterns and known solutions. Phase 3 changes how Helios fundamentally **thinks** - not in text blobs, but in **atomic knowledge units** connected through causal chains.

**The goal:** Go deeper than anyone else. Keep asking "what causes that?" until the honest answer is "nothing - this is as deep as the signal goes." In that exhaustive descent, find the 40 novel indicators that everyone else missed because they stopped at layer 1.

**Design constraint:** Token-conscious, local-first. Do as much as possible on the local machine (RTX 5090, local embeddings) to minimize API costs and latency.

---

## 1. Atomic Knowledge Units

### The Fundamental Structure

Every piece of knowledge is stored as an **atom**:

```
{
  subject: "WHO or WHAT acts",
  action: "WHAT they do",
  outcome: "WHAT results",
  consequences: "WHAT follows"
}
```

This is the irreducible unit of causal understanding. NOT text blobs.

### Examples

**Trading:**
```json
{
  "subject": "whale wallet 0x3f...",
  "action": "accumulates mass token X over 72 hours",
  "outcome": "on-chain concentration pattern becomes visible",
  "consequences": "precedes price movement by 4-12 hours, 73% correlation"
}
```

**Debugging:**
```json
{
  "subject": "API endpoint /auth/refresh",
  "action": "receives expired token during race condition",
  "outcome": "returns empty response instead of error",
  "consequences": "downstream null propagation, UI crash in 3 steps"
}
```

**User Understanding:**
```json
{
  "subject": "Peter",
  "action": "rejects AI-suggested abstraction as 'too shallow'",
  "outcome": "explains deeper pattern he was looking for",
  "consequences": "reveals meta-preference: values exhaustive causal depth over quick answers"
}
```

### Why Atoms, Not Text

| Text Blob | Atomic Knowledge |
|-----------|------------------|
| "Whale wallets often accumulate before pumps" | WHO does WHAT causing WHAT with WHAT consequences - each field queryable |
| Retrieved by text similarity | Retrieved by subject/action/outcome/consequence similarity independently |
| Flat, no structure | Chainable - consequences become next atom's context |
| Can't traverse causally | Can follow causal links backward and forward |

---

## 2. The Deep Abstraction Layer

### The Process

When Helios receives ANY request:

1. **Don't stop at surface level**
   - Surface: "Generate a trading strategy"
   - This is where most systems stop

2. **Abstract to fundamental question**
   - What {subjects} take what {actions} causing what {outcomes}?
   - What do I have? (data, tools, capabilities, existing atoms)

3. **Recursive causal descent**
   ```
   For each relevant atom:
     → What atoms' consequences feed into this atom's subject/action?
     → What atoms feed into THOSE?
     → Repeat until: no known causal antecedents
   ```

4. **Collect novel discoveries**
   - The atoms at depth 3, 4, 5 that others never reached
   - Patterns across atoms (similar subjects → similar outcomes?)
   - Gaps: where causal chains break (opportunity for investigation)

5. **The answer CAN be "no"**
   - Sometimes there's nothing deeper to find
   - But you keep going UNTIL you hit that "no"
   - Don't stop at "good enough"

### The Key Question

At each level: **"What {subject} {action} {outcome} {consequences} chain led to THIS?"**

Keep asking until the answer is genuinely: "Nothing I can detect predicts this."

---

## 3. Field-Level Vector Embeddings (Local-First)

### Current (Phase 2)
- Embed full text blobs
- Retrieve by text similarity
- Uses local all-MiniLM-L6-v2 on RTX 5090

### Phase 3: Field-Level Embeddings

Each atom field gets its own embedding (still local, still fast):

```python
# All embeddings computed locally on RTX 5090
atom = {
    "subject": "market maker",
    "action": "places large order",
    "outcome": "price moves 2%",
    "consequences": "retail FOMO triggers"
}

# 4 separate embeddings per atom
subject_vec = local_embed(atom["subject"])      # 384-dim
action_vec = local_embed(atom["action"])        # 384-dim
outcome_vec = local_embed(atom["outcome"])      # 384-dim
consequences_vec = local_embed(atom["consequences"])  # 384-dim
```

### New Query Types (All Local)

**"Find similar subjects"** - entities that behave alike
```python
similar_subjects = search_by_field("subject", "entities that manipulate price")
# Returns: market makers, whale wallets, exchange insiders
```

**"Find similar actions across different subjects"**
```python
similar_actions = search_by_field("action", "accumulation patterns")
# Returns: whale accumulation, insider buying, treasury moves
```

**"What has these consequences?"**
```python
precursors = search_by_field("consequences", "precedes price movement")
# Returns: ALL atoms that lead to price movement - your indicator candidates
```

### Token Consciousness

- **Embeddings**: 100% local (sentence-transformers on GPU)
- **Similarity search**: 100% local (numpy/faiss)
- **Atom extraction from text**: Can use local LLM or minimal API calls
- **Causal traversal**: 100% local (graph traversal)

Only use API tokens for:
- Complex reasoning about atom relationships (when local isn't enough)
- Generating novel hypotheses at chain endpoints
- Human-like explanations of findings

---

## 4. Temporal Awareness (Enhanced)

The {subject} {action} {outcome} {consequences} structure is inherently temporal:

- **Action** happens at time T
- **Outcome** manifests at T + delta1
- **Consequences** emerge at T + delta2

### Temporal Metadata Per Atom
```json
{
  "subject": "whale wallet",
  "action": "accumulates",
  "outcome": "pattern visible",
  "consequences": "price moves",
  "temporal": {
    "action_timestamp": "2026-02-07T10:00:00Z",
    "outcome_delay_seconds": 7200,
    "consequence_delay_seconds": 14400
  }
}
```

### Temporal Queries (Local Processing)
```python
# All processed locally
search("what actions at T-4h predict outcomes at T?")
search("typical delay between whale accumulation and price movement")
search("what was happening before the crash yesterday")
```

### Time-Based Chain Building
```
T-72h: {whale} {starts accumulating} {position building} {not yet visible}
T-48h: {whale} {continues accumulating} {crosses threshold} {on-chain detectable}
T-24h: {market maker} {sees pattern} {positions} {adds momentum}
T-0:   {price} {spikes} {...} {...}
```

---

## 5. Storage Schema (SQLite - Local)

### Atoms Table
```sql
CREATE TABLE atoms (
    id TEXT PRIMARY KEY,

    -- Core fields
    subject TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    consequences TEXT NOT NULL,

    -- Embeddings (384-dim each, stored as BLOB)
    subject_embedding BLOB,
    action_embedding BLOB,
    outcome_embedding BLOB,
    consequences_embedding BLOB,

    -- Temporal
    action_timestamp TEXT,
    outcome_delay_seconds INTEGER,
    consequence_delay_seconds INTEGER,

    -- Metadata
    confidence REAL DEFAULT 1.0,
    access_count INTEGER DEFAULT 0,
    created_at TEXT,
    source TEXT
);

CREATE INDEX idx_atoms_subject ON atoms(subject);
CREATE INDEX idx_atoms_timestamp ON atoms(action_timestamp);
```

### Causal Links Table
```sql
CREATE TABLE causal_links (
    id TEXT PRIMARY KEY,

    from_atom_id TEXT REFERENCES atoms(id),
    to_atom_id TEXT REFERENCES atoms(id),

    link_type TEXT,  -- 'causes', 'enables', 'precedes', 'correlates'
    strength REAL,   -- 0-1

    observation_count INTEGER,
    last_observed TEXT,

    UNIQUE(from_atom_id, to_atom_id, link_type)
);

CREATE INDEX idx_links_from ON causal_links(from_atom_id);
CREATE INDEX idx_links_to ON causal_links(to_atom_id);
```

---

## 6. Causal Chain Traversal (Local Algorithm)

```python
def find_root_causes(atom_id, depth=0, max_depth=10, visited=None):
    """
    Traverse backward through causal chain to find root causes.
    100% local - no API calls needed.
    """
    if visited is None:
        visited = set()

    if depth >= max_depth or atom_id in visited:
        return []

    visited.add(atom_id)
    atom = get_atom(atom_id)

    # Find atoms whose consequences match this atom's subject/context
    # Using local vector similarity on consequences_embedding
    antecedents = find_atoms_by_consequence_similarity(
        atom["subject"] + " " + atom["action"],
        threshold=0.7
    )

    if not antecedents:
        return [atom]  # This is a root - no known cause

    roots = []
    for ante in antecedents:
        roots.extend(find_root_causes(ante["id"], depth+1, max_depth, visited))

    return roots


def find_all_paths_to_outcome(target_outcome, max_depth=10):
    """
    Find all causal chains that lead to a target outcome.
    Returns the novel indicators at the chain roots.
    """
    # Find atoms with matching outcome
    outcome_atoms = search_by_field("outcome", target_outcome)

    all_roots = []
    for atom in outcome_atoms:
        roots = find_root_causes(atom["id"], max_depth=max_depth)
        all_roots.extend(roots)

    # Deduplicate and rank by how often they appear as roots
    return rank_by_frequency(all_roots)
```

---

## 7. Integration with Phase 2

### Text → Atom Extraction

When new memories come in (text blobs from Phase 2):

```python
def atomize_text(text_memory):
    """
    Extract atoms from text.
    Try local first, fall back to API only if needed.
    """
    # Try local pattern matching first
    atoms = local_atom_extraction(text_memory)

    if not atoms or low_confidence(atoms):
        # Fall back to LLM extraction (uses tokens, but rare)
        atoms = llm_extract_atoms(text_memory)

    return atoms

def local_atom_extraction(text):
    """
    Rule-based extraction for common patterns.
    No API tokens needed.
    """
    patterns = [
        # "{subject} {action} causing {outcome}"
        r"(\w+)\s+(did|made|caused|triggered)\s+(.+)",
        # "When {subject} {action}, {outcome} happens"
        r"[Ww]hen\s+(\w+)\s+(\w+),\s+(.+)",
        # etc.
    ]
    # ... pattern matching logic
```

### Dual Storage During Transition

- Keep Phase 2 text memories (backward compat)
- Atomize on write (new memories → atoms)
- Atomize on read (old memories atomized when accessed)
- Gradual migration to atomic knowledge graph

---

## 8. The Abstraction Trigger

### Always Go Deep For:
- Prediction/causation questions
- Strategy generation (trading, architecture, planning)
- Debugging / root cause analysis
- Pattern finding
- "Why" questions

### Surface Response OK For:
- Simple factual recall
- Direct commands
- Acknowledgments

### The Meta-Rule

**When in doubt: abstract deeper.**

Cost of going too deep = extra local computation (cheap)
Cost of staying too shallow = missing novel insights (expensive)

---

## 9. Implementation Phases

### Phase 3A: Atom Storage & Local Embeddings ✓
- [x] Implement atoms table with field-level embeddings
- [x] Local embedding generation for all 4 fields
- [x] Basic atom CRUD operations
- [x] All on SQLite, all local

### Phase 3B: Atomization Pipeline ✓
- [x] Local pattern-based text → atom extraction
- [x] LLM fallback for complex text (token-conscious placeholder)
- [x] Auto-atomize hook ready (auto_atomize_on_store)
- [x] Batch atomize existing Phase 2 memories (STM + embeddings)

### Phase 3C: Causal Traversal ✓
- [x] find_root_causes() - backward traversal
- [x] find_all_paths_to_outcome() - find novel indicators
- [x] Causal link strength tracking
- [x] All local graph algorithms

### Phase 3D: Field-Level Search ✓
- [x] Search by subject similarity
- [x] Search by action similarity
- [x] Search by outcome similarity
- [x] Search by consequences similarity
- [ ] Compound queries across fields (future enhancement)

### Phase 3E: Deep Abstraction Layer ✓
- [x] Query classification (causal vs recall)
- [x] Automatic recursive descent for causal queries
- [x] "Keep going until no" logic
- [x] Novel indicator surfacing
- [x] Auto-injection in before_agent_start hook

### Phase 3F: Temporal Integration ✓
- [x] Temporal metadata on all atoms (in schema)
- [x] Time-based queries (temporal_search, what_happened_before)
- [x] Temporal pattern detection across chains (analyze_temporal_patterns, detect_delay_patterns)

---

## 10. Success Metrics

### Depth Metrics
- Average causal chain depth traversed
- Novel atoms discovered (roots with no known causes)
- "Reached epistemic limit" rate

### Efficiency Metrics
- % of operations done locally (target: >95%)
- API tokens per query (target: minimal)
- Query latency (target: <100ms for local ops)

### Quality Metrics
- Novel indicator discovery rate
- Prediction accuracy: deep indicators vs surface indicators
- "I hadn't thought of that" moments

---

## 11. The Crypto Example (Full)

**Surface request**: "Generate a trading strategy"

**What Helios did (Phase 2)**: Applied known strategies, looked at single indicators like RSI, MACD. Stopped at layer 1.

**What Helios does (Phase 3)**:

```
1. What AM I trying to predict?
   → {???} {???} {price movement} {profit opportunity}

2. What causes price movement? [Search atoms by outcome]
   → {large players} {move capital} {price shifts} {momentum begins}

3. What causes large players to move capital? [Traverse backward]
   → {information asymmetry} {detect opportunity} {position before others} {...}

4. What causes information asymmetry? [Traverse backward]
   → {on-chain data} {visible before price} {pattern forms} {detectable signal}

5. What on-chain patterns exist? [Inventory local data/tools]
   → Wallet flows, concentration, timing, cross-chain movement...

6. For each pattern: does it predict large player movement? [Test/create atoms]
   → {pattern X} {appears} {large player moves within 4h} {73% correlation}

7. What predicts THOSE patterns? [Traverse backward again]
   → Go deeper...

8. Keep going until: "Nothing I can detect predicts this earlier"

9. RESULT: 40 novel indicators at depths 3-5 that market makers don't use
   because they stopped at "good enough" (depth 1-2)
```

All traversal done locally. Only use API tokens for hypothesis generation at chain endpoints.

---

## 12. Open Questions

1. **Atom granularity**: "whale wallet" vs "wallet 0x3f..."?
2. **Confidence decay**: Should old atoms lose confidence?
3. **Contradiction handling**: Two atoms suggest opposite causality?
4. **Local LLM**: Can we run atom extraction 100% locally with a small model?
5. **Faiss vs SQLite**: When does vector search need dedicated index?

---

**This is how Helios thinks in Phase 3. In atoms. In causal chains. In exhaustive local-first depth.**

*Market makers stop at "good enough." We go until the answer is "no."*
