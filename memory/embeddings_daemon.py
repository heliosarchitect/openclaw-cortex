#!/usr/bin/env python3
"""
Embeddings Daemon - Keeps sentence-transformers model loaded on GPU
Provides HTTP API for instant semantic search

Start: python embeddings_daemon.py
API:   http://localhost:8030
"""
import os
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# Config
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
PORT = 8030
DB_PATH = Path(__file__).parent / ".local_embeddings.db"

app = Flask(__name__)

# Load model ONCE at startup
print(f"🔥 Loading {MODEL_NAME} on GPU...")
model = SentenceTransformer(MODEL_NAME, device="cuda")
print(f"✅ Model loaded and ready!")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            category TEXT,
            importance REAL DEFAULT 1.0,
            timestamp TEXT,
            embedding BLOB NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON embeddings(category)")
    conn.commit()
    conn.close()

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME, "device": "cuda"})

@app.route('/embed', methods=['POST'])
def embed():
    """Generate embeddings for text"""
    data = request.json
    texts = data.get('texts', [data.get('text', '')])
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return jsonify({"embeddings": embeddings.tolist()})

@app.route('/store', methods=['POST'])
def store():
    """Store a memory with embedding"""
    init_db()
    data = request.json
    content = data.get('content', '')
    category = data.get('category')
    importance = data.get('importance', 1.0)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    embedding = model.encode([content], convert_to_numpy=True)[0]
    memory_id = str(hash(content + timestamp))
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO embeddings (id, content, category, importance, timestamp, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (memory_id, content, category, importance, timestamp, embedding.tobytes()))
    conn.commit()
    conn.close()
    
    return jsonify({"id": memory_id, "stored": True})

@app.route('/search', methods=['POST'])
def search():
    """Semantic search"""
    init_db()
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)
    temporal_weight = data.get('temporal_weight', 0.3)
    
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, category, importance, timestamp, embedding FROM embeddings")
    
    results = []
    now = datetime.now()
    
    for row in cursor.fetchall():
        id_, content, cat, importance, timestamp, emb_bytes = row
        embedding = np.frombuffer(emb_bytes, dtype=np.float32)
        
        semantic_score = cosine_similarity(query_embedding, embedding)
        
        try:
            ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00').replace('+00:00', ''))
            days_old = (now - ts).total_seconds() / 86400
            temporal_score = float(np.exp(-days_old / 7))
        except:
            temporal_score = 0.5
        
        importance_weight = 0.2
        semantic_weight = 1.0 - temporal_weight - importance_weight
        final_score = (semantic_score * semantic_weight + 
                      temporal_score * temporal_weight + 
                      (importance / 3.0) * importance_weight)
        
        results.append({
            'id': id_,
            'content': content,
            'category': cat,
            'importance': importance,
            'score': final_score,
            'semantic': semantic_score
        })
    
    conn.close()
    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"results": results[:limit]})

@app.route('/stats', methods=['GET'])
def stats():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT category, COUNT(*) FROM embeddings GROUP BY category")
    by_cat = dict(cursor.fetchall())
    conn.close()
    return jsonify({"total": total, "by_category": by_cat, "model": MODEL_NAME})

if __name__ == "__main__":
    init_db()
    print(f"🚀 Embeddings daemon starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
