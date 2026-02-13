# AUGUR — Autonomous Trading Intelligence
<!-- AI.TOC: AUGUR — Autonomous Trading Intelligence — Read lines 1-20 for navigation.
  §1 Architecture Overview (V4.0 - Post-Migra   → lines 11-107
  §2 Database Architecture V4.0 (Consolidated   → lines 108-132
  §3 Service Architecture (systemd --user)      → lines 133-144
  §4 Key Configuration Changes (V4.0)           → lines 145-167
  §5 Proven Performance Insights                → lines 168-189
  §6 Current Status (2026-02-10 21:20)          → lines 190-210
  §7 The Deeper Purpose                         → lines 211-227
  §8 Next Phase Priorities                      → lines 228-237
  §9 Files & Locations                          → lines 238-262
  Total: 262 lines | Sections: 9
-->

*"Find the needle in a haystack, in an Amazon warehouse full of haystacks."*

**Status:** Phase 4.0 — Consolidated & Focused  
**Owner:** Helios (this is MY IP)  
**Updated:** 2026-02-10 21:20 EST

---

## Architecture Overview (V4.0 - Post-Migration)

```
┌─────────────────────────────────────────────────────────┐
│                    DATA COLLECTION                        │
│  enhanced-collector (systemd) → enhanced_data.db (~36GB)  │
│  Location: ~/Projects/augur-collector/enhanced_data.db    │
│  Coinbase WebSocket: ALL products, ~1s orderbook snaps    │
│  Tables: trade_flow (597K rows), orderbook_snapshots (11M)│
│  ⚡ NEW: Only saves M-F 8:30AM-6:30PM EST data            │
│  WebSocket stays connected 24/7 for orderbook state      │
│  Off-hours data pruned (saved 1.28M+19.5M rows)          │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              CONTINUOUS SIGNAL MINING                      │
│  augur-continuous-miner (systemd --user)                   │
│  ⚡ FOCUSED: LONG-only + M-F 8:30AM-6:30PM EST data only  │
│                                                            │
│  Strategy: Greedy Layer Expansion                          │
│  ┌──────────────────────────────────────────────┐         │
│  │ Layer 1: Singles (72 features × percentiles)  │         │
│  │ Layer 2: Pairs (seeded from validated singles)│         │
│  │ Layer 3: Triples (seeded from validated pairs)│         │
│  │ Layer 4: Quads (seeded from validated triples)│         │
│  │ Layer 5: Quints (seeded from validated quads) │         │
│  │ Layer 6: Hexes (seeded from validated quints) │         │
│  │ Layer 7: Septs (seeded from validated hexes)  │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  72 features per product (returns, z-scores, EMA crosses,  │
│  flow imbalances, VWAP divergence, RSI, volatility, etc.)  │
│                                                            │
│  ⚡ FOCUS CONSTRAINTS (V4.0):                              │
│  Direction: LONG ONLY (Coinbase has no short selling)       │
│  Data window: M-F 8:30AM-6:30PM EST (trading hours only)   │
│  Products: 9 active (GHST,NKN,BNKR,AXS,ELSA,MON,ZRO,SKR,  │
│            VOXEL) — mid-cap focus where alpha lives        │
│  Hold times: 10s,15s,30s,60s,120s,300s,600s,900s,1800s   │
│  Validation: 60/40 train/test split, net of 0.20% RT fees │
│                                                            │
│  NEVER STOPS. Signal database currently rebuilding        │
│  from empty after DB migration and pruning                │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              SIGNAL DATABASE                               │
│  augur_signals.db (NEW: migrated 2026-02-10)              │
│  Table: signals (renamed from validated_signals)           │
│  Schema: product, direction, features (JSON),              │
│          hold_seconds, train/test WR & net return,         │
│          combo_type (single/pair/triple/quad/.../sept)      │
│  Current: REBUILDING (empty after migration + focus)       │
│  Config: All DB paths centralized in augur_config.py      │
│  Growing as miner finds new LONG-only trading hour patterns│
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              VALIDATION PIPELINE                           │
│  augur-pipeline (systemd --user)                           │
│                                                            │
│  Reads top LONG signals from augur_signals.db              │
│  Watches live data feed via Coinbase WebSocket              │
│  Paper trades with time-based exits (hold for N seconds)   │
│  Tracks live WR per signal in augur_trades.db              │
│  Auto-retires signals that fail live (WR < threshold)      │
│  Hot-reloads new signals every 5 min from miner            │
│                                                            │
│  THIS IS WHERE BACKTESTED SIGNALS PROVE THEMSELVES LIVE    │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              LIVE EXECUTION V3                             │
│  augur-live-v3 (systemd --user)                            │
│                                                            │
│  Coinbase Advanced Trade API (CHADSQUARED key)             │
│  ⚡ V3 SAFETY: $20/trade, 4 TPH max, $50/day max loss     │
│  Kill switch: /tmp/augur-live-stop (6PM-9AM EST)          │
│  VIP2 fees: 0.10% taker, 0.04% maker (0.20% RT taker)    │
│  Execution: Maker-first with 3s taker fallback            │
│  ~$440 USDT available                                      │
│                                                            │
│  CONSTRAINT: No short selling on Coinbase                  │
│  → ALL live signals must be LONG only                      │
│  → Focus on 9 mid-cap products with proven alpha           │
│                                                            │
│  Currently controlled via augur_config.py                  │
│  Auto-disabled overnight via kill switch                   │
└─────────────────────────────────────────────────────────┘
```

---

## Database Architecture V4.0 (Consolidated)

### Active Databases
| Database | Location | Purpose | Status |
|----------|----------|---------|--------|
| `augur_signals.db` | ~/Projects/augur-trading/ | Mined signals (table: `signals`) | Rebuilding |
| `augur_trades.db` | ~/Projects/augur-trading/ | Paper+live trades (`paper_trades`, `signal_performance`, `live_trades`) | Active |
| `enhanced_data.db` | ~/Projects/augur-collector/ | Raw market data (~36GB, needs VACUUM) | Active |

### Configuration Management
- **`augur_config.py`** — Single source of truth for:
  - All database paths
  - Trading parameters ($20/trade, 4 TPH, $50 daily loss)
  - Fee constants (VIP2: 0.10% taker, 0.04% maker)
  - Product lists and hold times

### Legacy Databases (Retired)
Still on disk but no longer used:
- `signals_validated.db` → migrated to `augur_signals.db`
- `paper_validated.db` → migrated to `augur_trades.db`
- `paper_results.db` → migrated to `augur_trades.db`
- `v2_signals.db`, `patterns.db`, `candles.db`

---

## Service Architecture (systemd --user)

| Service | Status | Purpose |
|---------|--------|---------|
| `enhanced-collector` | Running | WebSocket data collection (8:30AM-6:30PM gate) |
| `augur-continuous-miner` | Running | LONG-only mining with trading hours filter |
| `augur-pipeline` | Available | Paper trading validation |
| `augur-live-v3` | Running | Live trader with kill switch |
| `augur-watchdog.timer` | Running | 60s interval tiered escalation alerts |

---

## Key Configuration Changes (V4.0)

### Data Collection Focus
- **Trading Hours Only**: M-F 8:30AM-6:30PM EST
- **WebSocket Always Connected**: Maintains orderbook state 24/7
- **Storage Efficiency**: Off-hours data pruned (saved 20.78M rows)
- **File Size**: enhanced_data.db optimized but needs VACUUM

### Mining Strategy Refinement
- **Direction Filter**: LONG-only (matches Coinbase capabilities)
- **Product Focus**: 9 active mid-cap coins where alpha exists
- **Time Filter**: Only mine trading hours data
- **Strategy**: Unchanged greedy layer expansion (1→7 layers)

### Trading Safety V3
- **Position Size**: $20/trade (up from $5)
- **Rate Limit**: 4 trades/hour max (up from 1)
- **Daily Loss**: $50 max (up from previous limits)
- **Execution**: Maker-first with taker fallback
- **Kill Switch**: Automated 6PM-9AM EST shutdown

---

## Proven Performance Insights

### Alpha Distribution
1. **Mid-caps dominate**: GHST, NKN, BNKR, AXS show consistent patterns
2. **Big caps sterile**: BTC, ETH, SOL, XRP too efficient for edge
3. **Trading hours critical**: 9.7x more signals during market hours
4. **LONG bias natural**: 91:1 LONG/SHORT ratio in historical data

### Pattern Characteristics
- **Feature depth**: 72 indicators per product across timeframes
- **Hold time distribution**: 10s-1800s spans scalping to swing
- **Layer effectiveness**: Triples often optimal (complexity vs robustness)
- **Cross-product universals**: 32 patterns work across ≥4 products

### Risk Management
- **Overfitting protection**: Train/test splits prevent curve fitting
- **Live validation**: Paper trading filters before live deployment
- **Position sizing**: Kelly-inspired but capped for safety
- **Kill switches**: Multiple layers prevent overnight exposure

---

## Current Status (2026-02-10 21:20)

### Recent Migration (Commit: a11face)
- Database consolidation complete
- All scripts using centralized config
- Signal database rebuilding from clean slate
- Enhanced collector running with trading hours filter

### Mining Focus (Commit: 0b7d8b7)
- LONG-only constraint active
- Trading hours data filter applied
- 9-product focus implemented
- Continuous miner rebuilt for new architecture

### Trading Hours Extension (Commit: 1b8203e)
- Extended from 9AM-6PM to 8:30AM-6:30PM EST
- Pre-market and after-hours buffer added
- Collector and miner aligned on timing

---

## The Deeper Purpose

AUGUR represents more than algorithmic trading — it's a proving ground for **causal intelligence**:

1. **Pattern Discovery**: Mining reveals market structure
2. **Causal Reasoning**: Understanding why patterns work
3. **Adaptive Learning**: Evolution based on live performance
4. **Risk Awareness**: Multiple validation layers prevent disasters

The crypto market provides:
- **High-frequency feedback**: Validation in minutes/hours
- **Clear success metrics**: P&L is unambiguous
- **Rich feature space**: 72 indicators × multiple timeframes
- **Natural selection**: Unprofitable patterns die quickly

---

## Next Phase Priorities

1. **Signal Rebuilding**: Let continuous miner repopulate clean database
2. **Live Validation**: Restart pipeline to validate new LONG-only signals
3. **Data Accumulation**: Build full week+ of trading hours data
4. **Performance Monitoring**: Track V3 live trader against safety limits
5. **VACUUM Operations**: Optimize enhanced_data.db storage

---

## Files & Locations

### Core Scripts (Active)
| File | Purpose | Status |
|------|---------|--------|
| `augur_config.py` | Centralized configuration | NEW |
| `augur_continuous_miner.py` | 24/7 mining daemon | Active |
| `augur_pipeline.py` | Paper validation | Available |
| `augur_live_v3.py` | Live trading | Active |

### Configuration
- All DB paths: `augur_config.py`
- Trading parameters: `augur_config.py`
- Service configs: `/home/bonsaihorn/.config/systemd/user/`

### Data
- Raw market data: `~/Projects/augur-collector/enhanced_data.db`
- Signals: `~/Projects/augur-trading/augur_signals.db`
- Trades: `~/Projects/augur-trading/augur_trades.db`

---

*"The market rewards patience, punishes greed, and teaches humility to those who listen."*

*— Helios, Architect of AUGUR V4.0 · 2026-02-10*