# Cortex Memory Plugin — Configuration Reference

**Plugin ID:** `cortex`  
**Config path:** `plugins.entries.cortex.config` in `~/.openclaw/openclaw.json`  
**Source schema:** `~/Projects/helios/extensions/cortex/openclaw.plugin.json`

## Current Settings (2026-02-09)

| Setting | Value | Default | Rationale |
|---------|-------|---------|-----------|
| hotTierSize | **500** | 100 | RAM-only, keeps top-accessed memories in fast cache. Free on 74GB machine. |
| activeSessionCapacity | **200** | 50 | RAM-only, more session messages cached. Free on 74GB machine. |
| maxContextTokens | **2000** | 1500 | Modest bump — tokens injected per turn. 1500 was working well; 2000 gives slight headroom without 2.5x burn. |
| truncateOldMemoriesTo | **250** | 180 | Slightly more context per old memory. Marginal token increase. |

## All Configurable Settings

### Core Toggles

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `enabled` | boolean | `true` | — | Enable Cortex memory enhancements |
| `autoCapture` | boolean | `true` | — | Automatically capture important conversation moments |
| `stmFastPath` | boolean | `true` | — | Check STM before full memory search (fast path) |
| `deltaSyncEnabled` | boolean | `true` | — | Background delta sync every 5 minutes |
| `prefetchEnabled` | boolean | `true` | — | Predictive category prefetching |

### Scoring Weights

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `temporalRerank` | boolean | `true` | — | Re-rank search results by recency |
| `temporalWeight` | number | `0.4` | 0–1 | Weight for temporal/recency scoring |
| `importanceWeight` | number | `0.3` | 0–1 | Weight for importance scoring |
| `relevanceThreshold` | number | `0.5` | 0–1 | Skip memories below this relevance score |

### Capacity & Performance (RAM-side)

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `stmCapacity` | integer | `50000` | 5–100,000 | Maximum items in short-term memory |
| `hotTierSize` | integer | `100` | 10–1,000 | Most-accessed memories kept in hot tier (RAM) |
| `activeSessionCapacity` | integer | `50` | 10–500 | Messages kept in active session RAM cache |

### Token Budget (API cost)

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| `maxContextTokens` | integer | `1500` | 100–10,000 | Base token budget for memory context injection per turn. Dynamic scaling adds more for complex conversations. **This is the primary API cost lever.** |
| `truncateOldMemoriesTo` | integer | `180` | 50–500 | Truncate old memories to this many characters (keeps sentences coherent) |

### Infrastructure

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `embeddingsUrl` | string | `http://localhost:8030` | GPU embeddings daemon URL for memory index |

## Cost Impact Analysis

- **RAM-only settings** (hotTierSize, activeSessionCapacity, stmCapacity): Zero API cost. Only limited by available system RAM.
- **Token settings** (maxContextTokens): Directly proportional to API cost. Each +500 tokens ≈ +500 input tokens per turn.
- **Truncation** (truncateOldMemoriesTo): Indirect — affects how much of each memory survives for injection.
- **Scoring weights** (temporalWeight, importanceWeight, relevanceThreshold): No cost, but affect *which* memories surface.

## How to Apply Changes

```bash
# Via OpenClaw gateway config.patch (from agent or CLI):
# Settings go under plugins.entries.cortex.config
# Example:
{
  "plugins": {
    "entries": {
      "cortex": {
        "config": {
          "hotTierSize": 500,
          "maxContextTokens": 2000
        }
      }
    }
  }
}
```

Triggers automatic SIGUSR1 restart.

---
*Last updated: 2026-02-09 22:30 EST*
