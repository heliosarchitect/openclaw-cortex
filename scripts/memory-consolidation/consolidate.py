#!/usr/bin/env python3
"""
Memory Consolidation Engine
============================
Clusters semantically related memories, synthesizes them via LLM,
and promotes consolidated insights to permanent storage.

Data sources:
  - brain.db STM table (primary — 1500+ entries)
  - .embeddings.db memories table (legacy — 211 entries)

Embedding: local all-MiniLM-L6-v2 server at localhost:8030 (384-dim)
LLM: Ollama qwen2.5:32b at localhost:11434

Usage:
  ./consolidate.py scan              # Analyze clusters, show report
  ./consolidate.py consolidate       # Run full consolidation pipeline
  ./consolidate.py consolidate --dry # Dry run — show what would happen
  ./consolidate.py duplicates        # Find and report near-duplicates
  ./consolidate.py prune --dry       # Show what would be pruned
  ./consolidate.py prune             # Actually prune low-value memories
"""

import argparse
import hashlib
import json
import os
import sqlite3
import struct
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import requests
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BRAIN_DB = Path.home() / ".openclaw/workspace/memory/brain.db"
EMBEDDINGS_DB = Path.home() / ".openclaw/workspace/memory/.embeddings.db"
CONSOLIDATION_DB = Path.home() / ".openclaw/workspace/memory/consolidations.db"
EMBED_URL = "http://localhost:8030/embed"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:32b"
EMBED_DIM = 384

# Clustering parameters
DBSCAN_EPS = 0.35          # cosine distance threshold (lower = tighter clusters)
DBSCAN_MIN_SAMPLES = 2     # minimum cluster size
DUPLICATE_THRESHOLD = 0.92  # cosine similarity for near-duplicates
MIN_CLUSTER_SIZE = 2
MAX_CLUSTER_SIZE = 20       # don't try to consolidate massive clusters in one shot

# Importance thresholds
PROMOTE_THRESHOLD = 2.0     # consolidated insights >= this get promoted
PRUNE_AGE_DAYS = 14         # memories older than this + low importance can be pruned
PRUNE_IMPORTANCE = 1.2      # prune if importance <= this AND old AND in a consolidated cluster


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Memory:
    id: str
    content: str
    source: str          # 'stm' or 'legacy'
    categories: str      # JSON array string or plain string
    importance: float
    access_count: int
    created_at: str
    embedding: Optional[np.ndarray] = None

    @property
    def age_days(self) -> float:
        try:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except Exception:
            return 0.0

    @property
    def category_list(self) -> list[str]:
        try:
            return json.loads(self.categories)
        except Exception:
            return [self.categories] if self.categories else []


@dataclass
class Cluster:
    id: int
    memories: list[Memory] = field(default_factory=list)
    centroid: Optional[np.ndarray] = None
    consolidated_text: Optional[str] = None
    importance: float = 0.0

    @property
    def size(self) -> int:
        return len(self.memories)

    @property
    def avg_importance(self) -> float:
        if not self.memories:
            return 0.0
        return sum(m.importance for m in self.memories) / len(self.memories)

    @property
    def max_importance(self) -> float:
        return max((m.importance for m in self.memories), default=0.0)

    @property
    def total_access(self) -> int:
        return sum(m.access_count for m in self.memories)

    @property
    def categories(self) -> set[str]:
        cats = set()
        for m in self.memories:
            cats.update(m.category_list)
        return cats

    @property
    def date_range(self) -> str:
        dates = sorted(m.created_at for m in self.memories)
        if len(dates) < 2:
            return dates[0][:10] if dates else "?"
        return f"{dates[0][:10]} → {dates[-1][:10]}"


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding from local MiniLM server."""
    try:
        resp = requests.post(EMBED_URL, json={"text": text[:2000]}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        vec = data.get("embeddings", [None])[0] or data.get("embedding")
        if vec is None:
            return None
        return np.array(vec, dtype=np.float32)
    except Exception as e:
        print(f"  ⚠ Embedding error: {e}", file=sys.stderr)
        return None


def blob_to_vec(blob: bytes, dim: int = EMBED_DIM) -> Optional[np.ndarray]:
    """Convert stored blob to numpy vector."""
    if blob is None:
        return None
    try:
        # Try float32 first
        if len(blob) == dim * 4:
            return np.frombuffer(blob, dtype=np.float32)
        # Try float64
        if len(blob) == dim * 8:
            return np.frombuffer(blob, dtype=np.float64).astype(np.float32)
        # Try JSON
        return np.array(json.loads(blob), dtype=np.float32)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_stm_memories() -> list[Memory]:
    """Load memories from brain.db STM table."""
    if not BRAIN_DB.exists():
        print(f"  ⚠ brain.db not found at {BRAIN_DB}")
        return []

    conn = sqlite3.connect(str(BRAIN_DB))
    rows = conn.execute("""
        SELECT s.id, s.content, s.categories, s.importance, s.access_count, s.created_at,
               e.embedding
        FROM stm s
        LEFT JOIN embeddings e ON e.source_type = 'stm' AND e.source_id = s.id
        ORDER BY s.created_at DESC
    """).fetchall()
    conn.close()

    memories = []
    for row in rows:
        emb = blob_to_vec(row[6]) if row[6] else None
        memories.append(Memory(
            id=row[0],
            content=row[1],
            source='stm',
            categories=row[2] or '[]',
            importance=row[3] or 1.0,
            access_count=row[4] or 0,
            created_at=row[5],
            embedding=emb,
        ))
    return memories


def load_legacy_memories() -> list[Memory]:
    """Load memories from .embeddings.db."""
    if not EMBEDDINGS_DB.exists():
        return []

    conn = sqlite3.connect(str(EMBEDDINGS_DB))
    rows = conn.execute("""
        SELECT id, content, category, importance, access_count, timestamp
        FROM memories ORDER BY timestamp DESC
    """).fetchall()
    conn.close()

    memories = []
    for row in rows:
        cat = json.dumps([row[2]]) if row[2] else '[]'
        memories.append(Memory(
            id=row[0],
            content=row[1],
            source='legacy',
            categories=cat,
            importance=row[3] or 1.0,
            access_count=row[4] or 0,
            created_at=row[5],
            embedding=None,  # Legacy DB doesn't store embeddings inline
        ))
    return memories


def load_all_memories() -> list[Memory]:
    """Load and merge all memory sources."""
    stm = load_stm_memories()
    legacy = load_legacy_memories()
    print(f"  Loaded {len(stm)} STM memories, {len(legacy)} legacy memories")
    return stm + legacy


# ---------------------------------------------------------------------------
# Embedding pipeline
# ---------------------------------------------------------------------------

def ensure_embeddings(memories: list[Memory], batch_size: int = 50) -> list[Memory]:
    """Ensure all memories have embeddings, computing missing ones."""
    missing = [m for m in memories if m.embedding is None]
    if not missing:
        print(f"  All {len(memories)} memories have embeddings ✓")
        return memories

    print(f"  Computing embeddings for {len(missing)} memories...")
    computed = 0
    failed = 0
    for i, m in enumerate(missing):
        emb = get_embedding(m.content)
        if emb is not None:
            m.embedding = emb
            computed += 1
        else:
            failed += 1
        if (i + 1) % 100 == 0:
            print(f"    {i + 1}/{len(missing)} done ({computed} ok, {failed} failed)")

    print(f"  Embeddings: {computed} computed, {failed} failed")
    # Filter out memories without embeddings
    return [m for m in memories if m.embedding is not None]


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def cluster_memories(memories: list[Memory]) -> list[Cluster]:
    """Cluster memories using DBSCAN on cosine distance."""
    if len(memories) < 2:
        return []

    # Build embedding matrix
    X = np.vstack([m.embedding for m in memories])

    # Normalize for cosine distance
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X_norm = X / norms

    # DBSCAN with cosine distance (1 - similarity)
    print(f"  Clustering {len(memories)} memories (eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES})...")
    db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, metric='cosine')
    labels = db.fit_predict(X_norm)

    clusters = defaultdict(list)
    noise_count = 0
    for idx, label in enumerate(labels):
        if label == -1:
            noise_count += 1
            continue
        clusters[label].append(memories[idx])

    result = []
    for label, mems in sorted(clusters.items()):
        if len(mems) < MIN_CLUSTER_SIZE:
            continue
        embeddings = np.vstack([m.embedding for m in mems])
        centroid = embeddings.mean(axis=0)
        result.append(Cluster(id=label, memories=mems, centroid=centroid))

    print(f"  Found {len(result)} clusters ({noise_count} unclustered/unique memories)")
    return result


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def find_duplicates(memories: list[Memory], threshold: float = DUPLICATE_THRESHOLD) -> list[tuple[Memory, Memory, float]]:
    """Find near-duplicate memory pairs using cosine similarity."""
    if len(memories) < 2:
        return []

    X = np.vstack([m.embedding for m in memories])
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X_norm = X / norms

    print(f"  Computing pairwise similarities for {len(memories)} memories...")
    # Do in chunks to avoid OOM on large sets
    dupes = []
    chunk_size = 500
    for i in range(0, len(memories), chunk_size):
        chunk = X_norm[i:i + chunk_size]
        sim_matrix = chunk @ X_norm.T
        for ci in range(len(chunk)):
            real_i = i + ci
            for j in range(real_i + 1, len(memories)):
                sim = sim_matrix[ci, j]
                if sim >= threshold:
                    dupes.append((memories[real_i], memories[j], float(sim)))

    dupes.sort(key=lambda x: x[2], reverse=True)
    print(f"  Found {len(dupes)} duplicate pairs (threshold={threshold})")
    return dupes


# ---------------------------------------------------------------------------
# LLM Synthesis
# ---------------------------------------------------------------------------

def synthesize_cluster(cluster: Cluster) -> Optional[str]:
    """Use LLM to synthesize a cluster of related memories into a consolidated insight."""
    # Sort by importance, then recency
    sorted_mems = sorted(
        cluster.memories,
        key=lambda m: (-m.importance, m.created_at),
    )

    # Limit to avoid context overflow
    mems_to_use = sorted_mems[:MAX_CLUSTER_SIZE]

    memory_texts = []
    for i, m in enumerate(mems_to_use):
        memory_texts.append(
            f"[{i+1}] (importance={m.importance}, date={m.created_at[:10]}, "
            f"categories={m.category_list})\n{m.content[:500]}"
        )

    prompt = f"""You are a memory consolidation engine. Below are {len(mems_to_use)} related memories from an AI assistant's knowledge base. They share semantic themes.

Your task: Synthesize these into ONE consolidated insight that:
1. Preserves all critical facts, decisions, and lessons learned
2. Eliminates redundancy and noise
3. Captures the key narrative arc / evolution if there is one
4. Notes any contradictions between memories
5. Assigns an importance score (1.0=routine, 2.0=notable, 3.0=critical)

MEMORIES:
{chr(10).join(memory_texts)}

Respond in this exact format:
IMPORTANCE: <score>
CATEGORIES: <comma-separated>
INSIGHT:
<your consolidated text — be thorough but not redundant, aim for 2-4 paragraphs>"""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 1024},
        }, timeout=120)
        if resp.status_code != 200:
            print(f"  ⚠ LLM error: HTTP {resp.status_code}")
            return None
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠ LLM error: {e}")
        return None


def parse_synthesis(text: str) -> tuple[float, list[str], str]:
    """Parse LLM synthesis response into (importance, categories, insight)."""
    importance = 2.0
    categories = []
    insight = text

    lines = text.split("\n")
    insight_start = 0
    for i, line in enumerate(lines):
        if line.startswith("IMPORTANCE:"):
            try:
                importance = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("CATEGORIES:"):
            cats = line.split(":", 1)[1].strip()
            categories = [c.strip() for c in cats.split(",") if c.strip()]
        elif line.startswith("INSIGHT:"):
            insight_start = i + 1
            break

    if insight_start > 0:
        insight = "\n".join(lines[insight_start:]).strip()

    return importance, categories, insight


# ---------------------------------------------------------------------------
# Consolidation DB
# ---------------------------------------------------------------------------

def init_consolidation_db():
    """Initialize the consolidation tracking database."""
    conn = sqlite3.connect(str(CONSOLIDATION_DB))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS consolidations (
            id TEXT PRIMARY KEY,
            insight TEXT NOT NULL,
            importance REAL DEFAULT 2.0,
            categories TEXT,
            source_memory_ids TEXT,    -- JSON array of original memory IDs
            source_count INTEGER,
            cluster_id INTEGER,
            promoted INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pruned (
            memory_id TEXT PRIMARY KEY,
            source TEXT,               -- 'stm' or 'legacy'
            reason TEXT,               -- 'consolidated', 'duplicate', 'low_value'
            consolidation_id TEXT,     -- which consolidation absorbed it
            original_content TEXT,     -- backup of original content
            pruned_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_consolidations_promoted ON consolidations(promoted);
        CREATE INDEX IF NOT EXISTS idx_pruned_consolidation ON pruned(consolidation_id);
    """)
    conn.close()


def save_consolidation(cluster: Cluster, importance: float, categories: list[str], insight: str) -> str:
    """Save a consolidation result."""
    cid = f"cons_{hashlib.sha256(insight.encode()).hexdigest()[:12]}"
    source_ids = json.dumps([m.id for m in cluster.memories])
    cats = json.dumps(categories)
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(str(CONSOLIDATION_DB))
    conn.execute("""
        INSERT OR REPLACE INTO consolidations
        (id, insight, importance, categories, source_memory_ids, source_count, cluster_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (cid, insight, importance, cats, source_ids, cluster.size, cluster.id, now))
    conn.commit()
    conn.close()
    return cid


def record_prune(memory: Memory, reason: str, consolidation_id: str = ""):
    """Record a pruned memory for audit trail."""
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(CONSOLIDATION_DB))
    conn.execute("""
        INSERT OR IGNORE INTO pruned
        (memory_id, source, reason, consolidation_id, original_content, pruned_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (memory.id, memory.source, reason, consolidation_id, memory.content[:2000], now))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Promotion: write consolidated insight back to brain.db STM
# ---------------------------------------------------------------------------

def promote_to_stm(consolidation_id: str, insight: str, importance: float, categories: list[str]):
    """Write a consolidated insight into brain.db STM as a new memory."""
    import secrets
    stm_id = f"stm_{secrets.token_hex(6)}"
    now = datetime.now(timezone.utc).isoformat()
    cats = json.dumps(categories)

    conn = sqlite3.connect(str(BRAIN_DB))
    conn.execute("""
        INSERT OR IGNORE INTO stm (id, content, categories, importance, access_count, created_at, source)
        VALUES (?, ?, ?, ?, 0, ?, 'consolidation')
    """, (stm_id, f"[CONSOLIDATED] {insight}", cats, min(importance, 3.0), now))
    conn.commit()
    conn.close()

    # Also embed it
    emb = get_embedding(insight)
    if emb is not None:
        conn = sqlite3.connect(str(BRAIN_DB))
        emb_id = f"emb_{secrets.token_hex(6)}"
        conn.execute("""
            INSERT OR IGNORE INTO embeddings (id, source_type, source_id, content, embedding, model, created_at)
            VALUES (?, 'stm', ?, ?, ?, 'all-MiniLM-L6-v2', ?)
        """, (emb_id, stm_id, insight[:500], emb.tobytes(), now))
        conn.commit()
        conn.close()

    print(f"  ✅ Promoted {consolidation_id} → STM as {stm_id} (importance={importance})")
    return stm_id


# ---------------------------------------------------------------------------
# Pruning: remove absorbed low-value memories from STM
# ---------------------------------------------------------------------------

def prune_memory(memory: Memory, reason: str, consolidation_id: str = "", dry_run: bool = True):
    """Remove a memory from its source database."""
    if dry_run:
        print(f"  [DRY] Would prune {memory.id} ({memory.source}): {reason}")
        return

    record_prune(memory, reason, consolidation_id)

    if memory.source == 'stm':
        conn = sqlite3.connect(str(BRAIN_DB))
        conn.execute("DELETE FROM stm WHERE id = ?", (memory.id,))
        conn.execute("DELETE FROM embeddings WHERE source_type = 'stm' AND source_id = ?", (memory.id,))
        conn.commit()
        conn.close()
    elif memory.source == 'legacy':
        conn = sqlite3.connect(str(EMBEDDINGS_DB))
        conn.execute("DELETE FROM memories WHERE id = ?", (memory.id,))
        conn.commit()
        conn.close()

    print(f"  🗑  Pruned {memory.id} ({memory.source}): {reason}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_scan(args):
    """Scan and report on memory clusters."""
    print("═══ Memory Consolidation Engine — Scan ═══\n")

    memories = load_all_memories()
    memories = ensure_embeddings(memories)

    if not memories:
        print("No memories with embeddings found.")
        return

    clusters = cluster_memories(memories)

    print(f"\n{'─' * 70}")
    print(f"{'CLUSTER REPORT':^70}")
    print(f"{'─' * 70}\n")

    total_consolidatable = 0
    for c in sorted(clusters, key=lambda x: x.size, reverse=True)[:30]:
        total_consolidatable += c.size
        print(f"  Cluster #{c.id:3d} │ {c.size:3d} memories │ "
              f"avg_imp={c.avg_importance:.1f} │ max_imp={c.max_importance:.1f} │ "
              f"access={c.total_access:4d} │ cats={','.join(sorted(c.categories)[:3])}")
        # Show a sample
        sample = sorted(c.memories, key=lambda m: -m.importance)[:2]
        for m in sample:
            print(f"           └─ {m.content[:90]}...")
        print()

    # Summary
    unclustered = len(memories) - total_consolidatable
    print(f"{'─' * 70}")
    print(f"  Total memories:      {len(memories)}")
    print(f"  In clusters:         {total_consolidatable} ({total_consolidatable/len(memories)*100:.0f}%)")
    print(f"  Unique/unclustered:  {unclustered} ({unclustered/len(memories)*100:.0f}%)")
    print(f"  Clusters found:      {len(clusters)}")
    print(f"  Avg cluster size:    {total_consolidatable/max(len(clusters),1):.1f}")

    # Estimate savings
    large_clusters = [c for c in clusters if c.size >= 3]
    potential_reduction = sum(c.size - 1 for c in large_clusters)
    print(f"\n  🎯 Potential reduction: ~{potential_reduction} memories "
          f"(from {len(large_clusters)} clusters of 3+)")


def cmd_duplicates(args):
    """Find and report near-duplicates."""
    print("═══ Memory Consolidation Engine — Duplicate Report ═══\n")

    memories = load_all_memories()
    memories = ensure_embeddings(memories)

    if not memories:
        print("No memories with embeddings found.")
        return

    dupes = find_duplicates(memories, threshold=args.threshold)

    if not dupes:
        print("  No duplicates found! Memory is clean. ✓")
        return

    print(f"\n  Found {len(dupes)} duplicate pairs:\n")
    for i, (m1, m2, sim) in enumerate(dupes[:50]):
        print(f"  [{i+1}] Similarity: {sim:.3f}")
        print(f"      A: [{m1.source}] {m1.content[:80]}...")
        print(f"      B: [{m2.source}] {m2.content[:80]}...")
        print()

    # Count unique memories involved
    dupe_ids = set()
    for m1, m2, _ in dupes:
        dupe_ids.add(m1.id)
        dupe_ids.add(m2.id)
    print(f"  {len(dupe_ids)} unique memories involved in duplicates")
    print(f"  Estimated removable: ~{len(dupes)} (keep one from each pair)")


def cmd_consolidate(args):
    """Run the full consolidation pipeline."""
    dry_run = args.dry
    print(f"═══ Memory Consolidation Engine — {'DRY RUN' if dry_run else 'CONSOLIDATE'} ═══\n")

    init_consolidation_db()
    memories = load_all_memories()
    memories = ensure_embeddings(memories)

    if not memories:
        print("No memories to consolidate.")
        return

    # Step 1: Cluster
    clusters = cluster_memories(memories)
    min_sz = getattr(args, 'min_size', 3)
    max_sz = getattr(args, 'max_size', 50)
    actionable = [c for c in clusters if min_sz <= c.size <= max_sz]
    print(f"\n  {len(actionable)} clusters with {min_sz}-{max_sz} memories to consolidate\n")

    if not actionable:
        print("  No clusters large enough to consolidate.")
        return

    # Step 2: Synthesize each cluster
    consolidated = 0
    promoted = 0
    pruned_count = 0

    for c in sorted(actionable, key=lambda x: -x.size)[:args.limit]:
        print(f"  ┌── Cluster #{c.id} ({c.size} memories, cats={','.join(sorted(c.categories)[:3])})")
        print(f"  │   Date range: {c.date_range}")

        if dry_run:
            print(f"  │   [DRY] Would synthesize {c.size} memories")
            print(f"  │   Sample: {c.memories[0].content[:80]}...")
            print(f"  └──\n")
            consolidated += 1
            continue

        # Synthesize
        print(f"  │   Synthesizing with {OLLAMA_MODEL}...")
        result = synthesize_cluster(c)
        if result is None:
            print(f"  │   ⚠ Synthesis failed, skipping")
            print(f"  └──\n")
            continue

        importance, categories, insight = parse_synthesis(result)
        c.consolidated_text = insight
        c.importance = importance

        if not categories:
            categories = list(c.categories)[:3]

        # Save consolidation
        cid = save_consolidation(c, importance, categories, insight)
        consolidated += 1
        print(f"  │   ✅ Consolidated → {cid} (importance={importance})")

        # Promote if important enough
        if importance >= PROMOTE_THRESHOLD:
            promote_to_stm(cid, insight, importance, categories)
            promoted += 1

        # Prune absorbed memories (keep the highest-importance one as anchor)
        anchor = max(c.memories, key=lambda m: m.importance)
        for m in c.memories:
            if m.id == anchor.id:
                continue
            if m.importance <= PRUNE_IMPORTANCE and m.age_days >= PRUNE_AGE_DAYS:
                prune_memory(m, "consolidated", cid, dry_run=False)
                pruned_count += 1

        print(f"  └── Pruned {pruned_count} absorbed memories\n")

    print(f"\n{'─' * 70}")
    print(f"  Clusters processed:  {consolidated}")
    print(f"  Promoted to STM:     {promoted}")
    print(f"  Memories pruned:     {pruned_count}")
    if dry_run:
        print(f"  (DRY RUN — no changes made)")


def cmd_prune(args):
    """Prune near-duplicate and low-value memories."""
    dry_run = args.dry
    print(f"═══ Memory Consolidation Engine — {'DRY RUN PRUNE' if dry_run else 'PRUNE'} ═══\n")

    init_consolidation_db()
    memories = load_all_memories()
    memories = ensure_embeddings(memories)

    if not memories:
        print("No memories to prune.")
        return

    # Find duplicates
    dupes = find_duplicates(memories, threshold=DUPLICATE_THRESHOLD)

    # For each duplicate pair, mark the less important / older one for removal
    to_prune = {}
    for m1, m2, sim in dupes:
        # Keep the one with higher importance, or more accesses, or newer
        if m1.importance > m2.importance:
            victim = m2
        elif m2.importance > m1.importance:
            victim = m1
        elif m1.access_count > m2.access_count:
            victim = m2
        elif m2.access_count > m1.access_count:
            victim = m1
        elif m1.created_at > m2.created_at:
            victim = m2
        else:
            victim = m1

        if victim.id not in to_prune:
            to_prune[victim.id] = (victim, f"duplicate (sim={sim:.3f})")

    print(f"  {len(to_prune)} memories identified for pruning\n")

    pruned = 0
    for mid, (mem, reason) in sorted(to_prune.items(), key=lambda x: x[1][0].created_at):
        prune_memory(mem, reason, dry_run=dry_run)
        pruned += 1

    print(f"\n{'─' * 70}")
    print(f"  Pruned: {pruned}")
    if dry_run:
        print(f"  (DRY RUN — no changes made)")


def cmd_stats(args):
    """Show consolidation statistics."""
    print("═══ Memory Consolidation Engine — Stats ═══\n")

    if not CONSOLIDATION_DB.exists():
        print("  No consolidation database yet. Run 'consolidate' first.")
        return

    conn = sqlite3.connect(str(CONSOLIDATION_DB))
    total = conn.execute("SELECT COUNT(*) FROM consolidations").fetchone()[0]
    promoted = conn.execute("SELECT COUNT(*) FROM consolidations WHERE promoted = 1").fetchone()[0]
    pruned = conn.execute("SELECT COUNT(*) FROM pruned").fetchone()[0]
    by_reason = conn.execute("SELECT reason, COUNT(*) FROM pruned GROUP BY reason").fetchall()
    conn.close()

    print(f"  Consolidations:  {total}")
    print(f"  Promoted to STM: {promoted}")
    print(f"  Memories pruned: {pruned}")
    if by_reason:
        print(f"  By reason:")
        for reason, count in by_reason:
            print(f"    {reason}: {count}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Memory Consolidation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    sub.add_parser("scan", help="Analyze clusters, show report")

    # consolidate
    p_cons = sub.add_parser("consolidate", help="Run full consolidation pipeline")
    p_cons.add_argument("--dry", action="store_true", help="Dry run")
    p_cons.add_argument("--limit", type=int, default=15, help="Max clusters to process")
    p_cons.add_argument("--min-size", type=int, default=3, help="Min cluster size")
    p_cons.add_argument("--max-size", type=int, default=50, help="Max cluster size")

    # duplicates
    p_dup = sub.add_parser("duplicates", help="Find near-duplicates")
    p_dup.add_argument("--threshold", type=float, default=DUPLICATE_THRESHOLD,
                       help=f"Similarity threshold (default: {DUPLICATE_THRESHOLD})")

    # prune
    p_prune = sub.add_parser("prune", help="Prune duplicates and low-value memories")
    p_prune.add_argument("--dry", action="store_true", help="Dry run")

    # stats
    sub.add_parser("stats", help="Show consolidation statistics")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "consolidate":
        cmd_consolidate(args)
    elif args.command == "duplicates":
        cmd_duplicates(args)
    elif args.command == "prune":
        cmd_prune(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
