# AUGUR Sequence Pattern Analysis — Baseline-Adjusted

**Date:** 2026-02-10 08:36 EST  
**Product:** ETH-USD  
**Data:** 33,246 five-second bars (~48 hours, Feb 8-10 2026)  
**Price range:** $1,994 – $2,145 (net move: -5.2%)  
**Validation:** First-half / second-half split + baseline subtraction

---

## ⚠️ Critical Methodology Note: Baseline Bias

**ETH dropped 5.2% over the analysis window.** This creates a massive SHORT bias:

| Horizon | Baseline SHORT WR | Baseline LONG WR |
|---------|-------------------|-------------------|
| 1 min   | 54.6%             | 45.4%             |
| 2 min   | 54.4%             | 45.6%             |
| 5 min   | 56.6%             | 43.4%             |
| 10 min  | 55.0%             | 45.0%             |

A "60% WR SHORT" pattern only has **5.4pp of real edge** at 1-min horizon — the rest is just the trend. All results below are **baseline-adjusted**: we report edge ABOVE what a random entry would give.

---

## 🏆 Tier 1: Validated Patterns with Strong Edge (>10pp over baseline in both train AND test)

These are the real signals. They beat baseline by >10 percentage points in BOTH halves of the data.

### 1. Consecutive Strong Buy Flow → LONG (5-10min)

**Pattern:** 2+ minutes where buy/sell volume ratio exceeds 3:1  
**Edge:** +30-46pp over baseline  
**Mechanism:** Sustained heavy buying isn't noise — it's conviction

| Variant | Horizon | Train WR | Train Edge | Test WR | Test Edge | Train n | Test n |
|---------|---------|----------|------------|---------|-----------|---------|--------|
| 2min @ 3:1 ratio | 5min | 87.2% | +46.2pp | 76.5% | +30.8pp | 39 | 34 |
| 2min @ 3:1 ratio | 10min | 64.6% | +20.6pp | 74.4% | +28.4pp | 48 | 39 |
| 3min @ 2:1 ratio | 10min | 60.4% | +16.4pp | 70.4% | +24.4pp | 159 | 108 |
| 2min @ 2:1 ratio | 10min | 63.0% | +19.0pp | 56.4% | +10.4pp | 235 | 218 |

**⚡ Best signal in the entire dataset.** 2 minutes of 3:1 buy flow → LONG for 5 minutes: 82% WR with +39pp edge. Even the weaker variant (2:1 for 2 min) shows +10-19pp edge with 200+ signals.

**Concern:** Sample sizes are small (34-39 test signals for the strongest). Need more data to confirm the 3:1 variants. The 2:1 / 10min variant has 218 test signals — more reliable.

### 2. Low Activity → SHORT (1-5min)

**Pattern:** Trading activity drops below 20th percentile  
**Edge:** +7-21pp over baseline  
**Mechanism:** Quiet markets tend to resolve in the direction of the trend (which was down). This may be trend-following disguised as a pattern.

| Variant | Horizon | Train WR | Train Edge | Test WR | Test Edge | Train n | Test n |
|---------|---------|----------|------------|---------|-----------|---------|--------|
| Low activity | 1min | 80.0% | +21.1pp | 68.4% | +16.6pp | 85 | 38 |
| Low activity | 2min | 67.1% | +7.1pp | 69.6% | +19.2pp | 304 | 184 |
| Low activity | 5min | 65.9% | +6.9pp | 67.4% | +13.1pp | 989 | 660 |
| Low act → vol surge | 1min | 70.4% | +11.5pp | 81.0% | +29.1pp | 27 | 42 |
| Low act → vol surge | 2min | 80.3% | +20.3pp | 70.2% | +19.9pp | 66 | 84 |
| Low act → vol surge | 5min | 65.5% | +6.5pp | 69.5% | +15.2pp | 168 | 141 |

**⚠️ Caveat:** "Low activity → SHORT" works because ETH was trending down. In an uptrend, this might reverse. The **low_act→vol_surge** sequence is more interesting — it suggests that volume returning after quiet periods amplifies whatever direction comes next.

### 3. High Activity → LONG (5-10min)

**Pattern:** Trading activity above 80th percentile  
**Edge:** +5-15pp over baseline  
**Mechanism:** High-activity periods during a downtrend had a contrarian LONG edge

| Variant | Horizon | Train WR | Train Edge | Test WR | Test Edge | Train n | Test n |
|---------|---------|----------|------------|---------|-----------|---------|--------|
| High activity | 5min | 55.5% | +14.6pp | 53.3% | +7.6pp | 839 | 2,174 |
| High activity | 10min | 57.5% | +13.5pp | 52.4% | +6.4pp | 1,110 | 2,849 |
| High activity | 2min | 49.9% | +9.9pp | 54.9% | +5.2pp | 457 | 1,400 |

**Large sample sizes** (2000+ test signals). Edge is moderate (5-8pp in test) but very consistent. Combined with the flow patterns: high activity + buy flow = strongest conviction.

---

## 🥈 Tier 2: Validated Patterns with Moderate Edge (5-10pp in both train and test)

### 4. Order Book Imbalance Signals

| Pattern | Dir | Horizon | WR | Edge | Train Edge | Test Edge | Train n | Test n |
|---------|-----|---------|-----|------|------------|-----------|---------|--------|
| ob_ask_heavy (asks > bids) | SHORT | 1min | 63.5% | +8.9pp | +10.1pp | +8.7pp | 158 | 291 |
| imb_shift_bear_fast | SHORT | 1min | 61.9% | +7.3pp | +6.0pp | +8.4pp | 131 | 226 |
| ob_imb_flip_bull | LONG | 1min | 51.2% | +5.8pp | +6.3pp | +5.5pp | 196 | 300 |

**Insight:** Order book imbalance has a real but small edge at 1-minute. Ask-heavy book → SHORT is the strongest. The imbalance flip (rapid shift toward bearish) is also a valid signal.

### 5. Volume Imbalance & Sell Surge

| Pattern | Dir | Horizon | WR | Edge | Train Edge | Test Edge | Train n | Test n |
|---------|-----|---------|-----|------|------------|-----------|---------|--------|
| vol_imb_bear | SHORT | 1min | 61.4% | +6.8pp | +6.1pp | +7.3pp | 197 | 318 |
| sell_surge_3x | SHORT | 2min | 60.8% | +6.4pp | +6.8pp | +7.1pp | 151 | 270 |
| bid_halved_1m | SHORT | 1min | 60.7% | +6.1pp | +6.8pp | +6.0pp | 210 | 353 |

**Insight:** When sell volume dominates, or bid size collapses, there's a reliable 6-7pp SHORT edge at 1-2 minute horizons.

### 6. Spread Dynamics

| Pattern | Dir | Horizon | WR | Edge | Train Edge | Test Edge | Train n | Test n |
|---------|-----|---------|-----|------|------------|-----------|---------|--------|
| spread_narrow | LONG | 2min | 57.1% | +11.5pp | +14.8pp | +8.3pp | 53 | 164 |

**Insight:** Tight spreads slightly favor LONG entries. Makes intuitive sense — market makers tighten spreads when confident about fair value, which happens more during stability/accumulation.

---

## ❌ Patterns That FAILED Validation

These looked promising in raw WR but are actually just the trend:

| Pattern | Dir | Raw WR | Baseline | Real Edge | Verdict |
|---------|-----|--------|----------|-----------|---------|
| vol_accel_buy | SHORT | 63.7% | 56.6% | +7.1pp (5min) | Train: +12pp, Test: -1.2pp → **OVERFIT** |
| momentum_down | SHORT | 59.2% | 54.6% | +4.6pp | Below 5pp threshold |
| ask_3x_1m | SHORT | 59.5% | 54.6% | +4.9pp | Barely above noise |
| spread_compress_5m | SHORT | 58.1% | 56.6% | +1.5pp | **No real edge** |
| ob_imb_flip_bear | SHORT | 60.3% | 54.6% | +5.7pp | Mixed: train 4.3pp, test 6.8pp |

**The "buy volume acceleration → SHORT" paradox explained:** Buy surges happen slightly more often when price is already falling (mean reversion attempts that fail). The "edge" is really just trend persistence — in an uptrend, buy surges would predict LONG. This is NOT a real signal.

---

## 🔬 Regime Analysis

Regime distribution: Ranging 47.6% | Trend Down 18.3% | Trend Up 18.0% | Volatile 16.1%

### Bearish Signals by Regime

| Pattern | Trend Down | Ranging | Trend Up | Volatile |
|---------|-----------|---------|----------|----------|
| sell_surge SHORT | **69.0%** | **75.9%** | 51.4% | 52.2% |
| imb_shift_bear_fast SHORT | **82.4%** | **70.5%** | 55.4% | 50.4% |
| ob_imb_flip_bear SHORT | **82.7%** | **67.5%** | 51.7% | 50.3% |
| vol_accel_buy SHORT | **87.5%** | **68.9%** | 52.8% | 39.1% |
| momentum_down SHORT | **65.1%** | **72.2%** | 52.9% | 47.6% |

**Key finding:** Bearish patterns work in **Trend Down + Ranging** but are coin flips in **Trend Up + Volatile**. This is critical for implementation — patterns must be regime-aware.

### The "vol_accel_buy → SHORT" Regime Split

This is the most dramatic: **87.5% WR in downtrends, 39.1% in volatile markets.** It's pure trend-following — buy exhaustion signals work when the trend is already down. In choppy markets, buy surges actually lead to UP moves. A single pattern, two opposite outcomes depending on regime.

---

## 📊 Consecutive Flow Patterns: The Real Discovery

The strongest finding is **sustained directional flow predicting continuation**. This is the "leading indicator" we're looking for:

```
IF buy_volume / sell_volume > 3:1 for 2+ consecutive minutes
THEN price moves up 0.2%+ within 5 minutes (82% of the time)
Baseline-adjusted edge: +39pp
```

This passes every validation check:
- ✅ Train WR 87%, Test WR 77% (both far above baseline)
- ✅ Edge present in both halves
- ✅ Intuitive mechanism (heavy buying = real demand)
- ⚠️ Only concern: sample size (73 total signals in 48h ≈ 1.5/hour)

The weaker but higher-frequency variant:
```
IF buy_volume / sell_volume > 2:1 for 2+ consecutive minutes  
THEN price moves up within 10 minutes (60% of the time)
Baseline-adjusted edge: +15pp, 453 signals in 48h ≈ 9.4/hour
```

---

## 🎯 Actionable Recommendations

### Implement Now (High Confidence)

1. **Consecutive buy flow 2:1 for 2min → LONG (10min timeout)**
   - Edge: +15pp, 450+ signals/48h
   - Good frequency, validated, intuitive
   
2. **Consecutive buy flow 3:1 for 2min → LONG (5min timeout)**
   - Edge: +39pp, but only ~1.5 signals/hour
   - High conviction, lower frequency
   
3. **Low activity → volume surge → SHORT (2min timeout)**
   - Edge: +20pp, ~3 signals/hour
   - ⚠️ May be trend-dependent, revalidate in uptrend

### Implement with Regime Filter

4. **ob_ask_heavy → SHORT (1min)** — Only in ranging + trend_down regimes
5. **imb_shift_bear_fast → SHORT (1min)** — Only in ranging + trend_down regimes
6. **sell_surge → SHORT (2min)** — Only in ranging + trend_down regimes

### Need More Data

7. **Consecutive 3:1 flow patterns** — Only 34-39 test signals. Need 200+ to be confident
8. **spread_narrow → LONG (2min)** — 164 test signals, promising but needs confirmation
9. **Regime-conditional LONG patterns** — Not enough data in trend_up periods

### Do NOT Implement

- **vol_accel_buy → SHORT** — It's pure trend-following, will flip in uptrends
- **spread_compress_5m → SHORT** — No real edge after baseline adjustment
- Any pattern with <5pp baseline-adjusted edge in test set

---

## 🔮 Next Steps

1. **Collect more data** — 48h is barely enough. Need 1-2 weeks for robust validation
2. **Multi-regime validation** — Run the same analysis on a different 48h window (ideally one with ETH going UP) to confirm which patterns are regime-dependent vs universal
3. **Combine signals** — The consecutive flow + ob_imbalance combination could be even stronger
4. **Exit strategy matching** — These patterns were validated with fixed-horizon returns. The paper trader uses trailing stops. Need to backtest with actual exit logic.
5. **Implement the flow pattern** — It's the clearest edge with the best theoretical backing. Start with the 2:1/2min variant for higher frequency.

---

## Methodology

### Data Sources
- `orderbook_snapshots`: bid/ask size, spread, mid_price (sampled ~every second)
- `trade_flow`: aggregated buy/sell volume per second
- `trades`: individual trades with size and side
- All resampled to 5-second bars, merged, forward-filled

### Feature Categories
- **Base:** mid_price, bid/ask_size, spread_pct, buy/sell_volume, trade_count
- **Rolling:** 1-min and 5-min moving averages and std devs
- **Rate of change:** Feature ratios vs 1-min and 5-min ago
- **Imbalance:** (bid-ask)/(bid+ask) for order book, (buy-sell)/(buy+sell) for volume
- **Surge detection:** Current value / 5-min rolling average
- **Regime:** Based on 5-min momentum and volatility classification

### Validation Protocol
1. **Minimum signal count:** 25 in each half (50 total)
2. **Baseline adjustment:** Compare pattern WR to random-entry WR at same horizon
3. **Train/test split:** First 24h vs last 24h (temporal, no data leakage)
4. **Edge threshold:** Must beat baseline by >5pp in BOTH train and test to be ✅ VALID
5. **Win/loss definition:** >0.2% move in predicted direction = win, >0.2% against = loss

---

*Generated by AUGUR Sequence Pattern Miner — baseline-adjusted analysis*
