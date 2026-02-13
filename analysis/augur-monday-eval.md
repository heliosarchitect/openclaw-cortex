# AUGUR Phase 0 — First Monday Performance Evaluation
<!-- AI.TOC: AUGUR Phase 0 — First Monday Performance Evaluation — Read lines 1-20 for navigation.
  §1 📋 EXECUTIVE SUMMARY (Signal-ready)         → lines 8-28
  §2 1. Overall Performance Summary             → lines 29-71
  §3 2. Hourly Performance Deep Dive (EST)      → lines 72-139
  §4 3. Pair Performance                        → lines 140-187
  §5 4. Pattern Performance                     → lines 188-261
  §6 5. Direction Analysis                      → lines 262-290
  §7 6. Regime Halt Analysis                    → lines 291-324
  §8 7. Monday Morning Analysis                 → lines 325-336
  §9 8. Recommendations                         → lines 337-441
  §10 Appendix A: Phase 0 Elapsed Hour Perform   → lines 442-455
  §11 Appendix B: Full Pair Performance Table    → lines 456-463
  Total: 463 lines | Sections: 11
-->
**Date:** Monday, February 9, 2026 08:42 EST  
**Period:** Feb 7 18:03 → Feb 9 04:54 EST (~35 hours total, ~6 hours Phase 0)  
**Analyst:** Helios (Sub-agent: augur-analyst)

---

## 📋 EXECUTIVE SUMMARY (Signal-ready)

**AUGUR Phase 0 is losing money. The system needs surgery, not bandaids.**

### Key Numbers
- **35,464 total trades**, but only **8,092 unique price events** — patterns fire 4.4× per event on average
- **Overall WR: 48.2%** (all data), **34.4% Phase 0** (overnight only)
- **Total P/L: -$74.39** (all data), **-$67.41** (Phase 0 — 6 hours destroyed most gains)
- **Regime halt: Permanently halted since 5 AM** — rolling WR stuck at 26%, never recovers
- **Max drawdown: $765.71** (all), **$77.19** (Phase 0)

### 🔥 Top 3 Urgent Recommendations

1. **IMPLEMENT TIME-OF-DAY FILTER NOW** — Trade only hours 12-14, 17, 21-22 EST. This single change turns -$74 into +$842 on the same data. The overnight session (23:00-04:00) is a consistent money incinerator.

2. **FIX PATTERN DUPLICATION BUG** — 736 "unique" patterns are actually correlated variants firing on the same price events. ETHFI has 34 patterns that are literally the same 41 trades counted 34 times. Real unique patterns: ~50-100 max.

3. **KILL OVERNIGHT TRADING IMMEDIATELY** — Phase 0 only ran overnight (22:45 → 04:54) and lost $67.41 with 34.4% WR. The regime halt correctly identified this but can't save the system — it just triggers every 10 minutes forever.

---

## 1. Overall Performance Summary

### All Data (Feb 7 18:03 → Feb 9 04:54)

| Metric | Value |
|--------|-------|
| Total Trades | 35,464 |
| Unique Price Events | 8,092 |
| Wins | 17,108 |
| Losses | 18,356 |
| Win Rate | 48.2% |
| Total P/L | -$74.39 |
| Avg P/L per Trade | -$0.0021 |
| Sharpe-like Ratio | -0.008 |
| Max Win Streak | 752 |
| Max Loss Streak | 1,309 |
| Max Drawdown | $765.71 |

### Phase 0 Only (since 22:45 EST Feb 8)

| Metric | Value |
|--------|-------|
| Total Trades | 3,109 |
| Wins | 1,068 |
| Win Rate | **34.4%** ⚠️ |
| Total P/L | **-$67.41** |
| Avg P/L per Trade | -$0.0217 |
| Sharpe-like Ratio | -0.055 |
| Max Drawdown | $77.19 |

### Pre-Phase 0 (Feb 7 18:03 → Feb 8 22:45)

| Metric | Value |
|--------|-------|
| Total Trades | 32,355 |
| Win Rate | 49.6% |
| Total P/L | -$6.99 |
| Avg P/L per Trade | -$0.0002 |

**Verdict:** Pre-Phase 0 was approximately break-even (-$7 on 32K trades). Phase 0 deployment coincided with the overnight session, which destroyed $67 in 6 hours. The overnight period is fundamentally unprofitable.

---

## 2. Hourly Performance Deep Dive (EST)

### Full Hourly Breakdown (All Data)

| Hour | Trades | Wins | WR% | Total P/L | Avg P/L | Verdict |
|------|--------|------|-----|-----------|---------|---------|
| 0 (12am) | 753 | 277 | 36.8% | -$8.20 | -$0.011 | ✗ SKIP |
| 1 | 460 | 144 | 31.3% | -$11.52 | -$0.025 | ✗ SKIP |
| 2 | 401 | 157 | 39.2% | +$1.21 | +$0.003 | ~ marginal |
| 3 | 501 | 161 | 32.1% | -$20.09 | -$0.040 | ✗ SKIP |
| 4 | 576 | 205 | 35.6% | -$19.95 | -$0.035 | ✗ SKIP |
| 5 | 50 | 22 | 44.0% | -$1.88 | -$0.038 | ✗ SKIP |
| 6 | 38 | 20 | 52.6% | +$1.74 | +$0.046 | ~ low volume |
| 7 | 37 | 18 | 48.6% | -$0.80 | -$0.022 | ✗ low volume |
| 8 | 39 | 20 | 51.3% | -$1.06 | -$0.027 | ✗ low volume |
| 9 | 28 | 14 | 50.0% | -$0.22 | -$0.008 | ~ low volume |
| 10 | 187 | 75 | 40.1% | +$0.60 | +$0.003 | ~ marginal |
| 11 | 634 | 177 | 27.9% | **-$78.33** | -$0.124 | ✗✗ TOXIC |
| **12** | **1,892** | **1,082** | **57.2%** | **+$47.78** | +$0.025 | **✓ TRADE** |
| **13** | **2,232** | **1,217** | **54.5%** | **+$132.66** | +$0.059 | **✓✓ BEST** |
| **14** | **1,994** | **1,040** | **52.2%** | **+$79.50** | +$0.040 | **✓ TRADE** |
| 15 | 1,915 | 849 | 44.3% | -$130.04 | -$0.068 | ✗✗ TOXIC |
| 16 | 3,984 | 1,813 | 45.5% | **-$255.77** | -$0.064 | ✗✗✗ WORST |
| **17** | **1,343** | **1,123** | **83.6%** | **+$133.71** | +$0.100 | **✓✓✓ GOLDEN** |
| 18 | 59 | 24 | 40.7% | +$0.60 | +$0.010 | ~ low volume |
| 19 | 5,804 | 2,872 | 49.5% | +$32.15 | +$0.006 | ~ marginal |
| 20 | 5,690 | 1,944 | 34.2% | **-$417.59** | -$0.073 | ✗✗✗ WORST |
| **21** | **4,349** | **2,365** | **54.4%** | **+$294.33** | +$0.068 | **✓✓ EXCELLENT** |
| **22** | **2,011** | **1,310** | **65.1%** | **+$153.54** | +$0.076 | **✓✓ EXCELLENT** |
| 23 | 487 | 179 | 36.8% | -$6.76 | -$0.014 | ✗ SKIP |

### Key Findings

**The "Golden Window" from backtesting (17-20 / 5-8 PM) is SPLIT:**
- Hour 17 (5 PM): **INCREDIBLE** — 83.6% WR, +$133.71. Best single hour.
- Hour 18 (6 PM): Low volume, marginal (+$0.60)
- Hour 19 (7 PM): Break-even (+$32 on 5,800 trades, barely profitable)
- Hour 20 (8 PM): **CATASTROPHIC** — 34.2% WR, -$417.59. Worst single hour.

**The REAL golden window is 12-14 + 17 + 21-22:**

| Filter | Trades | WR | P/L |
|--------|--------|----|-----|
| All hours | 35,464 | 48.2% | -$74.39 |
| Profitable hours only | 20,310 | 55.6% | **+$877.81** |
| Best 6 hours (12-14,17,21-22) | 13,821 | **58.9%** | **+$841.51** |
| Best 6 hours + LONG only | 13,786 | **59.0%** | **+$843.10** |

**If we only traded the best 6 hours, we'd be up $841 instead of down $74.** That's a $915 swing from a simple time filter.

### Phase 0 Hourly Performance (overnight only)

Phase 0 only ran during the WORST hours:

| Hour (EST) | Trades | WR% | P/L |
|------------|--------|-----|-----|
| 22 | 153 | 37.9% | +$2.00 |
| 23 | 460 | 34.8% | -$6.96 |
| 0 | 720 | 36.0% | -$8.22 |
| 1 | 427 | 30.7% | -$11.29 |
| 2 | 367 | 37.1% | -$0.20 |
| 3 | 451 | 29.9% | -$24.92 |
| 4 | 531 | 35.6% | -$17.83 |

**Every single overnight hour has WR below 40%.** Phase 0 never had a chance — it deployed into the dead zone.

---

## 3. Pair Performance

### Top Performers (by P/L)

| Pair | Trades | WR% | Total P/L | Avg P/L |
|------|--------|-----|-----------|---------|
| SOL-USD | 12,250 | 53.0% | +$56.44 | +$0.005 |
| NEAR-USD | 741 | 27.5% | +$11.37 | +$0.015 |
| XRP-USD | 338 | 52.7% | +$8.23 | +$0.024 |
| AAVE-USD | 931 | 52.1% | +$2.18 | +$0.002 |
| BTC-USD | 397 | 55.9% | +$2.12 | +$0.005 |

### Bottom Performers (by P/L)

| Pair | Trades | WR% | Total P/L | Avg P/L |
|------|--------|-----|-----------|---------|
| ETH-USD | 12,294 | 52.5% | **-$28.85** | -$0.002 |
| AVAX-USD | 2,267 | 31.1% | **-$25.16** | -$0.011 |
| LTC-USD | 648 | 44.3% | -$12.52 | -$0.019 |
| LINK-USD | 819 | 48.0% | -$12.43 | -$0.015 |
| BNKR-USD | 44 | 29.5% | -$9.65 | -$0.219 |
| DOGE-USD | 693 | 45.6% | -$8.77 | -$0.013 |
| ARB-USD | 1,304 | 34.7% | -$7.87 | -$0.006 |

### Pair Analysis

- **273 total pairs** traded — absurdly over-diversified
- **261 pairs have <50 trades** — insufficient data for any statistical conclusion
- Only **12 pairs** have >100 trades with meaningful P/L
- **SOL-USD dominates**: 12,250 trades (34.5% of all trades), only profitable major pair
- **ETH-USD is a money pit**: 12,294 trades (34.7%), losing -$28.85 despite 52.5% WR
- **AVAX-USD already blacklisted**: correctly identified, 31.1% WR is terrible
- **NEAR-USD is anomalous**: 27.5% WR but +$11.37 P/L (few big winners)

### Blacklist Candidates (>100 trades, consistently losing)

| Pair | Trades | WR% | P/L | Recommendation |
|------|--------|-----|-----|----------------|
| ARB-USD | 1,304 | 34.7% | -$7.87 | Already blacklisted ✓ |
| AVAX-USD | 2,267 | 31.1% | -$25.16 | Already blacklisted ✓ |
| NEAR-USD | 741 | 27.5% | +$11.37 | Already blacklisted ✓ (low WR but profitable — review) |
| LTC-USD | 648 | 44.3% | -$12.52 | **BLACKLIST** |
| LINK-USD | 819 | 48.0% | -$12.43 | **BLACKLIST** |
| DOGE-USD | 693 | 45.6% | -$8.77 | **BLACKLIST** |
| ETH-USD | 12,294 | 52.5% | -$28.85 | **REVIEW** — high WR but losing. Position sizing issue? |

---

## 4. Pattern Performance

### Overview
- **736 unique pattern names** — far too many
- Many are correlated variants (e.g., `imbalance_above_40pct_ETHFI` through `imbalance_above_70pct_ETHFI` are the same trade)
- 196 patterns have <10 trades (statistically meaningless)
- 443 patterns have 10-99 trades (marginal significance)
- Only 97 patterns have 100+ trades

### 🚨 CRITICAL BUG: Pattern Duplication

Multiple patterns fire on the **same price event** simultaneously:
- Average: **4.4 patterns per unique price event**
- Maximum: **83 patterns firing at once** (SOL-USD at 20:06:10)
- ETHFI has **34 pattern variants** that are literally the **same 41 trades** counted 34 times

**This inflates trade count, distorts WR calculations, and makes the regime halt WR metric unreliable.**

### Pattern Family Analysis

| Family | Trades | WR% | Total P/L |
|--------|--------|-----|-----------|
| other (persistence, etc.) | 705 | 48.7% | +$3.33 |
| spread | 9,762 | 47.0% | +$0.49 |
| imbalance | 18,289 | 48.8% | -$15.10 |
| price_ret | 6,708 | 48.6% | **-$63.11** |

**price_ret patterns are the biggest losers**, responsible for -$63 of the -$74 total loss.

### Top 10 Patterns by P/L

| Pattern | Trades | WR% | P/L |
|---------|--------|-----|-----|
| price_ret_30_below_30pct_SKR-USD | 28 | 53.6% | +$6.36 |
| spread_pct_below_30pct_XRP-USD | 155 | 54.8% | +$4.87 |
| price_ret_30_above_90pct_JITOSOL-USD | 61 | 73.8% | +$4.63 |
| price_ret_30_below_20pct_RNBW-USD | 17 | 41.2% | +$4.50 |
| imbalance_below_40pct_API3-USD | 8 | 37.5% | +$4.09 |
| spread_pct_above_10pct_A8-USD | 20 | 45.0% | +$3.10 |
| price_ret_30_above_90pct_MSOL-USD | 72 | 63.9% | +$3.07 |
| price_ret_30_above_70pct_MSOL-USD | 89 | 57.3% | +$2.81 |
| price_ret_30_above_50pct_SUI-USD | 34 | 55.9% | +$2.56 |
| persistence_4_consec | 626 | 48.9% | +$2.46 |

### Bottom 10 Patterns by P/L

| Pattern | Trades | WR% | P/L |
|---------|--------|-----|-----|
| spread_pct_below_30pct_BNKR-USD | 44 | 29.5% | -$9.65 |
| price_ret_30_below_30pct_LSETH-USD | 48 | 27.1% | -$6.17 |
| price_ret_30_below_30pct_MSOL-USD | 62 | 45.2% | -$6.09 |
| price_ret_30_below_20pct_CBETH-USD | 53 | 30.2% | -$6.01 |
| price_ret_30_below_10pct_MSOL-USD | 37 | 29.7% | -$5.92 |
| price_ret_30_below_10pct_JITOSOL-USD | 29 | 27.6% | -$5.70 |
| price_ret_30_below_40pct_MSOL-USD | 74 | 39.2% | -$5.57 |
| price_ret_30_below_30pct_JITOSOL-USD | 64 | 43.8% | -$5.52 |
| price_ret_30_below_10pct_CBETH-USD | 32 | 25.0% | -$5.49 |
| price_ret_30_below_40pct_LSETH-USD | 90 | 44.4% | -$4.68 |

**Pattern: All bottom 10 are `price_ret_30_below_*` patterns on derivative tokens (LSETH, MSOL, CBETH, JITOSOL).** These trade the base asset (ETH/SOL) when a derivative's price return is low — essentially a contrarian bet that fails consistently.

### High Confidence Patterns (>60% WR, 20+ trades)
- 29 patterns exceed 60% WR
- **price_ret_30_above_90pct_JITOSOL-USD**: 73.8% WR (61 trades) — BEST
- But 24 of the 29 are ETHFI imbalance variants (same 41 trades duplicated)
- Real high-confidence patterns: ~5

### Low Confidence Patterns (<35% WR, 20+ trades)
- **87 patterns** below 35% WR — candidates for removal
- Most are AVAX, ARB, NEAR variants (already blacklisted)
- Remaining: PEPE, SHIB, ATOM, DOT, BERA, FARTCOIN, MAMO, RENDER patterns

---

## 5. Direction Analysis

| Direction | Trades | WR% | Total P/L | Avg P/L |
|-----------|--------|-----|-----------|---------|
| UP (long) | 34,739 | 48.3% | **-$108.76** | -$0.003 |
| DOWN (short) | 725 | 43.4% | **+$34.36** | +$0.047 |

### Key Findings

- **97.96% of all trades are UP (long)** — almost entirely long-biased already
- **SHORT trades are profitable** (+$34.36) despite lower WR, because wins are bigger
- Going LONG-only barely changes the math: -$108.76 vs -$74.39 total (you'd lose MORE by removing shorts)
- **Shorts are small but profitable** — consider keeping them

### Direction by Notable Hours

| Hour | Dir | Trades | WR% | P/L |
|------|-----|--------|-----|-----|
| 3 AM | DOWN | 98 | **60.2%** | +$18.54 |
| 3 AM | UP | 403 | 25.3% | -$38.63 |
| 13 (1 PM) | UP | 2,232 | 54.5% | +$132.66 |
| 17 (5 PM) | UP | 1,343 | 83.6% | +$133.71 |
| 21 (9 PM) | UP | 4,349 | 54.4% | +$294.33 |
| 22 (10 PM) | UP | 1,976 | 65.9% | +$155.13 |

**Overnight shorts at 3 AM are actually profitable (60.2% WR) while longs at 3 AM are terrible (25.3% WR).** If trading overnight at all, go short-only.

---

## 6. Regime Halt Analysis

### Current Status: **PERMANENTLY HALTED** 🔴

The regime halt has fired **44 times** in ~10 hours since Phase 0 deployed:

- First halt: 22:53 EST Feb 8 (8 minutes after deploy)
- Rolling WR values observed: 24%, 26%, 28% — **never reached 30% threshold**
- Since 5:04 AM, halts fire every exactly 10 minutes (the halt duration)
- **The system is in a death loop**: halt → wait 10 min → resume → immediately re-halt

### Rolling WR Distribution at Halt

| WR | Count |
|----|-------|
| 24% | 3 |
| 26% | 16 |
| 28% | 25 |

### Is the 30% Threshold Correct?

**YES — the threshold is working as designed.** The overnight WR genuinely IS below 30%. The problem isn't the threshold; it's that the system shouldn't be trading overnight at all.

However, the halt mechanism has a design flaw:
- It halts for ~10 minutes then re-evaluates
- The rolling window still contains the bad trades
- So it re-halts immediately
- This continues indefinitely until enough time passes that the window rolls off the bad trades
- In the current scenario, it will remain halted until the profitable afternoon hours generate enough wins to push the rolling WR above 30%

**Recommendation:** Add a maximum consecutive halt count. After N halts (e.g., 5), switch to hourly re-evaluation instead of 10-minute. Or: implement the time filter and the halt won't trigger during profitable hours.

---

## 7. Monday Morning Analysis

### No Monday Morning Trades

The system has been regime-halted since ~5:04 AM. Last trade was at 04:54 AM EST.

**Zero trades since midnight Monday.** The regime halt is preventing any Monday morning analysis.

This is actually **correct behavior** — the system's overnight WR was 34.4%, and the halt protected against further losses. The halt saved approximately $11/hour that would have been lost.

---

## 8. Recommendations

### 🔴 PRIORITY 1: Time-of-Day Filter (IMMEDIATE)

**YES — implement immediately.**

Trade ONLY during these hours (EST):
- **12:00 - 14:59** (Noon-3 PM): 54.6% WR, +$260 P/L
- **17:00 - 17:59** (5 PM): 83.6% WR, +$134 P/L  
- **21:00 - 22:59** (9-11 PM): 59.0% WR, +$448 P/L

**AVOID:**
- 11:00 (pre-noon): 27.9% WR, -$78 P/L
- 15:00-16:59: 44.8% WR, -$386 P/L combined
- 20:00: 34.2% WR, -$418 P/L
- 23:00-04:00 (overnight): 33.5% WR, consistently negative

**Expected impact:** -$74 → **+$842** (all data), a $916 improvement from one filter.

### 🔴 PRIORITY 2: Fix Pattern Duplication (IMMEDIATE)

**YES — critical architecture fix.**

Current: 736 patterns, many correlated, 4.4 patterns fire per price event.  
Target: Deduplicate to ~50-100 independent patterns.

Specific actions:
1. For each pair, keep only the BEST-performing pattern per family (e.g., one `imbalance_*_ETHFI` instead of 34)
2. When multiple patterns fire on the same (product, timestamp), take only the highest-WR pattern's signal
3. Remove all `price_ret_30_below_*` patterns on derivative tokens (LSETH, MSOL, CBETH, JITOSOL) — the bottom 10 losers are all this family

### 🟡 PRIORITY 3: Pair Filter (THIS WEEK)

**Add to blacklist:**
- `LTC-USD`: 648 trades, 44.3% WR, -$12.52
- `LINK-USD`: 819 trades, 48.0% WR, -$12.43
- `DOGE-USD`: 693 trades, 45.6% WR, -$8.77

**Keep existing blacklist:**
- `AVAX-USD` ✓ (31.1% WR)
- `ARB-USD` ✓ (34.7% WR)
- `NEAR-USD` ✓ (27.5% WR but profitable — may revisit later)

**Review (not enough data to blacklist yet):**
- `ETH-USD`: -$28.85 but 52.5% WR on 12K trades. Losing due to volume, not bad WR. The issue is likely overnight trading hours — try time filter first.

**Focus on winners:**
- `SOL-USD`: Only consistently profitable major pair
- `BTC-USD`: 55.9% WR, profitable
- `XRP-USD`: 52.7% WR, profitable
- `AAVE-USD`: 52.1% WR, profitable

### 🟡 PRIORITY 4: Pattern Pruning (THIS WEEK)

**Remove entirely (87 patterns with <35% WR, 20+ trades):**

Top candidates for removal:
- All `imbalance_below_*_NEAR-USD` (11-17% WR)
- `imbalance_above_90pct_AKT-USD` (12.5% WR)
- `spread_pct_above_60pct_PEPE-USD` (13.0% WR)
- All `price_ret_30_below_10pct_*` on MSOL/JITOSOL/CBETH/LSETH (25-30% WR, -$5-6 each)

**Keep (genuine high performers):**
- `price_ret_30_above_90pct_JITOSOL-USD` (73.8% WR)
- `price_ret_30_above_90pct_MSOL-USD` (63.9% WR)
- `spread_pct_below_30pct_XRP-USD` (54.8% WR, 155 trades)

### 🟢 PRIORITY 5: Regime Halt Tuning (AFTER TIME FILTER)

**If time filter is implemented:** The halt becomes less critical since you're only trading profitable hours. Keep it at 30% as a safety net.

**If time filter is NOT implemented:** The halt is correctly preventing catastrophic overnight losses. Consider:
- Increasing halt duration exponentially (10 min → 20 min → 40 min → 1 hr → 2 hr)
- Adding a time-based bypass (don't halt during known-profitable hours)
- Adding a "give up until next profitable window" mode

### 🟢 PRIORITY 6: Direction Filter

**NO — do not go LONG-only.**

Shorts are only 2% of trades but contribute +$34.36 to P/L. The system is already 98% long. Removing shorts would make performance worse (-$108.76 instead of -$74.39).

If anything, consider **more short opportunities** during overnight hours where short WR is 60.2% vs long WR of 25.3%.

### 🟢 PRIORITY 7: Position Sizing

Not actionable yet with paper trading, but for live deployment:
- **Increase size during golden hours** (17:00 especially — 83.6% WR)
- **Reduce size during marginal hours** (19:00 — 49.5% WR)
- **Consider confidence-weighted sizing**: Patterns with >60% WR get 2x allocation
- **Cap concurrent positions**: Currently 83 patterns can fire at once — need a max-positions limit

### 💡 New Features Needed

1. **Time-of-day filter** (Priority 1 — already recommended)
2. **Pattern deduplication at trade time** — if multiple patterns fire on the same event, take only the best one
3. **Exponential halt backoff** — don't keep retrying every 10 minutes
4. **Confidence scoring** — weight patterns by historical WR, not equally
5. **Per-pair position limits** — SOL and ETH dominate (69% of all trades), creating concentration risk
6. **Rolling performance tracker per pattern** — decay old WR data, detect patterns that stop working
7. **Minimum WR threshold for pattern activation** — don't trade patterns below 45% WR
8. **Automated backtesting before deploying new patterns from discovery**

---

## Appendix A: Phase 0 Elapsed Hour Performance

| Elapsed Hr | Count | Wins | WR% | P/L | Cumulative P/L | Time |
|------------|-------|------|-----|-----|-----------------|------|
| 0 | 479 | 171 | 35.7% | -$9.20 | -$9.20 | Feb 8 22:45 |
| 1 | 685 | 244 | 35.6% | +$6.26 | -$2.94 | Feb 8 23:45 |
| 2 | 513 | 173 | 33.7% | -$16.18 | -$19.12 | Feb 9 00:45 |
| 3 | 404 | 132 | 32.7% | -$10.59 | -$29.71 | Feb 9 01:45 |
| 4 | 443 | 146 | 33.0% | -$16.42 | -$46.13 | Feb 9 02:45 |
| 5 | 421 | 145 | 34.4% | -$22.36 | -$68.49 | Feb 9 03:45 |
| 6 | 164 | 57 | 34.8% | +$1.08 | -$67.41 | Feb 9 04:45 |

**Every hour of Phase 0 has WR in the 30-36% range.** The system never found its footing overnight. Losses were consistent and relentless.

## Appendix B: Full Pair Performance Table

See raw data in analysis queries. 273 pairs tracked, 44 with meaningful P/L (|P/L| > $1, 20+ trades).

---

*Report generated Feb 9, 2026 08:42 EST by augur-analyst sub-agent.*
