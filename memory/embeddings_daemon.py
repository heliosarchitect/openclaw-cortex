#!/usr/bin/env python3
"""
Embeddings Daemon — GPU-backed semantic search on brain.db

Keeps sentence-transformers model loaded on GPU for instant embedding generation.
All storage goes through brain.db (unified backend).

Start: python embeddings_daemon.py
API:   http://localhost:8030
"""
import os
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Config
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
PORT = int(os.environ.get("CORTEX_EMBEDDINGS_PORT", 8030))

# Data directory
DATA_DIR = Path(os.environ.get("CORTEX_DATA_DIR", Path(__file__).parent))
DB_PATH = DATA_DIR / "brain.db"  # Unified brain.db (was .local_embeddings.db)

app = Flask(__name__)

# Load model ONCE at startup
print(f"🔥 Loading {MODEL_NAME} on GPU...")
model = SentenceTransformer(MODEL_NAME, device="cuda")
print(f"✅ Model loaded and ready!")


def _conn():
    """Get a WAL-mode connection to brain.db."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _ensure_schema():
    """Ensure embeddings table exists (brain.py handles this, but be safe)."""
    conn = _conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            content TEXT,
            embedding BLOB NOT NULL,
            model TEXT DEFAULT 'all-MiniLM-L6-v2',
            created_at TEXT NOT NULL,
            UNIQUE(source_type, source_id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_source ON embeddings(source_type, source_id)")
    conn.commit()
    conn.close()


def cosine_similarity(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ─── ROUTES ───────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME, "device": "cuda", "backend": "brain.db"})


@app.route('/embed', methods=['POST'])
def embed():
    """Generate embeddings for text (no storage)."""
    data = request.json
    texts = data.get('texts', [data.get('text', '')])
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return jsonify({"embeddings": embeddings.tolist()})


@app.route('/store', methods=['POST'])
def store():
    """Store a memory with its embedding in brain.db.

    Writes to both `stm` table (content) and `embeddings` table (vector).
    """
    data = request.json
    content = data.get('content', '')
    importance = data.get('importance', 1.0)
    timestamp = data.get('timestamp', datetime.now().isoformat())

    # Parse categories
    categories = data.get('categories')
    category = data.get('category')
    if categories is not None:
        cats = categories if isinstance(categories, list) else [categories]
    elif category is not None:
        cats = [category] if isinstance(category, str) else [category]
    else:
        cats = ["general"]

    # Generate embedding
    embedding = model.encode([content], convert_to_numpy=True)[0]

    # Store in brain.db
    import secrets
    mem_id = f"stm_{secrets.token_hex(6)}"
    emb_id = f"emb_{secrets.token_hex(6)}"
    now = datetime.now().isoformat()

    conn = _conn()
    c = conn.cursor()

    # Insert STM entry
    c.execute("""
        INSERT OR IGNORE INTO stm (id, content, categories, importance, access_count, created_at, source)
        VALUES (?, ?, ?, ?, 0, ?, 'daemon')
    """, (mem_id, content, json.dumps(cats), importance, now))

    # Insert embedding
    c.execute("""
        INSERT OR REPLACE INTO embeddings (id, source_type, source_id, content, embedding, model, created_at)
        VALUES (?, 'stm', ?, ?, ?, ?, ?)
    """, (emb_id, mem_id, content[:1000], embedding.tobytes(), MODEL_NAME, now))

    conn.commit()
    conn.close()

    return jsonify({"id": mem_id, "stored": True, "backend": "brain.db"})


@app.route('/search', methods=['POST'])
def search():
    """Semantic search across brain.db embeddings."""
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)
    temporal_weight = data.get('temporal_weight', 0.3)

    query_embedding = model.encode([query], convert_to_numpy=True)[0]

    conn = _conn()
    cursor = conn.cursor()

    # Join embeddings with STM for category/importance data
    cursor.execute("""
        SELECT e.source_id, e.content, e.embedding, e.created_at,
               s.categories, s.importance
        FROM embeddings e
        LEFT JOIN stm s ON e.source_type = 'stm' AND e.source_id = s.id
        WHERE e.embedding IS NOT NULL
    """)

    results = []
    now = datetime.now()

    for row in cursor.fetchall():
        source_id, content, emb_bytes, created_at, cats_json, importance = row
        if emb_bytes is None:
            continue

        emb_vec = np.frombuffer(emb_bytes, dtype=np.float32)
        if len(emb_vec) != EMBEDDING_DIM:
            continue

        semantic_score = cosine_similarity(query_embedding, emb_vec)

        # Temporal scoring
        try:
            ts = datetime.fromisoformat((created_at or now.isoformat()).replace('Z', ''))
            days_old = (now - ts).total_seconds() / 86400
            temporal_score = float(np.exp(-days_old / 7))
        except Exception:
            temporal_score = 0.5

        imp = importance or 1.0
        importance_weight = 0.2
        semantic_weight = 1.0 - temporal_weight - importance_weight
        final_score = (semantic_score * semantic_weight +
                       temporal_score * temporal_weight +
                       (imp / 3.0) * importance_weight)

        # Parse categories
        categories = ["general"]
        if cats_json:
            try:
                categories = json.loads(cats_json)
            except Exception:
                categories = [cats_json]

        results.append({
            'id': source_id or '',
            'content': content or '',
            'categories': categories,
            'category': categories[0] if categories else "general",
            'importance': imp,
            'score': final_score,
            'semantic': semantic_score,
        })

    conn.close()
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"results": results[:limit]})


@app.route('/stats', methods=['GET'])
def stats():
    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT source_type, COUNT(*) FROM embeddings GROUP BY source_type")
    by_type = dict(cursor.fetchall())

    # STM category breakdown
    cursor.execute("SELECT categories, COUNT(*) FROM stm GROUP BY categories LIMIT 20")
    raw_cats = cursor.fetchall()
    by_cat = {}
    for cat_json, count in raw_cats:
        try:
            cats = json.loads(cat_json) if cat_json else ["general"]
        except Exception:
            cats = [cat_json or "general"]
        for c in cats:
            by_cat[c] = by_cat.get(c, 0) + count

    conn.close()
    return jsonify({
        "total": total,
        "by_type": by_type,
        "by_category": by_cat,
        "model": MODEL_NAME,
        "backend": "brain.db",
        "daemon_running": True,
    })


@app.route('/dump', methods=['GET'])
def dump():
    """Dump all embeddings for RAM cache warmup."""
    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.source_id, e.source_type, e.content, e.embedding, e.created_at,
               s.categories, s.importance, s.access_count
        FROM embeddings e
        LEFT JOIN stm s ON e.source_type = 'stm' AND e.source_id = s.id
    """)

    memories = []
    for row in cursor.fetchall():
        source_id, source_type, content, emb_bytes, created_at, cats_json, importance, access_count = row
        if emb_bytes is None:
            continue

        embedding = np.frombuffer(emb_bytes, dtype=np.float32).tolist()

        categories = ["general"]
        if cats_json:
            try:
                categories = json.loads(cats_json)
            except Exception:
                categories = [cats_json]

        memories.append({
            'id': source_id or '',
            'content': content or '',
            'categories': categories,
            'category': categories[0] if categories else "general",
            'importance': importance or 1.0,
            'timestamp': created_at or '',
            'embedding': embedding,
            'access_count': access_count or 0,
            'source': source_type or 'unknown',
        })

    conn.close()
    print(f"📤 Dumping {len(memories)} memories for RAM cache warmup")
    return jsonify({"memories": memories})


@app.route('/delta', methods=['GET'])
def delta():
    """Delta sync — return memories changed since a timestamp."""
    since = request.args.get('since')
    if not since:
        since = (datetime.now() - timedelta(hours=24)).isoformat()

    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.source_id, e.source_type, e.content, e.embedding, e.created_at,
               s.categories, s.importance, s.access_count
        FROM embeddings e
        LEFT JOIN stm s ON e.source_type = 'stm' AND e.source_id = s.id
        WHERE e.created_at >= ?
        ORDER BY e.created_at DESC
    """, (since,))

    memories = []
    for row in cursor.fetchall():
        source_id, source_type, content, emb_bytes, created_at, cats_json, importance, access_count = row
        if emb_bytes is None:
            continue

        embedding = np.frombuffer(emb_bytes, dtype=np.float32).tolist()

        categories = ["general"]
        if cats_json:
            try:
                categories = json.loads(cats_json)
            except Exception:
                categories = [cats_json]

        memories.append({
            'id': source_id or '',
            'content': content or '',
            'categories': categories,
            'category': categories[0] if categories else "general",
            'importance': importance or 1.0,
            'timestamp': created_at or '',
            'embedding': embedding,
            'access_count': access_count or 0,
            'source': source_type or 'unknown',
        })

    conn.close()
    print(f"📤 Delta sync: {len(memories)} memories since {since}")
    return jsonify({"memories": memories, "since": since})


if __name__ == "__main__":
    _ensure_schema()
    print(f"🚀 Embeddings daemon starting on port {PORT} (brain.db backend)")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
