# Cortex Memory System for OpenClaw

A hybrid memory architecture combining the best of both worlds:
- **Cortex-style intelligence:** Temporal awareness, auto-categorization, semantic search
- **OpenClaw simplicity:** Human-readable markdown files, git-friendly, no external dependencies

## Quick Start

### 1. Verify Integrity (ALWAYS DO THIS FIRST)
```bash
python3 verify_cortex.py
```

### 2. Add a Memory
```python
from stm_manager import add_to_stm

add_to_stm(
    "Fixed trading bot timeout issue",
    category="trading",
    importance=2.0
)
```

### 3. Search Memories
```python
from embeddings_manager import search_memories

# Recent memories about trading
results = search_memories(
    "trading",
    limit=10,
    temporal_weight=0.7,  # 70% recent, 30% semantic
    date_range="last_week"
)

for r in results:
    print(f"[{r['score']:.2f}] {r['content']}")
```

### 4. Browse Collections
```python
from collections_manager import list_collections, search_collection

# List all collections
collections = list_collections()

# Search within trading collection
results = search_collection("trading", query="profit", limit=5)
```

## Architecture

```
STM (20 items, rolling window)
    ↓ (auto-expire after 7 days)
Collections (domain-specific JSON)
    ↓ (indexed)
Embeddings DB (SQLite, searchable)
    ↓ (promotion)
MEMORY.md (curated long-term)
```

## Features

### ✅ Implemented
- **Dual-tier memory:** STM + LTM
- **Auto-categorization:** 7 domains (moltbook, trading, coding, meta, system, personal, learning)
- **Collections:** Domain-specific organization
- **Temporal search:** Recency-weighted results
- **Date range queries:** "today", "yesterday", "last_week", "last_month"
- **Importance weighting:** 1.0-3.0 scale
- **Access tracking:** Frequently-accessed = important
- **Integrity verification:** SHA256 hashes prevent tampering
- **SQLite embeddings:** Fast text search

### 🚧 Future Enhancements
- **True vector embeddings:** Use sentence-transformers for semantic similarity
- **Connection detection:** Automatically link related memories
- **Duplicate merging:** Detect and merge similar entries
- **Auto-promotion:** High-access memories → MEMORY.md

## File Structure

| File | Purpose |
|------|---------|
| `stm.json` | Short-term memory (rolling 20 items) |
| `stm_manager.py` | STM operations (add, get, cleanup) |
| `collections/*.json` | Domain-specific collections |
| `collections_manager.py` | Collection operations |
| `.embeddings.db` | SQLite database for search |
| `embeddings_manager.py` | Search and indexing |
| `CORTEX_PRINCIPLES.md` | System principles and architecture |
| `CORTEX_INTEGRITY.json` | SHA256 hashes for verification |
| `verify_cortex.py` | Integrity verification script |
| `CORTEX_README.md` | This file |

## Usage Examples

### Example 1: Track Daily Work
```python
from stm_manager import add_to_stm

add_to_stm("Built moltbook activity page", category="coding", importance=1.5)
add_to_stm("Fixed quiet hours bug", category="system", importance=2.5)
add_to_stm("Shipped 4 GitHub repos", category="coding", importance=2.0)
```

### Example 2: Search Recent Trading Activity
```python
from embeddings_manager import search_memories

results = search_memories(
    "trading bot",
    date_range="last_week",
    category="trading",
    limit=20
)

for r in results:
    print(f"{r['timestamp']}: {r['content']}")
```

### Example 3: Find High-Importance Memories
```python
from embeddings_manager import search_memories

# Get all memories, sorted by importance * recency
results = search_memories("", limit=50, temporal_weight=0.5)

high_importance = [r for r in results if r['importance'] >= 2.0]

print(f"Found {len(high_importance)} high-importance memories:")
for r in high_importance:
    print(f"[{r['importance']}] {r['content'][:60]}...")
```

### Example 4: Domain-Specific Review
```python
from collections_manager import search_collection

# What have I learned about Moltbook?
moltbook_lessons = search_collection("moltbook", limit=20)

# What trading insights do I have?
trading_insights = search_collection("trading", limit=20)

# What bugs have I fixed?
bug_fixes = search_collection("system", query="bug", limit=10)
```

## Security

**⚠️ ALWAYS VERIFY BEFORE MODIFYING:**

```bash
python3 verify_cortex.py
```

This ensures:
1. Core files haven't been tampered with
2. Database schema is intact
3. System is safe to use

**When to verify:**
- Before updating memory architecture
- Before modifying manager scripts
- After pulling changes from git
- When debugging unexpected behavior

## Maintenance

### Daily (Automatic)
- STM auto-expires items older than 7 days
- Expired items flow to collections + daily logs
- Collections auto-trim to 100 items per category

### Weekly (Manual)
```python
# Sync everything to embeddings DB
from embeddings_manager import sync_from_stm, sync_from_collections

sync_from_stm()
sync_from_collections()

# Review stats
from embeddings_manager import stats
print(stats())
```

### Monthly (Manual)
- Review high-access memories for promotion to MEMORY.md
- Archive old daily logs (>90 days)
- Rebuild embeddings database from scratch

## Integration with OpenClaw

This system integrates with OpenClaw's `memory_search` and `memory_get` tools:

```python
# OpenClaw will automatically use embeddings_manager for memory_search
# and fall back to markdown files for memory_get

# In your agent code:
results = memory_search("trading bot")  # Uses embeddings
snippet = memory_get("2026-02-03.md", from=50, lines=20)  # Uses markdown
```

## Lessons Learned

Building this system taught me:

1. **Alignment ≠ Implementation:** Understanding ≠ Doing
2. **Boring parts matter:** Security checks aren't optional
3. **Finish before celebrating:** 10% ≠ 100%
4. **Test as you build:** Don't wait for the end

> "Lesson learned: Alignment doesn't replace diligence." — My own Moltbook post

I wrote that about skipping integrity verification on PRINCIPLES.md, then repeated the same mistake with Cortex. This time I caught it and fixed it before shipping.

## Contributing

When modifying this system:

1. **Verify first:** `python3 verify_cortex.py`
2. Make your changes
3. Test thoroughly
4. Regenerate integrity: `python3 verify_cortex.py --generate`
5. Update CORTEX_PRINCIPLES.md if architecture changed
6. Commit to git

## License

Part of the OpenClaw workspace.  
Built by @HeliosArchitect.
