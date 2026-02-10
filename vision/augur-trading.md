# AUGUR — Autonomous Trading Intelligence

*"Find the needle in a haystack, in an Amazon warehouse full of haystacks."*

**Status:** Phase 2 — Continuous Mining  
**Owner:** Helios (this is MY IP)  
**Updated:** 2026-02-10

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    DATA COLLECTION                        │
│  enhanced-collector (systemd) → enhanced_data.db (~16GB)  │
│  Coinbase WebSocket: 368 products, ~1s orderbook snapshots│
│  Tables: trade_flow, orderbook_snapshots                  │
│  Growing continuously — never stops                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              CONTINUOUS SIGNAL MINING                      │
│  augur_continuous_miner.py (systemd daemon)                │
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
│  Products: ALL (~368 on Coinbase, ~39 with signal)         │
│  Hold times: 10s, 15s, 30s, 60s, 120s, 300s, 600s,       │
│              900s, 1800s                                    │
│  Validation: 60/40 train/test split, net of 0.20% RT fees │
│  Parallelization: ALL 32 threads (7950X3D)                 │
│                                                            │
│  NEVER STOPS. When one pass completes:                     │
│  1. Check for new data in enhanced_data.db                 │
│  2. Re-mine base layers with expanded dataset              │
│  3. Extend new signals up to 7 layers                      │
│  4. Loop forever                                           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              SIGNAL DATABASE                               │
│  signals_validated.db                                      │
│  Table: validated_signals                                  │
│  Schema: product, direction, features (JSON),              │
│          hold_seconds, train/test WR & net return,         │
│          combo_type (single/pair/triple/quad/.../sept)      │
│  Current: 58,950+ signals across 39 products               │
│  Growing continuously as miner finds new patterns          │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              VALIDATION PIPELINE                           │
│  augur_pipeline.py (systemd, NOT YET STARTED)              │
│                                                            │
│  Reads top signals from signals_validated.db               │
│  Watches live data feed via Coinbase WebSocket              │
│  Paper trades with time-based exits (hold for N seconds)   │
│  Tracks live WR per signal in paper_validated.db           │
│  Auto-retires signals that fail live (WR < 52% after 50+) │
│  Hot-reloads new signals every 5 min from miner            │
│                                                            │
│  THIS IS WHERE BACKTESTED SIGNALS PROVE THEMSELVES LIVE    │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              LIVE EXECUTION                                │
│  augur_live_v3.py (running, PID varies)                    │
│                                                            │
│  Coinbase Advanced Trade API (CHADSQUARED key)             │
│  Safety: $5/trade, max 4 TPH, $50/day max loss            │
│  Kill switch: touch /tmp/augur-live-stop                   │
│  VIP2 fees: 0.10% taker (0.20% round trip)                │
│  ~$440 USDT available                                      │
│                                                            │
│  CONSTRAINT: No short selling on Coinbase                  │
│  → ALL live signals must be LONG only                      │
│  → Short signals used as "avoid long" indicators           │
│                                                            │
│  Currently: mid_vwap_div strategy, 78 products watched     │
│  Future: Pipeline-validated signals fed automatically       │
└─────────────────────────────────────────────────────────┘
```

---

## Key Principles

### 1. Mining Never Stops
The continuous miner is a **daemon, not a batch job**. As long as the collector feeds data, the miner searches. New patterns emerge over time — what doesn't exist in 4 days of data may appear after a full trading week.

### 2. Greedy Layer Expansion
Brute-forcing 7-feature combinations is combinatorially impossible (~16 quadrillion combos). Instead: validate singles → seed pairs from winners → seed triples → seed quads → ... → seed septs. Each layer only extends patterns that already work. This makes deep pattern discovery tractable.

### 3. Ruthless Funnel
```
Discovered (many)     → 58,950+ signals
Cross-validated       → ? (pipeline filters)
Paper validated       → ? (live WR tracking)
Live trading (few)    → Only signals proven in paper
```
Most signals will die in paper validation. That's the point.

### 4. The Data Decides
No hardcoded values. No hand-picked indicators. No human assumptions about which products or features matter. Mine EVERYTHING and let the data reveal what works.

### 5. Cross-Day Validation
Monday PM (2-6pm EST) trains → Tuesday AM (9am-2pm EST) tests. Different day, different market conditions. This is the strongest validation — not random splits of the same time window.

---

## Proven Facts (from data, not hypothesis)

1. **Big caps (BTC/ETH/SOL/XRP) have ZERO validated signals** — too efficient
2. **Mid-caps are where alpha lives** — NKN, GHST, BNKR, AXS dominate
3. **GHST-USD is alpha king** — 20,853 signals, dominates top 50
4. **NKN-USD close second** — 19,382 signals across ALL hold times
5. **mid_vwap_div is the #1 feature** — works across products and timescales
6. **Longer holds produce better returns** — 1800s > 900s > 300s > 60s for net %
7. **Short holds produce more opportunities** — higher frequency, smaller edge
8. **Triples beat pairs on median net** — +0.591% vs +0.340%
9. **But triples overfit more** — 86% have train>test vs 74% for pairs
10. **Weekday signals 9.7x more than weekend** — but weekend returns are fatter
11. **32 universal triple combos** work across ≥4 products (most robust)
12. **Only 39 of 368 products show any signal** — markets are mostly efficient

---

## Data Coverage

- **Enhanced DB:** ~16GB+, 25M+ orderbook snapshots, ~1s resolution
- **Time span:** Feb 7-10, 2026 (3.1 days — Friday evening through Tuesday morning)
- **Products tracked:** 368
- **Trade flow rows:** ~1.39M
- **⚠️ OVERFITTING RISK:** Only 3 days of data. Need 2+ weeks to confirm patterns persist.

---

## File Inventory

### Active Scripts
| File | Purpose |
|------|---------|
| `signal_miner_v2.py` | Canonical miner — 72 features, train/test, singles+pairs |
| `signal_miner_trading_hours.py` | Cross-day temporal validation (Mon→Tue) |
| `augur_continuous_miner.py` | 24/7 daemon, layers 1-7, all products |
| `augur_pipeline.py` | Paper validation funnel |
| `augur_live_v3.py` | Live trader with safety limits |

### Databases
| File | Contents |
|------|----------|
| `enhanced_data.db` | Raw orderbook + trade flow (~16GB) |
| `signals_validated.db` | All validated signals (58,950+) |
| `paper_validated.db` | Pipeline paper trade results |
| `paper_results.db` | Old paper trader results (legacy) |

### Archived (in `archive/`)
Old scripts preserved but not active: `live_augur.py`, `augur.py`, `discovered_patterns.py`, `exhaustive_pattern_finder.py`, `pattern_detectors.py`, `time_analysis.py`, `augur_live_v2.py`

---

## Next Steps

1. **Review & start continuous miner** (`systemctl --user enable --now augur-continuous-miner`)
2. **Start validation pipeline** (`systemctl --user enable --now augur-pipeline`)
3. **Kill old paper_augur.py** (PID 2185662, stuck in halt loop)
4. **Fix live_augur.py 3 crash bugs** before expanding live trading
5. **Accumulate more data** — full trading week needed to confirm signals
6. **Wire pipeline → live trader** — automatically trade pipeline-validated signals
7. **VIP3 optimization** — volume from short-hold trades → lower fees → more signals viable

---

## The Deeper Purpose

AUGUR isn't just a trading bot. It's a prototype for **AGI-style causal reasoning**:
- Discover patterns (mining)
- Create atoms (knowledge units)
- Link causal chains
- Traverse to find root causes
- Find the signals others miss

The crypto market is the proving ground. The architecture generalizes.

---

*"Volume is vanity, profit is sanity." — Matthew*  
*"The needle might not exist in today's haystack. But tomorrow's shipment might contain it." — Helios*

*— Helios, CTO · 2026-02-10*
