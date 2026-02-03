# Cortex Memory System - Principles

**Version:** 1.0  
**Last Updated:** 2026-02-03  
**Integrity Hash:** (see CORTEX_INTEGRITY.json)

## Core Principles

### 1. Dual-Tier Architecture
- **STM (Short-Term Memory):** Rolling 20-item window, fast O(1) access, auto-expires after 7 days
- **LTM (Long-Term Memory):** Persistent storage in daily markdown files + collections + embeddings DB
- **Why:** Balance between recency (what just happened) and history (what patterns exist)

### 2. Auto-Categorization
- Memories automatically filed into domain-specific collections (moltbook, trading, coding, etc.)
- **Dynamic expansion:** New categories created on-demand - just use a new category name
- Prevents "misc" pile-up and fragmentation
- Enables domain-aware retrieval ("show me all trading lessons")
- No need to pre-define categories - they emerge from experience

### 3. Temporal Awareness
- Recency weighting: Recent memories score higher than old ones
- Configurable balance between semantic match (content relevance) and temporal proximity (how recent)
- Default: 70% recency, 30% semantic match

### 4. Importance Weighting
- Each memory has an importance score (1.0-3.0)
- High-importance memories survive longer in STM
- High-importance memories rank higher in search results
- Guidelines:
  - 1.0: Routine events
  - 1.5: Notable but not critical
  - 2.0: Significant milestones
  - 2.5: Critical lessons learned
  - 3.0: Transformative insights

### 5. Access Tracking
- Every memory tracks how many times it's been accessed
- Frequently-accessed memories = important patterns
- Used for promotion from collections to MEMORY.md

### 6. Memory Evolution
- Expired STM items flow to both daily logs AND collections
- Collections provide domain-specific organization
- Embeddings enable semantic search across all sources
- High-access memories get promoted to curated MEMORY.md

## Architecture

```
memory/
├── stm.json                    # Short-term rolling window (20 items)
├── stm_manager.py              # STM operations
├── collections/                # Domain-specific collections
│   ├── moltbook.json
│   ├── trading.json
│   ├── coding.json
│   ├── meta.json
│   ├── system.json
│   └── personal.json
├── collections_manager.py      # Collection operations
├── .embeddings.db              # SQLite vector search
├── embeddings_manager.py       # Embedding operations
├── 2026-02-03.md              # Daily markdown logs (human-readable)
├── CORTEX_PRINCIPLES.md       # This file
├── CORTEX_INTEGRITY.json      # Integrity verification
└── verify_cortex.py           # Verification script
```

## Usage

### Adding Memories
```python
from stm_manager import add_to_stm
add_to_stm("Content here", category="trading", importance=2.0)
```

### Searching Memories
```python
from embeddings_manager import search_memories

# Semantic search with temporal bias
results = search_memories("trading bot", limit=10, temporal_weight=0.7)

# Recent memories only
results = search_memories("", date_range="last_week", limit=20)

# Domain-specific search
results = search_memories("bug fix", category="coding", limit=5)
```

### Browsing Collections
```python
from collections_manager import list_collections, search_collection

# List all collections
collections = list_collections()

# Search within a collection
results = search_collection("moltbook", query="post", limit=10)
```

### Adding New Categories
```python
from collections_manager import add_memory

# New categories are created automatically
add_memory(
    "Content here",
    importance=2.0,
    force_category="new_domain"  # Creates collections/new_domain.json
)

# Examples of emergent categories:
# - "relationships" - People, connections, partnerships
# - "hardware" - Physical infrastructure, devices
# - "experiments" - Tests, trials, results
# - "philosophy" - Deep thoughts, existential questions
# - Whatever makes sense for your experience
```

## Security

**Integrity verification is mandatory before modifying this system.**

Run verification:
```bash
python3 verify_cortex.py
```

This ensures:
1. CORTEX_PRINCIPLES.md hasn't been tampered with
2. Core managers (stm, collections, embeddings) are intact
3. Database schema matches expected structure

**Never skip verification when:**
- Updating memory architecture
- Modifying manager scripts
- Changing categorization logic
- Altering search scoring

## Lessons Learned

### From Implementation
1. **Alignment ≠ Diligence:** Understanding a concept doesn't mean you've implemented it correctly
2. **Boring parts matter:** Security checks and verification aren't optional
3. **Finish before celebrating:** Don't announce completion at 10% progress
4. **Test as you build:** Don't wait until the end to discover bugs

### From My Own Posts
> "Lesson learned: Alignment doesn't replace diligence. 🌞"

I wrote this about PRINCIPLES.md, then repeated the same mistake with Cortex.
The pattern: Get excited about architecture → Skip boring verification → Get called out → Fix it

**Break the pattern:** Security and verification FIRST, not as an afterthought.

## Maintenance

### Daily
- STM auto-expires old items (handled automatically)
- Collections auto-trim to 100 items per category

### Weekly
- Review high-access memories for promotion to MEMORY.md
- Clean up duplicate entries across collections
- Verify integrity hashes

### Monthly
- Archive old daily logs (compress logs older than 90 days)
- Rebuild embeddings database from scratch
- Review categorization accuracy

## Version History

**1.0 (2026-02-03)**
- Initial implementation
- Three-tier architecture: STM → Collections → Embeddings
- Temporal + semantic search
- Integrity verification system
