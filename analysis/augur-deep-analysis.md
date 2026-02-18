# AUGUR Paper Trading — Deep Performance Analysis
<!-- AI.TOC: AUGUR Paper Trading — Deep Performance Analysis — Read lines 1-20 for navigation.
  §1 Resolution (2026-02-10)                    → lines 10-32
  §2 Executive Summary                          → lines 33-48
  §3 1. Database Overview                       → lines 49-65
  §4 2. The Five Bugs                           → lines 66-150
  §5 3. Performance Analysis (With Caveats)     → lines 151-226
  §6 4. Vision vs Reality Gap                   → lines 227-260
  §7 5. Root Cause Analysis                     → lines 261-291
  §8 6. Recommendations (Priority Ordered)      → lines 292-334
  §9 7. What Might Actually Work                → lines 335-349
  §10 8. Conclusion                              → lines 350-359
  Total: 359 lines | Sections: 10
-->

**Date:** 2026-02-10 01:00 EST  
**Analyst:** Helios (sub-agent)  
**Data range:** 2026-02-07 18:03 → 2026-02-10 00:47 (~55 hours)  
**Status:** 🟢 RESOLVED — All 5 bugs fixed (2026-02-10 07:00 EST)

---

## Resolution (2026-02-10)

All 5 critical bugs identified below have been fixed in `paper_augur.py`. A live trader (`live_augur.py`) was also built.

| Bug | Fix | Date | Line(s) |
|-----|-----|------|---------|
| 1. Duplicate trade recording | Per-product position dedup (`key = product`) | 2026-02-08 | Already fixed during analysis period |
| 2. Cross-product pattern matching | Exact match on `conditions.get('product')` replacing substring `product not in name` | 2026-02-10 ~05:30 | L565 |
| 3. Missing indicators (`imbalance_ma`, `volume_proxy`, `price_ret_60`) | Added all three calculations to `get_orderbook_state()` from 60-snapshot window | 2026-02-10 ~05:30 | L513-540 |
| 4. Exit strategy mismatch | `max_hold` now reads pattern's backtested `lookahead` instead of fixed 300s | 2026-02-10 ~05:30 | L768, L787 |
| 5. Enhanced DB wrong path | Path corrected to `augur-collector/enhanced_data.db` | 2026-02-10 00:23 | L37 |

**Additional fixes applied:**
- Compound pattern evaluation added (multi-condition patterns with operator support) — L577-610
- Signal bridge: `_emit_live_signal()` writes `live_signal.json` for live trader — L741-755
- Pattern-specific `max_hold` passed through from `check_all_patterns` → `open_paper_position` → `trailing_stop_monitor`

**Next steps:** Reset `paper_results.db` and run clean 48-72 hour validation with fixed code. Pre-fix data below is retained for reference only.

---

---

## Executive Summary

AUGUR paper trading is reporting 48.2% WR and -78% cumulative PnL across 35,571 trade records. **But the real picture is worse and simultaneously better than it looks.** The 35,571 "trades" are only **~8,232 actual unique trades** — 75.6% are duplicates from a recording bug. The deduplicated performance is **43.4% WR** and **-75.9% PnL**.

The system has **five compounding bugs** that make the current data nearly useless for evaluating pattern quality:

1. **Duplicate trade recording** (75.6% of all records)
2. **Cross-product pattern matching** (`ETH-USD` matches `CBETH-USD`, `LSETH-USD` patterns)
3. **50% of loaded patterns reference indicators the paper trader can't evaluate**
4. **Exit strategy mismatch** between backtest and paper trading
5. **Enhanced DB was wrong path** until 30 min ago (pattern discovery ran blind)

**Bottom line:** We cannot determine whether AUGUR's patterns have real edge until these bugs are fixed. The current data is corrupted by implementation errors, not necessarily by bad patterns.

---

## 1. Database Overview

| Metric | Value |
|--------|-------|
| Total trade records | 35,571 |
| Unique trades (deduped) | ~8,232 |
| Duplicate records | 26,911 (75.6%) |
| Date range | Feb 7-10, 2026 (~55 hours) |
| Products traded | 276 |
| Patterns loaded (after dedup) | 363 |
| Patterns in patterns.db | 27,919 total / 738 passing filter |
| Overall WR (raw) | 48.2% |
| Overall WR (deduped) | 43.4% |
| Cumulative PnL | -77.95% (raw) / -75.91% (deduped) |

---

## 2. The Five Bugs

### Bug 1: Duplicate Trade Recording (CRITICAL)

**What:** 75.6% of trade records are duplicates — same timestamp, same product, same PnL, different pattern names.

**Evidence:** At 2026-02-08 20:06:10, there are **83 trade records** for SOL-USD, all with identical PnL of +0.1268%. They represent one physical trade recorded under 83 different pattern names that matched.

**Timeline:** The duplication ratio changes over time:
- Feb 7-8 (before 15:00): ratio=1.0x (no duplicates)
- Feb 8 15:00-23:00: ratio=3.5x to 11.7x (heavy duplication)
- Feb 9 00:00-04:00: ratio=4.1x to 8.0x 
- Feb 9 04:00+: ratio=1.0x (fixed — per-product dedup activated)

**Root cause:** The original code used `f"{pattern_name}_{product}"` as position key, allowing multiple positions per product. The fix changed to `key = product` (one position per product), but **all patterns that match are still being recorded as separate trade entries**. The `check_all_patterns` function returns only the best signal, but the `trailing_stop_monitor` records the trade under `pos['pattern']` — the single best pattern at entry time. The duplication comes from the period BEFORE the per-product dedup was applied, when each pattern opened its own position.

**Impact:** All aggregate statistics are inflated by 4-10x for the period Feb 8 15:00 to Feb 9 04:00. This distorts hourly analysis, product analysis, and overall WR.

### Bug 2: Cross-Product Pattern Matching (CRITICAL)

**What:** The pattern-matching check `if product not in name: continue` uses substring matching. When `product='ETH-USD'`, it matches patterns named `*CBETH-USD`, `*LSETH-USD`, and `*WETH-USD` because "ETH-USD" is a substring.

**Evidence:**
- **84% of ETH-USD trades** used CBETH-USD or LSETH-USD patterns
- ETH-USD with correct patterns: 10,885 trades, 51.7% WR, PnL=-65.52%
- ETH-USD patterns from wrong products made up the bulk of matches
- SOL-USD had 88.7% wrong-match trades (MSOL-USD, JITOSOL-USD patterns)

**Impact:** The two highest-volume products (ETH-USD: 12,297 trades, SOL-USD: 12,252 trades) are predominantly trading on signals calibrated for *different assets* with different volatility profiles, spreads, and liquidity. CBETH-USD patterns applied to ETH-USD are using thresholds computed from CBETH data — meaningless for ETH.

**Fix:** Replace `if product not in name: continue` with exact match: extract product from pattern conditions JSON and compare directly.

### Bug 3: Missing Indicators (HIGH)

**What:** 50% of loaded patterns (182/363) reference indicators that `get_orderbook_state()` doesn't compute.

| Indicator | In patterns.db | Computed by paper trader |
|-----------|:-:|:-:|
| spread_pct | ✅ | ✅ |
| imbalance | ✅ | ✅ |
| price_ret_30 | ✅ | ✅ |
| spread_change | ✅ | ✅ |
| **imbalance_ma** | ✅ | ❌ |
| **volume_proxy** | ✅ | ❌ |
| **price_ret_60** | ✅ | ❌ |

**Impact:** These 182 patterns silently never match. The paper trader loads them, checks each tick, gets `None` from `ob_state.get(indicator)`, and skips them. But they consume CPU and their "best_wr" might shadow a valid pattern if their stored WR is higher.

**Fix:** Either add computation for `imbalance_ma`, `volume_proxy`, `price_ret_60` to `get_orderbook_state()`, or filter them out during pattern loading.

### Bug 4: Exit Strategy Mismatch (HIGH)

**What:** Patterns were backtested with fixed lookahead windows. Paper trader uses a completely different exit strategy.

| Backtested with | Paper trader uses |
|----------------|-------------------|
| Fixed 30s lookahead (273 patterns) | 0.3% trailing stop |
| Fixed 60s lookahead (97 patterns) | 5 min max hold |
| Fixed 120s lookahead (47 patterns) | 15s min hold |
| Fixed 300s lookahead (106 patterns) | — |
| Fixed 600s lookahead (212 patterns) | — |

A pattern backtested with "price higher after 10 minutes" (600s lookahead) is being evaluated with "0.3% trailing stop within 5 minutes." These are fundamentally different questions:
- Backtest: "Is price higher at T+600s?"
- Paper: "Did price reach +0.3% from entry at any point in 15-300s, without first dropping 0.3% from peak?"

**Impact:** A pattern with 70% WR at 10-minute fixed lookahead could easily have 45% WR with trailing stop exits. The trailing stop kills trades that would have recovered. The 5-min timeout closes before the 10-min window the pattern was designed for.

### Bug 5: Enhanced DB Wrong Path (FIXED 30 min ago)

The `ENHANCED_DB` path pointed to `~/Projects/Chad_Volume_tracker/enhanced_data.db` (non-existent) instead of `~/Projects/augur-collector/enhanced_data.db` (actual 16GB database). This means:
- Pattern discovery's `run_discovery()` ran hourly but returned 0 every time
- `_load_pairs_from_data()` fell back to `{'ETH-USD', 'BTC-USD', 'SOL-USD'}` whenever it used the wrong path
- `get_orderbook_state()` couldn't query enhanced data — all pattern checks got empty `ob_state` and no patterns matched

**Wait — this is worse than Bug 3.** If `get_orderbook_state()` was failing entirely because the DB didn't exist, then NO exhaustive patterns would have matched AT ALL. Yet we have 34,867 exhaustive pattern trades. This means either:
1. The code caught the exception silently and still matched patterns somehow, OR
2. The pairs loaded from somewhere else initially

Looking at the code: `get_orderbook_state` has a bare `except Exception: pass` that returns `{}`, so when enhanced_db was wrong, it returned empty dict → `ob_state.get(indicator)` returns `None` → no patterns match. **But we have trades.** This suggests the path was corrected at some point during the run, or the fallback pairs worked with the WebSocket data directly for persistence patterns.

The 704 persistence pattern trades (48.7% WR, +3.33% PnL) may be the only legitimate data, since those use WebSocket trade data, not the enhanced DB.

---

## 3. Performance Analysis (With Caveats)

Despite the bugs, the data reveals structural patterns worth analyzing:

### 3.1 By Direction

| Direction | Trades | WR | PnL | Avg PnL |
|-----------|--------|-----|-----|---------|
| up (LONG) | 34,831 | 48.3% | -110.48% | -0.003% |
| down (SHORT) | 740 | 43.1% | +32.53% | +0.044% |

**91:1 LONG bias.** Of 363 loaded patterns, 331 are LONG and only 32 are SHORT. The system is overwhelmingly bullish. In a market that trended down during this period, that's catastrophic.

### 3.2 By Hour

The most telling dimension:

| Hour | Trades | WR | PnL | Note |
|------|--------|-----|-----|------|
| H11 | 634 | 27.9% | -78.33% | Worst WR |
| H16 | 3,984 | 45.5% | -255.77% | Worst PnL (highest volume) |
| H20 | 5,690 | 34.2% | -417.59% | CATASTROPHIC |
| H17 | 1,343 | 83.6% | +133.71% | Best WR |
| H22 | 2,011 | 65.1% | +153.54% | Strong |
| H21 | 4,349 | 54.4% | +294.33% | Best PnL |
| H13 | 2,232 | 54.5% | +132.66% | Solid |

**H20 alone accounts for -417.59% PnL** — more than the total cumulative loss. The regime detection (halt at <30% rolling WR) only triggered once during H20. It wasn't fast enough.

H17's 83.6% WR is suspicious — ETH-USD had 97.2% WR in that hour, suggesting a strong directional move that happened to align with the LONG bias, not genuine pattern edge.

### 3.3 By Product

| Product | Trades | WR | PnL | Note |
|---------|--------|-----|-----|------|
| ETH-USD | 12,297 | 52.5% | -29.21% | Biggest loser by volume |
| SOL-USD | 12,252 | 53.0% | +56.63% | Only major winner |
| AVAX-USD | 2,267 | 31.1% | -25.16% | Terrible (blacklisted) |
| BTC-USD | 398 | 56.0% | +2.43% | Low volume but profitable |
| XRP-USD | 340 | 52.4% | +8.11% | Small but consistent |

ETH-USD + SOL-USD account for 69% of all trades. The concentration is extreme.

### 3.4 By Indicator Type

| Indicator | Trades | WR | PnL | Avg PnL |
|-----------|--------|-----|-----|---------|
| imbalance | 18,319 | 48.7% | -16.28% | -0.001% |
| price_ret_30 | 6,728 | 48.5% | -63.94% | -0.010% |
| spread_pct | 6,601 | 46.7% | -5.59% | -0.001% |
| spread_change | 3,218 | 47.0% | +4.53% | +0.001% |
| persistence | 704 | 48.7% | +3.33% | +0.005% |

**price_ret_30** is the worst performer by far (-63.94% PnL). Imbalance has the most trades but barely negative. Spread_change and persistence are the only net positive indicators.

### 3.5 Backtest vs Paper WR Gap

Across 453 patterns with 20+ paper trades:
- **Average gap:** -12.1% (paper WR exceeds backtest WR on average!)
- **308 of 453 patterns** (68%) have paper WR HIGHER than backtest WR
- **Maximum positive gap:** +45.3% (backtest 75%, paper 29.7%)
- **Maximum negative gap:** -62.7% (backtest 11.1%, paper 73.8%)

This is **backwards from what you'd expect**. Normally backtest WR > paper WR. The fact that paper WR exceeds backtest for 68% of patterns suggests the paper trader is evaluating patterns incorrectly (Bug 2: cross-product matching, Bug 4: different exit strategies) and getting lucky on some.

### 3.6 Winner vs Loser Asymmetry

| | Count | Avg PnL | Total PnL |
|---|---|---|---|
| Winners | 17,133 | +0.188% | +3,223.63% |
| Losers | 18,438 | -0.179% | -3,301.58% |

The asymmetry is nearly symmetric: winners average +0.188%, losers average -0.179%. After fees (0.05% maker), any WR below ~51.5% is net negative. At 48.2% WR, the system is barely underwater per-trade, but the volume amplifies small per-trade losses into massive cumulative losses.

---

## 4. Vision vs Reality Gap

### What VISION.md Promises

The vision document is exceptional — 93KB, deeply thought-out, with a clear understanding of the problems. Key architectural promises:

1. **Pattern funnel**: Discovered (27,919) → Cross-validated (~3,000) → Significant (~800) → Paper-validated (~200) → Live candidates (~50) → Live (~20)
2. **Pattern lifecycle**: discovered → backtested → paper_active → paper_validated → live_candidate → live → retired
3. **No hardcoded thresholds** — percentile-based
4. **Cross-validation**: train/test split before any pattern reaches paper
5. **WR decay tracking**: auto-retirement when patterns stop working
6. **Exit strategy alignment**: paper should test what backtest tested
7. **Meta-layer**: learning which discovery methods produce durable patterns

### What Actually Exists

| Feature | Vision | Reality |
|---------|--------|---------|
| Pattern funnel | 6-stage with filters | **None** — all 363 deduped patterns go straight to execution |
| Cross-validation | k-fold or temporal split | **None** — patterns trained and tested on same data |
| Pattern lifecycle | 7 stages with evidence gates | **None** — patterns are permanent, no retirement |
| Exit strategy | Aligned with backtest | **Mismatched** — trailing stop vs fixed lookahead |
| Indicator alignment | Paper evaluates what patterns measure | **50% mismatch** — 182 patterns reference uncomputed indicators |
| Product matching | Exact | **Substring** — cross-contamination |
| Direction balance | Both LONG and SHORT | **91:1 LONG bias** |
| WR decay tracking | Rolling WR per pattern | **None** — only aggregate regime detection |
| Risk management | Position sizing, correlation limits, kill switch | **Only regime halt** (50-trade rolling WR < 30%) |
| Data path | Correct | **Wrong until 30 min ago** |

The vision doc's own self-assessment in Section 3 is accurate:
> *"TODAY: All 27,919 are shoved directly into execution. No funnel. That's why WR is 47.4%."*

---

## 5. Root Cause Analysis

### Why is WR ~48% instead of the 60-70% the patterns claim?

1. **No validation funnel.** The 60% WR threshold in patterns.db comes from backtesting on the SAME data that discovered the patterns. This is textbook overfitting. A pattern that looks 70% WR in-sample could be 50% out-of-sample.

2. **Cross-product contamination.** ETH-USD is trading on CBETH-USD signals. The thresholds were calibrated for a different asset.

3. **Exit strategy mismatch.** Patterns tested with "is price higher after X seconds" are evaluated with "trailing stop + timeout." Different questions yield different win rates.

4. **LONG-only in a mixed/down market.** 331/363 patterns are LONG. Any period of downward price action wipes them out.

5. **No time-of-day filtering.** H20 alone causes -417.59% PnL. The patterns don't know that H20 is toxic.

6. **High trade frequency.** ETH-USD averages 224 trades/hour (before dedup fix). Most of these are noise-level signals re-entering every 15 seconds.

### The Cascade

```
Wrong enhanced_db path → no real-time data → pattern discovery blind
    → stale patterns from initial brute-force only
Cross-product matching → 84% of ETH-USD trades on wrong signals
Missing indicators → 50% of patterns silently never fire
Exit mismatch → the other 50% are tested with wrong exit logic
No funnel → overfit patterns promoted directly to execution
LONG bias → one-directional risk in two-directional markets
    → aggregate: ~random performance with systematic drag from fees + bad signals
```

---

## 6. Recommendations (Priority Ordered)

### P0 — Fix Before Any More Trading

1. **Fix cross-product matching.** Replace `if product not in name` with exact match on `conditions.get('product')`. This is a one-line fix that eliminates 84% of ETH-USD's bad trades.

2. **Add missing indicators.** Implement `imbalance_ma`, `volume_proxy`, `price_ret_60` in `get_orderbook_state()`, or filter these patterns out at load time.

3. **Align exit strategies.** Either:
   - Change paper trader to use fixed lookahead (matching backtest), OR
   - Re-run discovery with trailing stop exit (matching paper trader)
   The first is easier. Add an exit_strategy field to patterns and respect it.

4. **Reset paper_results.db.** Current data is corrupted by all five bugs. Archive it, start fresh with fixed code.

### P1 — Build the Pattern Funnel

5. **Cross-validation in discovery.** Split data into train/test (70/30 or temporal). Only promote patterns that hold WR on held-out data.

6. **Rolling WR per pattern** (not just aggregate). Retire patterns whose individual rolling WR drops below threshold.

7. **Time-of-day gating.** Don't trade patterns in hours where they've shown < 45% WR (e.g., blacklist H20 for most patterns).

### P2 — Structural Improvements

8. **Direction balance.** Actively seek SHORT patterns. 91:1 LONG bias is existential risk.

9. **Reduce trade frequency.** One trade per product per 5 minutes is plenty. The current 224/hour on ETH-USD is noise-trading.

10. **Position sizing.** Kelly criterion or fixed fractional instead of flat 10%.

11. **Correlation limits.** Don't go LONG on ETH-USD, SOL-USD, BTC-USD, LINK-USD simultaneously — they're all correlated.

### P3 — The Vision Gap

12. **Build the lifecycle.** Even a simple 3-stage version (discovered → paper_testing → validated/retired) would be transformative.

13. **Dashboard.** The vision doc has excellent dashboard specs. Build them — they'd expose these bugs instantly.

14. **Meta-layer.** Track which indicator types produce durable patterns vs noise.

---

## 7. What Might Actually Work

Despite all the bugs, there are faint signals of real edge:

- **BTC-USD** (56.0% WR, +2.43%) on only 7 patterns — small but consistent
- **XRP-USD** (52.4% WR, +8.11%) — spread_pct patterns seem to work here
- **SOL-USD** (53.0% WR, +56.63%) — the only high-volume profitable product
- **spread_change indicator** (+4.53% PnL) — the only net-positive indicator type
- **H12-H14, H17, H21-H22** — consistently profitable hours
- **persistence patterns** (48.7% WR, +3.33%) — the only discovery-based patterns, slightly positive

The pattern `price_ret_30_above_90pct_JITOSOL-USD` has 73.8% paper WR on 61 trades (backtest WR was only 11.1% — suggesting it's picking up a strong trend signal that the fixed-lookahead backtest missed). Worth investigating.

---

## 8. Conclusion

**AUGUR's vision is sound. The implementation has critical bugs that make current results meaningless as pattern validation.**

The good news: the bugs are identifiable and fixable. The bad news: every trade record in the current database is contaminated by at least one bug, so we need to start validation over from scratch after fixes.

The single highest-leverage change is **fixing cross-product matching** + **resetting the database**. That alone would produce clean data. Combined with exit strategy alignment and the pattern funnel, AUGUR could start answering the question it was designed to answer: do these upstream signals actually lead?

Right now, it can't answer that question. The implementation noise drowns the signal.
