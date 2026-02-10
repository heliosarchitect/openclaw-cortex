# AUGUR Pattern Quality Audit

**Date:** 2026-02-10 01:00 EST  
**Auditor:** Helios  
**Scope:** Pattern discovery, validation, and live trading pipeline

---

## Executive Summary

AUGUR's paper trading achieves **48.2% WR on 35,571 trades** — net negative PnL of -78%. The system is trading slightly worse than random. Six root causes identified, ordered by impact:

1. **No train/test split** — patterns are fit and scored on the same data
2. **Massive multiple-testing problem** — 972 hypotheses tested per pair with no correction
3. **333 of 738 active patterns use indicators that can't be computed in live trading**
4. **Only 2.5 days of data** — not enough for regime-diverse pattern discovery
5. **Trailing stop + spread mechanics** eat profits on tiny crypto moves
6. **LONG bias** — 97.9% of trades are LONG, SHORT direction rarely triggered

---

## 1. Pattern Database Overview

| Metric | Value |
|--------|-------|
| Total patterns | 27,919 |
| Active (WR≥60%, occ≥100) | 738 |
| After dedup in paper_augur | ~363 |
| Created on | Feb 8, 2026 (single batch) |
| Data window | Feb 7-10 (2.5 days) |
| Indicators | 7 primary + 3 derived |
| Products | ~230 pairs |

### Win Rate Distribution (all patterns)
| Bucket | Count | Avg Occurrences |
|--------|-------|-----------------|
| <50% | 24,754 | 1,235 |
| 50-55% | 1,217 | 2,919 |
| 55-60% | 655 | 1,988 |
| 60-65% | 444 | 607 |
| 65-70% | 281 | 251 |
| 70-75% | 165 | 439 |
| 75-80% | 120 | 184 |
| 80-85% | 128 | 101 |
| 85-90% | 64 | 129 |
| 90%+ | 91 | 88 |

**Red flag:** High-WR patterns have LOW occurrences. This is the textbook signature of overfitting — extreme results from small samples.

### Indicators Used
| Indicator | Pattern Count | Computable Live? |
|-----------|--------------|-----------------|
| spread_pct | 4,188 | ✅ Yes |
| price_ret_60 | 4,151 | ❌ No |
| imbalance_ma | 4,082 | ❌ No |
| imbalance | 4,033 | ✅ Yes |
| price_ret_30 | 4,018 | ✅ Yes |
| volume_proxy | 3,960 | ❌ No |
| spread_change | 3,458 | ✅ Yes |

**333 of 738 active patterns (45%) use indicators that `get_orderbook_state()` cannot compute.** These patterns silently fail (return None → skip), meaning the trader only has ~400 usable patterns, not 738.

---

## 2. Paper Trading Results

### Overall
- **35,571 trades** over ~2.5 days
- **48.2% WR**, -0.0022% avg PnL, **-78% total PnL**
- 7.4% of trades have exactly 0% PnL (spread-killed)
- 9.3% of trades have |PnL| < 0.01% (noise-dominated)

### Direction Bias
| Direction | Trades | WR | Avg PnL |
|-----------|--------|-----|---------|
| up (LONG) | 34,839 | 48.3% | -0.003% |
| down (SHORT) | 744 | 43.3% | +0.044% |

97.9% of trades are LONG. The SHORT patterns that DO fire actually have positive PnL but are extremely rare.

### Temporal Performance
| Hour (UTC) | Trades | Paper WR |
|-----------|--------|----------|
| 12 | 1,892 | 57.2% |
| 13 | 2,232 | 54.5% |
| 17 | 1,343 | **83.6%** |
| 21 | 4,349 | 54.4% |
| 22 | 2,011 | 65.1% |
| 20 | 5,690 | **34.2%** |
| 11 | 634 | **27.9%** |
| 0-4 | 2,798 | **34.3%** |

Hour 17 and 22 are strong; hours 20, 11, and 0-4 are toxic. Time-filtering alone could add 5-10% overall WR.

### Daily Degradation
| Date | Trades | WR | Avg PnL |
|------|--------|----|---------|
| Feb 7 | 59 | 40.7% | +0.010% |
| Feb 8 | 14,752 | 51.9% | -0.005% |
| Feb 9 | 20,653 | 45.6% | -0.000% |
| Feb 10 | 107 | 23.4% | -0.033% |

**WR is degrading daily.** Feb 8 (discovery day) had 51.9%, Feb 9 dropped to 45.6%, Feb 10 collapsed to 23.4%. Classic overfitting decay — patterns work best near discovery time and degrade as market evolves.

---

## 3. Historical vs Live Win Rate Gap

### Aggregate
| Metric | Value |
|--------|-------|
| Avg historical WR (matched patterns) | 37.5% |
| Avg paper WR | 45.9% |
| Avg gap | **-8.3%** |
| Patterns where paper BEATS historical | 334/539 (62%) |
| Patterns with gap > 20% (overfit) | 53 |
| Patterns with gap > 10% | 113 |

**Counterintuitive:** Most patterns do BETTER in paper than in history. This is because:
1. Historical WR includes ALL patterns (many <50%), but only WR≥60% are traded
2. The dedup filter selects the best WR per combo, which regresses to mean in live
3. Paper trader takes only the highest-WR signal per product (best-of selection bias)

### The Worst Offenders (Hist WR >> Paper WR)
| Pattern | Hist WR | Paper WR | Gap | Trades |
|---------|---------|----------|-----|--------|
| spread_pct_below_10pct_POLS-USD | 90.9% | 27.3% | +63.6% | 11 |
| price_ret_30_below_70pct_SWFTC-USD | 81.0% | 25.0% | +56.0% | 16 |
| spread_pct_below_20pct_PYR-USD | 62.9% | 8.3% | +54.6% | 12 |
| spread_change_above_80pct_PLUME-USD | 51.0% | 0.0% | +51.0% | 12 |
| imbalance_above_50pct_AIOZ-USD | 50.2% | 0.0% | +50.2% | 10 |

These are textbook overfit — high historical WR on few samples, complete failure in live.

### By Indicator
| Indicator | n | Hist WR | Paper WR | Gap | % Profitable |
|-----------|---|---------|----------|-----|--------------|
| imbalance_ma | 108 | 28.7% | **51.0%** | -22.3% | 67% |
| imbalance | 212 | 39.8% | 41.9% | -2.2% | 43% |
| price_ret_30 | 105 | 37.7% | 44.9% | -7.2% | 44% |
| spread_change | 56 | 36.8% | 43.3% | -6.5% | 46% |
| spread_pct | 120 | 45.7% | 40.2% | +5.4% | 38% |
| persistence | 6 | 46.2% | 47.1% | -0.9% | 33% |

**`imbalance_ma` is the best live performer (51% WR, 67% profitable) but CAN'T be computed in live trading** — it's missing from `get_orderbook_state()`.

### By Lookahead
| Lookahead (sec) | n | Hist WR | Paper WR | Gap |
|-----------------|---|---------|----------|-----|
| 30 | 353 | 37.0% | 45.0% | -8.0% |
| 60 | 86 | 33.4% | 47.4% | -14.0% |
| 120 | 26 | 36.5% | 44.8% | -8.3% |
| 300 | 53 | 43.9% | 38.9% | +5.0% |
| 600 | 83 | 46.3% | 38.4% | +7.9% |

Short lookaheads (30-120s) outperform in live. Long lookaheads (300-600s) underperform. But the paper trader uses a fixed 5-minute max hold with 0.3% trailing stop — **it doesn't use the pattern's own lookahead value.**

---

## 4. Root Cause Analysis

### 4.1 NO TRAIN/TEST SPLIT (Critical)

The `exhaustive_pattern_finder.py` computes thresholds and win rates **on the same data**:

```python
# Line ~126: Threshold computed from percentile
threshold = df[indicator].quantile(percentile / 100)

# Line ~133: Signal tested on SAME dataframe  
signal_indices = df.index[mask].tolist()

# Line ~145: Win rate computed on same indices
results.append(pnl)  # ← SAME data used for threshold AND evaluation
```

There is **zero holdout, zero walk-forward, zero cross-validation.** The WR is purely in-sample. With 2.5 days of data, even a random signal will show high WR on some percentile/lookahead combos.

**Fix:** Walk-forward validation — use first 70% for threshold computation, last 30% for WR evaluation. Or time-based split: discover on day 1, validate on day 2.

### 4.2 MASSIVE MULTIPLE TESTING (Critical)

Per pair, the exhaustive finder tests:
- 7 indicators × 2 directions × 9 percentiles × 6 lookaheads = **756 hypotheses**

With 230 pairs: **173,880 total hypotheses tested.** With no multiple-testing correction (Bonferroni, FDR), finding patterns with 60%+ WR by chance is **guaranteed.**

At 5% false positive rate: ~8,694 spurious patterns expected. The system found 27,919 total patterns — a large portion are statistical noise.

**Fix:** Apply Bonferroni correction (α/N) or FDR (Benjamini-Hochberg). Require minimum edge > baseline + 3*SE(baseline).

### 4.3 MISSING INDICATORS IN LIVE TRADING (High)

The exhaustive finder discovers patterns using 7 indicators. `get_orderbook_state()` only computes 4:

| Indicator | Discovered | Computable Live |
|-----------|-----------|----------------|
| spread_pct | ✅ | ✅ |
| imbalance | ✅ | ✅ |
| price_ret_30 | ✅ | ✅ |
| spread_change | ✅ | ✅ |
| **price_ret_60** | ✅ | ❌ |
| **imbalance_ma** | ✅ | ❌ |
| **volume_proxy** | ✅ | ❌ |
| **compound** | ✅ | ❌ |

This means 45% of "active" patterns silently never fire. The dedup logic picks the "best WR per combo" — if the best is an uncomputable indicator, the whole combo is dead.

**Fix:** Add `imbalance_ma`, `price_ret_60`, and `volume_proxy` to `get_orderbook_state()`:
```python
# In get_orderbook_state(), add:
if len(rows) >= 60:
    result['price_ret_60'] = (rows[0][1] - rows[59][1]) / rows[59][1] * 100
    result['imbalance_ma'] = sum(
        (r[3] - r[4]) / (r[3] + r[4] + 1e-9) for r in rows[:30]
    ) / 30
    result['volume_proxy'] = sum(r[3] + r[4] for r in rows[:30]) / 30
```

### 4.4 INSUFFICIENT DATA WINDOW (High)

All 27,909 patterns were discovered on **Feb 8, 2026** using data from **Feb 7 12:49 to Feb 8 ~12:00** — roughly 24 hours. This single market regime becomes the "truth" for pattern detection.

Crypto markets exhibit:
- Bull/bear regimes
- Weekend vs weekday effects
- Correlation shifts (BTC dominance changes)
- Liquidity regime changes

2.5 days covers none of this meaningfully.

**Fix:** Minimum 2 weeks of data before discovery. Ideally 30+ days covering multiple market regimes.

### 4.5 EXIT MECHANISM MISMATCH (Medium)

The exhaustive finder tests with fixed-time exits (`future_return[lookahead]`), but the paper trader uses a 0.3% trailing stop with 5-minute max hold — **regardless of the pattern's optimal lookahead.**

A pattern discovered with 600s lookahead (10 minutes) will be exited at 5 minutes max in paper trading. A pattern with 30s optimal lookahead gets the same 5-minute window.

Additionally, the trailing stop discovery code exists in the exhaustive finder but **no trailing-stop patterns were saved** (all 27,919 are `fixed_time` exit type). The trailing stop simulation code runs but its results aren't persisted.

**Fix:** Use pattern-specific exit parameters. Store the optimal lookahead and use it as max hold time in live trading.

### 4.6 BASELINE WR COMPUTATION ERROR (Medium)

The exhaustive finder uses `baseline_wr = 0.5` (coin flip):
```python
baseline_wr = 0.5  # Random
edge = win_rate - baseline_wr
```

But the actual baseline varies dramatically by lookahead:
- 30s lookahead: baseline WR ~43-50% (markets have slight upward drift)
- 600s lookahead: baseline WR ~33-47% (more variance, less predictable)

The inline discovery in `paper_augur.py` computes per-product baselines correctly, but the exhaustive finder (which created 27,909 of 27,919 patterns) does not.

**Fix:** Compute per-product, per-lookahead baseline WR from the data. Require edge > 3 standard errors above baseline.

---

## 5. Specific Recommendations

### Immediate (Fix today)

1. **Add missing indicators to `get_orderbook_state()`** — `imbalance_ma`, `price_ret_60`, `volume_proxy`. This alone unlocks 333 dormant patterns, including the best-performing `imbalance_ma` (51% live WR).

2. **Add hour-based filtering** — Skip hours 0-4, 11, 20 (WR < 40%). Trade only hours 12-14, 17, 21-22 (WR > 52%). This is the single easiest WR boost.

3. **Kill patterns with 0% paper WR** — 12 patterns have 0% WR on 5+ trades. Remove them immediately.

### Short-term (This week)

4. **Implement walk-forward validation** in the exhaustive finder:
   - Split data 70/30 by time
   - Compute thresholds on first 70%
   - Score WR on last 30%
   - Only keep patterns where out-of-sample WR > 55%

5. **Multiple testing correction** — Apply FDR at 5%. This will kill most of the 27,919 patterns but the survivors will be real signals.

6. **Use pattern-specific exit parameters** — Each pattern has an optimal lookahead stored in conditions. Use it as the max hold time instead of a fixed 5 minutes.

### Medium-term (Next 2 weeks)

7. **Accumulate 30 days of data** before re-running discovery. The collector is gathering data at ~750K orderbook snapshots/hour — let it run.

8. **Add trade flow indicators** — The enhanced collector stores `trade_flow` (buy/sell volume buckets) and `orderbook_depth` (10 levels). These are not used by either the finder or the trader. Buy/sell imbalance in actual trades is a stronger signal than orderbook imbalance (which can be spoofed).

9. **Implement regime detection** — The current `_check_regime` halts at 30% rolling WR over 50 trades. Better: detect market regime (trending/ranging/volatile) and only trade patterns that match the current regime.

10. **Track paper trading results per-indicator** — The current system tracks per-pattern, but with 27K patterns, individual stats are noisy. Aggregate by indicator type to find which signal families work.

---

## 6. What's Actually Working

Not all bad news:

- **`imbalance_ma` indicator** — 51% live WR, 67% of patterns profitable. But it's not being computed in live! Fix this first.
- **Hour 17 EST** — 83.6% WR on 1,343 trades. Something real is happening here (likely US market close).
- **Hour 22 EST** — 65.1% WR on 2,011 trades.
- **SHORT direction** — Only 744 trades but +0.044% avg PnL (positive!). SHORT signals work but are extremely rare.
- **JITOSOL-USD** — Multiple patterns with 73-80% paper WR. This pair may have genuine predictable microstructure.
- **CBETH-USD** — `spread_change` patterns showing 78.6% WR on 14 trades.

---

## 7. Architecture Diagram

```
CURRENT FLOW (broken):

enhanced_collector.py → enhanced_data.db (16GB, ✅ working)
                              ↓
exhaustive_pattern_finder.py → patterns.db (27,919 patterns)
  ⚠️ Wrong DB path (was Chad_Volume_tracker, now fixed)
  ⚠️ No train/test split
  ⚠️ No multiple testing correction
  ⚠️ Computes 7 indicators, live only handles 4
                              ↓
paper_augur.py → paper_results.db (35K trades, 48.2% WR)
  ⚠️ Missing 3 indicators (imbalance_ma, price_ret_60, volume_proxy)
  ⚠️ Fixed 5-min exit regardless of pattern optimal lookahead
  ⚠️ No time-of-day filter
  ⚠️ 97.9% LONG bias

PROPOSED FLOW:

enhanced_collector.py → enhanced_data.db
                              ↓
exhaustive_pattern_finder_v2.py → patterns_v2.db
  ✅ Walk-forward validation (70/30 time split)
  ✅ FDR multiple testing correction
  ✅ Per-product baseline WR
  ✅ Min 2 weeks data
                              ↓
paper_augur_v2.py → paper_results_v2.db
  ✅ All 7 indicators computed
  ✅ Pattern-specific exit parameters
  ✅ Hour filtering (only trade WR>50% hours)
  ✅ Regime detection
```

---

*End of audit. Total patterns analyzed: 27,919. Paper trades analyzed: 35,571. Critical issues: 6. Estimated WR improvement from fixes: +8-15%.*
