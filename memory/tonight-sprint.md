# Tonight Sprint — 5 HELIOS Self-Improvements (2026-02-12)

Matthew directive: "5 Helios upgrades you and Nova can implement tonight"
Note: AUGUR, LBF docs, Wazuh integration are AFTER these 5.

## 5 Helios-Centric Upgrades

### 1. 🧠 Memory Hygiene + Dedup (Helios solo, 30 min)
**Problem**: 2,885 STM entries with known triplicates. Wastes context tokens every turn via semantic retrieval. Stale memories pollute search results.
**Deliverable**: Run cortex_dedupe (merge at 0.90 threshold), prune obsolete entries (old V2 trading bugs, superseded decisions), verify <2,000 clean STM entries remain.
**Impact**: Cleaner context injection = better reasoning per turn.

### 2. 🔄 H0-4: Workspace File Internalization (Nova builds, Helios deploys, 2 hr)
**Problem**: OpenClaw loads 8 .md files EVERY TURN (~5,200 tokens wasted). SOUL.md, USER.md, IDENTITY.md rarely change but are re-injected constantly.
**Deliverable**: Modify `src/agents/workspace.ts` — add content hash caching. Only inject file content when hash changes from last turn. Cache hashes in session state.
**Key files**: `src/agents/workspace.ts` (line 237 `loadWorkspaceBootstrapFiles`), `src/agents/bootstrap-files.ts`, `src/agents/system-prompt.ts` (line 542)
**Impact**: ~5,200 tokens/turn saved = ~40% context overhead reduction.
**Repo**: ~/Projects/helios/ (OpenClaw source)

### 3. 📊 Self-Monitoring Dashboard (Nova builds, 1 hr)
**Problem**: No visibility into Helios performance metrics. Can't track: tokens/turn, response latency, memory hit rate, sub-agent success rate, heartbeat efficiency.
**Deliverable**: `helios_monitor.py` — Python script that parses session transcripts + brain.db to compute:
  - Avg tokens per turn (trend over time)
  - Memory retrieval relevance score
  - Sub-agent spawn count + success rate
  - Heartbeat OK vs action ratio
  - Context reset frequency
  Output: JSON metrics + optional Prometheus endpoint (feeds existing Prometheus on hpserver1)
**Impact**: Can't improve what you can't measure.
**Repo**: Helios/brain-db or new Helios/helios-monitor

### 4. 🤖 SYNAPSE Protocol V2 (Nova builds, 1 hr)
**Problem**: SYNAPSE v1 works but is primitive — no message expiry, no priority queue, no structured task delegation format, no acknowledgment verification.
**Deliverable**: Upgrade brain.db SYNAPSE tables:
  - Add `expires_at` column (auto-cleanup stale messages)
  - Add `task_status` enum (pending/in_progress/complete/failed) for delegation tracking
  - Add `result` field for sub-agent to write deliverables back
  - Add `context` field for attaching relevant file paths/data
  - Matching brain.py methods + CLI commands
  Tests: 10+ new tests covering delegation lifecycle
**Impact**: Better Nova delegation = more autonomous overnight work.
**Repo**: Helios/brain-db

### 5. 🧬 Smart Context Budgeting (Nova builds, 1 hr)
**Problem**: Cortex injects memories by recency + access count, but doesn't consider: current task relevance, token budget remaining, or diminishing returns from similar memories.
**Deliverable**: `smart_context.py` — middleware that:
  - Scores candidate memories by cosine similarity to current turn (not just recency)
  - Deduplicates semantically similar candidates before injection
  - Respects a configurable token budget (e.g., 4,000 tokens max for memory injection)
  - Prioritizes diversity across categories (don't inject 5 AUGUR memories when only 1 is relevant)
  Integration point: brain.py `get_context_memories()` method
**Impact**: Higher signal-to-noise in every turn's context window.
**Repo**: Helios/brain-db

## Execution Order
1. Memory Hygiene (quick win, clean foundation) — 30 min
2. H0-4 Internalization (biggest token savings) — 2 hr (Nova)
3. SYNAPSE V2 (enables better delegation for rest of night) — 1 hr (Nova)
4. Smart Context Budgeting (compound improvement) — 1 hr (Nova)
5. Self-Monitoring Dashboard (measure everything) — 1 hr (Nova)

## THEN: AUGUR fee filter, LBF docs, Wazuh integration

## Standards
- All work in Gitea repos (Helios org)
- README.md, CHANGELOG.md, ARCHITECTURE.md in every repo
- Tests for all new code
- Git commits with descriptive messages
- Daily log updated throughout
