# Tonight Sprint — Helios Upgrades (2026-02-12)

Matthew directive: "Come up with 5 upgrades that you and Nova can implement tonight"

## 5 Upgrades

### 1. 🧠 Cortex Dedup + Memory Hygiene (Helios solo)
**Problem**: 2,885 STM entries, many duplicates (3+ copies of AUGUR STRATEGIC PIVOT, trading memories). Wastes context tokens and confuses semantic search.
**Deliverable**: Run cortex_dedupe, clean stale memories, update MEMORY.md index. Target: <2,000 unique STM entries.
**Time**: 30 min

### 2. 📊 AUGUR Embedding-Based Signal Discovery (Nova builds, Helios deploys)  
**Problem**: Matthew said "think of mining signals like embeddings — discover connections." Current miner uses brute-force percentile thresholds. Missing latent structure.
**Deliverable**: `augur_embedding_miner.py` — embed raw market features into vector space, cluster, find regime transitions that precede profitable moves. Use all-MiniLM-L6-v2 on RTX 5090.
**Time**: 2 hours
**Repo**: Helios/augur-trading (new branch: `embedding-signals`)

### 3. 🏗️ LBF Documentation Standards (Nova builds)
**Problem**: Matthew said "if there isn't documentation for software products and upgrades, build that out." Multiple repos missing README/CHANGELOG/ARCHITECTURE.
**Deliverable**: Audit all Helios org repos on Gitea, add missing docs to each:
- `Helios/brain-db` — has README, needs CHANGELOG + ARCHITECTURE
- `Helios/augur-trading` — has README (Nova wrote), needs CHANGELOG + ARCHITECTURE  
- `Helios/n8n-workflows` — has ARCHITECTURE + README, needs CHANGELOG
- `Helios/llm-fleet` — needs all 3
**Time**: 1 hour

### 4. 🔌 Wazuh-Sentinel Integration (Nova builds, Helios deploys)
**Problem**: Wazuh is running with 5 agents but no alerting pipeline. Security events go nowhere.
**Deliverable**: n8n workflow that polls Wazuh API for high-severity alerts (level 12+) → stores in brain.db → sends Signal notification for critical events. ClawHub has `security-sentinel` skill to explore.
**Time**: 1 hour

### 5. 📈 AUGUR Fee-Aware Signal Filter (Helios solo or Nova)
**Problem**: 140 live trades today, ALL losers because gross edge < 0.20% fee. Signals that look great in backtest die on fees.
**Deliverable**: Add `min_gross_return` gate to live executor. Only trade signals where backtested gross return > 2× fee rate (>0.40%). Also add per-product fee awareness (limit_only products = 0% maker fee).
**Time**: 30 min

## Execution Order
1. Fee-aware filter (quick win, prevents future losses) — 30 min
2. Memory hygiene (clean before building more) — 30 min  
3. LBF docs (Nova sub-agent) — 1 hour
4. Wazuh integration (Nova sub-agent) — 1 hour
5. Embedding signal discovery (biggest, most impactful) — 2 hours

## Standards
- All work goes in Gitea repos under Helios org
- Every repo gets README.md, CHANGELOG.md, ARCHITECTURE.md
- Tests where applicable
- Git commits with descriptive messages
- Daily log updated throughout
