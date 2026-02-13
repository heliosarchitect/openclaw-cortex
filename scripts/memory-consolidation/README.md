# Memory Consolidation Engine

Clusters semantically related memories, synthesizes them via LLM, and manages memory bloat through intelligent pruning.

## Architecture

```
brain.db STM (1500+) ──┐
                        ├─→ Embed (MiniLM-L6-v2 @ :8030) → Cluster (DBSCAN) → Synthesize (qwen2.5:32b @ :11434)
.embeddings.db (211) ──┘                                                          │
                                                                                   ├→ Promote to STM
                                                                                   └→ Prune absorbed memories
```

**Data flow:**
1. Load all memories from brain.db STM + legacy .embeddings.db
2. Ensure all have 384-dim embeddings (compute missing via local server)
3. DBSCAN clustering on cosine distance (eps=0.35)
4. LLM synthesizes each cluster into a consolidated insight
5. High-importance consolidations promoted back to STM
6. Low-value absorbed memories pruned (with audit trail)

## Commands

```bash
# Analyze — see clusters without changing anything
./consolidate.py scan

# Find near-duplicates (threshold adjustable)
./consolidate.py duplicates
./consolidate.py duplicates --threshold 0.95

# Consolidate — synthesize clusters
./consolidate.py consolidate --dry              # Preview
./consolidate.py consolidate --limit 10         # Process top 10 clusters
./consolidate.py consolidate --min-size 5 --max-size 15  # Size filter

# Prune duplicates
./consolidate.py prune --dry                    # Preview removals
./consolidate.py prune                          # Actually remove

# Stats
./consolidate.py stats
```

## Storage

- **consolidations.db** — tracks all consolidations + pruned memories (audit trail)
- All pruned memories have original content backed up before removal
- Promoted insights get `[CONSOLIDATED]` prefix + new embeddings

## Tuning

Key parameters in `consolidate.py`:
- `DBSCAN_EPS = 0.35` — cosine distance threshold (lower = tighter clusters)
- `DUPLICATE_THRESHOLD = 0.92` — similarity for near-duplicate detection
- `PROMOTE_THRESHOLD = 2.0` — min importance to promote to permanent STM
- `PRUNE_AGE_DAYS = 14` — only prune memories older than this
- `PRUNE_IMPORTANCE = 1.2` — only prune if importance ≤ this

## Current Stats (2026-02-13)

- 1713 total memories across both stores
- 168 clusters found, 58% of memories are clustered
- 14,700+ duplicate pairs detected
- ~452 memories prunable via dedup alone
- ~1,061 reducible via cluster consolidation
