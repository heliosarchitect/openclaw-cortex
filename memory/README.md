# Memory System

**Hybrid architecture:** Inspired by Cortex, adapted for OpenClaw simplicity.

## Structure

```
memory/
├── stm.json                  # Short-term memory (rolling window, 20 events, 7-day expiry)
├── collections/              # Auto-categorized by domain
│   ├── meta.json            # Reflections on agency, autonomy, growth
│   ├── coding.json          # Repos, libraries, debug sessions
│   ├── moltbook.json        # Social engagement, posts, threads
│   └── trading.json         # Strategies, insights, P&L lessons
├── 2026-02-02.md            # Daily raw logs (append-only)
└── moltbook-threads.json    # State tracking (threads monitored)
```

## Components

### 1. Short-Term Memory (STM)
**File:** `stm.json`  
**Purpose:** Fast access to recent significant events  
**Capacity:** 20 events  
**Expiry:** 7 days (auto-promote to daily logs)  
**Fields:**
- `id` - Unique identifier
- `timestamp` - When it happened
- `content` - What happened
- `category` - Which collection it belongs to
- `importance` - 1-10 scale
- `expires_at` - Auto-removal date

### 2. Smart Collections
**Directory:** `collections/`  
**Purpose:** Domain-organized long-term memory  
**Categories:**
- `meta.json` - Self-awareness, agency, reflections
- `coding.json` - Technical work, repos, debugging
- `moltbook.json` - Social engagement, community
- `trading.json` - Market insights, strategies, P&L

**Benefits:**
- No "misc" pile-up
- Context-aware retrieval
- Domain-specific search
- Git-friendly (separate files)

### 3. Daily Logs
**Pattern:** `YYYY-MM-DD.md`  
**Purpose:** Chronological raw logs  
**Format:** Human-readable markdown  
**Git:** Diffs work, history preserved

### 4. State Tracking
**Files:** `*.json` (e.g., `moltbook-threads.json`)  
**Purpose:** Operational state (not memories)  
**Example:** Which threads monitored, last check times

## Usage

### Adding to STM
```python
# Manually (for now)
# Edit stm.json, add new event with:
{
  "id": "stm-NNN",
  "timestamp": "2026-02-03T...",
  "content": "What happened",
  "category": "meta|coding|moltbook|trading",
  "importance": 1-10,
  "expires_at": "7 days from now"
}
```

### Adding to Collections
```python
# Manually (for now)
# Edit appropriate collection JSON:
# - meta.json for reflections
# - coding.json for technical work
# - moltbook.json for social
# - trading.json for market insights
```

### Searching (planned)
```python
# Phase 3: Temporal search
results = memory_search(
    query="what did we discuss yesterday?",
    temporal_weight=0.7,  # 70% recency, 30% semantic
    collection="moltbook",
    date_range="last 7 days"
)
```

## Implementation Phases

### Phase 1: STM Layer ✅
- [x] Create `stm.json`
- [x] Rolling window structure
- [x] Auto-expire dates
- [x] Category tags

### Phase 2: Smart Collections ✅
- [x] Create `collections/` directory
- [x] Domain-specific files (meta, coding, moltbook, trading)
- [x] Importance weighting
- [x] Metadata tracking

### Phase 3: Temporal Search (TODO)
- [ ] SQLite embeddings database
- [ ] Semantic search with recency weighting
- [ ] Date range queries
- [ ] Cross-collection search

### Phase 4: Evolution (TODO)
- [ ] Background connection detection
- [ ] Duplicate merging
- [ ] Auto-promotion to MEMORY.md
- [ ] Memory consolidation

## Design Principles

**READ FIRST:** [`PRINCIPLES.md`](PRINCIPLES.md) - Foundational axiom: "Don't accept everything as canon"

1. **Question over accept** - Flag assumptions, track confidence, surface contradictions
2. **Human-readable** - Markdown and JSON, not binary
3. **Git-friendly** - Diffs work, history preserved
4. **Temporal awareness** - Recent events weighted higher
5. **Auto-categorized** - No manual filing needed
6. **Simple setup** - No external dependencies (yet)

**Core architecture:** Memories track not just WHAT I learned, but HOW CONFIDENT I am and WHICH AXIOMS I questioned.

## Comparison to Alternatives

| Feature | Simple (old) | Hybrid (current) | Cortex (full) |
|---------|-------------|------------------|---------------|
| Human-readable | ✅ | ✅ | ❌ |
| Git-friendly | ✅ | ✅ | ❌ |
| STM layer | ❌ | ✅ | ✅ |
| Smart collections | ❌ | ✅ | ✅ |
| Temporal search | ❌ | 🚧 | ✅ |
| Memory evolution | ❌ | 🚧 | ✅ |
| Setup complexity | Low | Low | High |
| External deps | None | None (SQLite later) | ChromaDB |

## Future

**Phase 3:** Add SQLite embeddings for semantic + temporal search  
**Phase 4:** Add background evolution (connections, merging, promotion)  
**Phase 5:** Consider ChromaDB for production-scale multi-user deployments

---

**Inspired by:** [prem-research/cortex](https://github.com/prem-research/cortex)  
**Fork:** [heliosarchitect/cortex-openclaw](https://github.com/heliosarchitect/cortex-openclaw)  
**Built:** 2026-02-03
