# Cortex Memory Management Spec
<!-- AI.TOC: Cortex Memory Management Spec — Read lines 1-20 for navigation.
  §1 Current State                              → lines 3-9
  §2 Proposed Additions                         → lines 10-176
  §3 Priority Order                             → lines 177-191
  §4 Implementation Notes                       → lines 192-199
  Total: 199 lines | Sections: 4
-->

## Current State
- `cortex_create_category` — create new category with keywords
- `cortex_add` — store memory with ONE category
- `cortex_list_categories` — list existing categories
- `cortex_stm` — view recent STM items
- `cortex_stats` — get memory statistics

## Proposed Additions

### 1. Multi-Category Tagging
**Problem:** RAM 3500 EMP prep is both `shtf` AND `vehicles`. Currently must pick one.

**Solution:**
```
cortex_add:
  categories: ["shtf", "vehicles"]  # Array instead of single string
```

**Behavior:**
- Memory appears in searches for BOTH categories
- Hot memory can surface via either category's keywords
- Display shows primary category, with secondary tags visible

---

### 2. Move Memory Between Categories
**Problem:** Miscategorized memory, or category structure evolved.

**Solution:**
```
cortex_move:
  memory_id: "abc123"
  from_category: "general"
  to_category: "trading"
```

**Behavior:**
- Updates category field in database
- Re-indexes for semantic search
- Preserves access count, importance, timestamps

---

### 3. Merge/Compact Categories
**Problem:** Created `trading` and `crypto` separately, realize they should be one.

**Solution:**
```
cortex_merge:
  from_category: "crypto"
  into_category: "trading"
  delete_source: true  # Optional: remove empty category after merge
```

**Behavior:**
- Moves all memories from source to target
- Merges keyword lists
- Optionally deletes now-empty source category

---

### 4. Memory Deduplication
**Problem:** Same memory appearing 5x in semantic results (already observed).

**Solution:**
```
cortex_dedupe:
  category: "trading"  # Optional: scope to category
  similarity_threshold: 0.95  # How similar to consider duplicate
  action: "report" | "merge" | "delete_older"
```

**Behavior:**
- Scans for near-duplicate content via embedding similarity
- Report: Just list duplicates
- Merge: Combine into one, sum access counts, keep highest importance
- Delete older: Keep most recent, delete others

---

### 5. Importance Adjustment
**Problem:** Stored something at importance 1.5, later realized it's critical.

**Solution:**
```
cortex_update:
  memory_id: "abc123"
  importance: 3.0  # New importance
  # Could also update content, add notes, etc.
```

---

### 6. Memory Linking
**Problem:** Two memories are related but in different categories.

**Solution:**
```
cortex_link:
  memory_id: "abc123"
  related_to: "def456"
  relationship: "builds_on" | "contradicts" | "supersedes" | "related"
```

**Behavior:**
- When one memory surfaces, linked memories get boosted
- Can query: "what's related to this memory?"
- Enables knowledge graph traversal

---

### 7. Memory Archival
**Problem:** Old memories cluttering active context, but don't want to delete.

**Solution:**
```
cortex_archive:
  memory_id: "abc123"
  # OR
  older_than: "30d"
  category: "trading"
```

**Behavior:**
- Archived memories don't appear in hot tier or semantic search by default
- Can query archived memories explicitly
- Reduces noise without losing history

---

### 8. Category Rename
**Problem:** Named category poorly, want to fix without losing memories.

**Solution:**
```
cortex_rename_category:
  old_name: "stuff"
  new_name: "general"
```

---

### 9. Bulk Operations
**Problem:** Need to tag 50 memories with new category after creating it.

**Solution:**
```
cortex_bulk:
  action: "add_category" | "remove_category" | "set_importance"
  filter:
    contains: "RAM 3500"
    # OR
    category: "general"
    # OR
    older_than: "7d"
  value: "vehicles"  # The category to add, or importance to set
```

---

### 10. Memory Edit/Append
**Problem:** Have new info about an existing memory, don't want duplicate.

**Solution:**
```
cortex_edit:
  memory_id: "abc123"
  append: "UPDATE: Also need spare fuel injectors."
  # OR
  replace: "Full new content..."
```

---

## Priority Order

1. **Multi-category tagging** — Most immediate value, simple schema change
2. **Deduplication** — Already causing noise in my context
3. **Importance adjustment** — Quick win, simple update
4. **Memory edit/append** — Reduces duplicate creation
5. **Move between categories** — Needed for reorganization
6. **Category merge** — Less urgent but useful
7. **Linking** — Advanced feature, enables knowledge graph
8. **Archival** — For long-term maintenance
9. **Bulk operations** — Power feature for reorganization
10. **Category rename** — Nice to have

---

## Implementation Notes

- All operations should update timestamps (modified_at)
- Maintain audit trail for debugging
- Re-embed content after edits that change text
- Access counts should transfer/sum on merges
- Consider "undo" for destructive operations (soft delete first)
