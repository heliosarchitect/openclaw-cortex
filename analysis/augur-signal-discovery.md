# AUGUR Signal Discovery - Exhaustive Search Results
<!-- AI.TOC: AUGUR Signal Discovery - Exhaustive Search Results — Read lines 1-20 for navigation.
  §1 0. Price Context (Full Period)             → lines 10-18
  §2 1. Base Rates (Random Entry)               → lines 19-31
  §3 2. Top 20 Validated Signals (Train+Test    → lines 32-56
  §4 3. Liquid Market Signals                   → lines 57-60
  §5 4. Cross-Product Signal Stability          → lines 61-80
  §6 5. Best Signal Per Product                 → lines 81-130
  §7 6. Indicator Definitions                   → lines 131-166
  §8 7. Summary & Recommendations               → lines 167-208
  Total: 208 lines | Sections: 8
-->

Generated: 2026-02-10 16:04 UTC

Database: enhanced_data.db (1-second trade_flow + orderbook snapshots)
Candle size: 5 seconds | All indicators use PRIOR bars only (no lookahead)
Round-trip fee: 0.20% (VIP2 taker 0.10% each way)
**Validation: 50/50 time-ordered train/test split. Only signals profitable in BOTH halves are shown.**

## 0. Price Context (Full Period)
- **BTC-USD**: $69429.2248 → $69110.2669 (-0.5%)
- **ETH-USD**: $2061.7100 → $2018.7058 (-2.1%)
- **SOL-USD**: $87.4400 → $84.1300 (-3.8%)
- **NKN-USD**: $0.0051 → $0.0124 (+143.1%)
- **BNKR-USD**: $0.0006 → $0.0011 (+86.9%)
- **AXS-USD**: $1.3550 → $1.5110 (+11.5%)
- **XRP-USD**: $1.4220 → $1.4051 (-1.2%)

## 1. Base Rates (Random Entry)

*See per-product base rates at 60s hold in Phase 1 results above.*

Combined base rates across all products:
- 15s hold: WR=47.6% long, avg return +0.001%
- 30s hold: WR=48.2% long, avg return +0.002%
- 60s hold: WR=48.7% long, avg return +0.004%
- 120s hold: WR=48.7% long, avg return +0.006%
- 300s hold: WR=49.1% long, avg return +0.011%

To be profitable, a signal must achieve avg net return > 0% after 0.20% RT fees.

## 2. Top 20 Validated Signals (Train+Test Profitable)

| Rank | Product | Indicator | Condition | Dir | Hold | Train WR | Train Net | Train N | Test WR | Test Net | Test N |
|------|---------|-----------|-----------|-----|------|----------|-----------|---------|---------|----------|--------|
| 1 | NKN-USD | zscore_60 | below p10 (-1.752) | LONG | 300s | 58.2% | 1.452% | 328 | 59.5% | 1.435% | 328 |
| 2 | NKN-USD | rsi_24 | below p10 (37.96) | LONG | 300s | 53.0% | 1.090% | 328 | 60.1% | 1.370% | 328 |
| 3 | NKN-USD | spread | above p90 (1.78) | LONG | 300s | 56.4% | 4.435% | 330 | 50.2% | 1.017% | 331 |
| 4 | NKN-USD | spread_ma6 | above p90 (1.589) | LONG | 300s | 68.3% | 4.226% | 328 | 47.7% | 0.900% | 329 |
| 5 | NKN-USD | rsi_24 | below p20 (42.33) | LONG | 300s | 56.9% | 1.196% | 652 | 52.3% | 0.875% | 652 |
| 6 | NKN-USD | count_buy_pct | above p90 (1) | LONG | 300s | 45.2% | 0.870% | 312 | 47.9% | 0.849% | 313 |
| 7 | NKN-USD | zscore_60 | below p20 (-1.244) | LONG | 300s | 60.0% | 1.678% | 653 | 54.1% | 0.740% | 654 |
| 8 | NKN-USD | rsi_12 | below p10 (31.66) | LONG | 300s | 51.4% | 0.713% | 325 | 60.1% | 1.148% | 326 |
| 9 | NKN-USD | count_buy_pct | above p80 (1) | LONG | 300s | 43.6% | 0.669% | 429 | 50.7% | 0.843% | 430 |
| 10 | NKN-USD | trend_align | below p30 (-1) | LONG | 300s | 52.0% | 0.904% | 871 | 51.8% | 0.617% | 872 |
| 11 | BNKR-USD | mom_24 | above p90 (0.01633) | LONG | 300s | 60.0% | 0.609% | 877 | 55.9% | 0.752% | 878 |
| 12 | BNKR-USD | rsi_24 | above p90 (67.46) | LONG | 300s | 64.0% | 0.584% | 877 | 58.4% | 0.789% | 878 |
| 13 | NKN-USD | zscore_60 | below p30 (-0.8757) | LONG | 300s | 54.9% | 1.145% | 976 | 51.6% | 0.569% | 977 |
| 14 | BIRB-USD | spread_ma6 | above p90 (0.1769) | SHORT | 300s | 69.3% | 0.544% | 257 | 66.9% | 0.576% | 257 |
| 15 | BNKR-USD | mom_12 | above p90 (0.01036) | LONG | 300s | 60.9% | 0.524% | 878 | 56.2% | 0.666% | 878 |
| 16 | NKN-USD | rsi_12 | below p20 (38.07) | LONG | 300s | 48.5% | 0.520% | 654 | 54.0% | 0.687% | 655 |
| 17 | BNKR-USD | rsi_12 | above p90 (73.18) | LONG | 300s | 64.0% | 0.561% | 878 | 54.3% | 0.514% | 878 |
| 18 | NKN-USD | mom_60 | below p10 (-0.04854) | LONG | 300s | 59.3% | 2.473% | 327 | 53.7% | 0.491% | 328 |
| 19 | BNKR-USD | rsi_24 | above p80 (61.21) | LONG | 300s | 62.0% | 0.486% | 1754 | 56.4% | 0.510% | 1755 |
| 20 | NKN-USD | zscore_60 | below p10 (-1.752) | LONG | 120s | 54.6% | 0.475% | 328 | 58.2% | 0.641% | 328 |

## 3. Liquid Market Signals

**No validated signals found on liquid markets (BTC/ETH/SOL/XRP/LTC/DOGE/LINK).**

## 4. Cross-Product Signal Stability

Signals profitable on 3+ products (strongest evidence of real edge):

| Indicator | Condition | Dir | Hold | # Products | Avg Min Net | Products |
|-----------|-----------|-----|------|------------|-------------|----------|
| rsi_24 | above | LONG | 300s | 3 | 0.260% | BIRB-USD,BNKR-USD,NKN-USD |
| buy_pct_accel | below | LONG | 300s | 3 | 0.160% | BERA-USD,BNKR-USD,NKN-USD |
| buy_pct_accel | above | LONG | 300s | 3 | 0.157% | BERA-USD,BNKR-USD,NKN-USD |
| spread_change | below | LONG | 300s | 3 | 0.144% | BERA-USD,BNKR-USD,NKN-USD |
| buy_pct | above | LONG | 300s | 3 | 0.102% | BERA-USD,BNKR-USD,NKN-USD |
| ob_imb | above | LONG | 300s | 4 | 0.080% | BERA-USD,BIRB-USD,BNKR-USD,NKN-USD |
| count_buy_pct_6 | above | LONG | 300s | 3 | 0.077% | BIRB-USD,BNKR-USD,NKN-USD |
| buy_pct_6 | above | LONG | 300s | 3 | 0.076% | BIRB-USD,BNKR-USD,NKN-USD |
| mom_24 | below | LONG | 300s | 3 | 0.073% | BERA-USD,BNKR-USD,NKN-USD |
| vol_24 | below | LONG | 300s | 3 | 0.058% | BERA-USD,BNKR-USD,NKN-USD |
| ob_imb_6 | above | LONG | 300s | 3 | 0.029% | BERA-USD,BNKR-USD,NKN-USD |
| ob_imb_3 | above | LONG | 300s | 4 | 0.028% | BERA-USD,BIRB-USD,BNKR-USD,NKN-USD |
| vol_6 | below | LONG | 300s | 3 | 0.026% | AXS-USD,BERA-USD,ZRO-USD |

## 5. Best Signal Per Product

### NKN-USD
- **zscore_60** below p10 → LONG 300s | Train: WR=58.2% net=1.452% n=328 | Test: WR=59.5% net=1.435% n=328
- **rsi_24** below p10 → LONG 300s | Train: WR=53.0% net=1.090% n=328 | Test: WR=60.1% net=1.370% n=328
- **spread** above p90 → LONG 300s | Train: WR=56.4% net=4.435% n=330 | Test: WR=50.2% net=1.017% n=331

### BNKR-USD
- **mom_24** above p90 → LONG 300s | Train: WR=60.0% net=0.609% n=877 | Test: WR=55.9% net=0.752% n=878
- **rsi_24** above p90 → LONG 300s | Train: WR=64.0% net=0.584% n=877 | Test: WR=58.4% net=0.789% n=878
- **mom_12** above p90 → LONG 300s | Train: WR=60.9% net=0.524% n=878 | Test: WR=56.2% net=0.666% n=878

### BIRB-USD
- **spread_ma6** above p90 → SHORT 300s | Train: WR=69.3% net=0.544% n=257 | Test: WR=66.9% net=0.576% n=257
- **spread_ma6** above p80 → SHORT 300s | Train: WR=66.2% net=0.411% n=509 | Test: WR=63.3% net=0.380% n=510
- **vol_24** above p90 → SHORT 300s | Train: WR=74.3% net=1.100% n=257 | Test: WR=70.2% net=0.380% n=258

### AXS-USD
- **spread_ma6** below p10 → LONG 300s | Train: WR=50.8% net=0.502% n=303 | Test: WR=64.7% net=0.370% n=303
- **spread_ma6** below p20 → LONG 300s | Train: WR=53.7% net=0.731% n=605 | Test: WR=62.1% net=0.244% n=605
- **spread_ma6** below p30 → LONG 300s | Train: WR=57.0% net=0.667% n=905 | Test: WR=56.2% net=0.096% n=906

### BERA-USD
- **mom_60** above p90 → SHORT 300s | Train: WR=46.8% net=0.389% n=265 | Test: WR=65.4% net=0.329% n=266
- **vol_12** below p20 → LONG 300s | Train: WR=47.0% net=0.198% n=534 | Test: WR=56.0% net=0.144% n=534
- **vol_12** below p30 → LONG 300s | Train: WR=48.2% net=0.177% n=803 | Test: WR=56.9% net=0.131% n=803

### ZRO-USD
- **mom_60** below p10 → SHORT 300s | Train: WR=58.4% net=0.258% n=281 | Test: WR=56.7% net=0.536% n=282
- **vol_12** above p90 → SHORT 120s | Train: WR=56.1% net=0.058% n=287 | Test: WR=57.8% net=0.207% n=287
- **vol_6** above p90 → SHORT 300s | Train: WR=42.5% net=0.165% n=287 | Test: WR=50.2% net=0.041% n=287

### MAMO-USD
- **spread** below p10 → SHORT 300s | Train: WR=62.2% net=0.223% n=312 | Test: WR=45.0% net=0.069% n=313

### SKR-USD
- **mom_60** above p90 → SHORT 300s | Train: WR=67.8% net=0.398% n=416 | Test: WR=56.4% net=0.065% n=417
- **mom_12** above p90 → SHORT 300s | Train: WR=50.2% net=0.063% n=418 | Test: WR=55.4% net=0.167% n=419
- **mom_24** above p90 → SHORT 300s | Train: WR=51.0% net=0.050% n=418 | Test: WR=56.7% net=0.185% n=418

### HYPE-USD
- **vol_24** below p10 → SHORT 300s | Train: WR=70.7% net=0.059% n=246 | Test: WR=86.6% net=0.313% n=247
- **vol_24** below p30 → SHORT 300s | Train: WR=66.3% net=0.007% n=738 | Test: WR=69.5% net=0.090% n=738

### ICP-USD
- **spread_ma6** below p10 → SHORT 300s | Train: WR=68.8% net=0.048% n=279 | Test: WR=77.4% net=0.162% n=279

### WLFI-USD
- **vol_24** above p90 → LONG 300s | Train: WR=60.0% net=0.635% n=260 | Test: WR=67.8% net=0.011% n=261

## 6. Indicator Definitions

All indicators computed from PRIOR 5-second bars only. No future data leakage.

**Order Flow (safe, no division-by-zero):**
- `buy_pct` = buy_volume / total_volume (prior bar), range [0,1]
- `buy_pct_N` = N-bar rolling mean of buy_pct
- `count_buy_pct` = buy_count / total_count (prior bar)
- `buy_pct_accel` = diff(buy_pct)

**Volume:**
- `vol_ratio_N` = prior_bar_volume / N-bar_rolling_avg(volume)
- `buy_vol_ratio_N` = prior_bar_buy_volume / N-bar_avg(buy_volume)

**Price Action:**
- `mom_N` = close[-1] / close[-N-1] - 1 (prior N bars)
- `vol_N` = rolling std of returns over N prior bars
- `vol_expand` = vol_6 / vol_24
- `zscore_N` = (close[-1] - rolling_mean_N) / rolling_std_N

**Mean Reversion & Momentum:**
- `rsi_N` = standard RSI over N prior bars
- `mean_rev_score` = -mom_12 * vol_ratio_12 (drop + volume = buy)
- `mom_vol_score` = mom_6 * vol_ratio_6 (momentum * volume)

**Orderbook:**
- `ob_imb` = (bid_size - ask_size) / (bid_size + ask_size) (prior bar)
- `ob_imb_N` = N-bar rolling mean
- `spread` = avg_spread_pct (prior bar)
- `spread_ma6` = 6-bar rolling mean of spread
- `ob_imb_change` = diff(ob_imb)

**Cross-Timeframe:**
- `trend_align` = sign(mom_6) + sign(mom_12) + sign(mom_60), range [-3, +3]


## 7. Summary & Recommendations

- **612** signal configs passed train/test validation
- Across **11** products
- Best overall: **zscore_60** on **NKN-USD** → LONG 300s, min(train,test) net = 1.435%

### Actionable Signals for Paper Trading

**NKN-USD - zscore_60**
- Condition: below -1.752 (p10)
- Direction: LONG, Hold: 300s
- Expected net return: 1.435% (conservative estimate)
- Win rate: Train 58.2% / Test 59.5%
- Sample: Train 328 / Test 328

**NKN-USD - rsi_24**
- Condition: below 37.96 (p10)
- Direction: LONG, Hold: 300s
- Expected net return: 1.090% (conservative estimate)
- Win rate: Train 53.0% / Test 60.1%
- Sample: Train 328 / Test 328

**NKN-USD - spread**
- Condition: above 1.78 (p90)
- Direction: LONG, Hold: 300s
- Expected net return: 1.017% (conservative estimate)
- Win rate: Train 56.4% / Test 50.2%
- Sample: Train 330 / Test 331

**NKN-USD - spread_ma6**
- Condition: above 1.589 (p90)
- Direction: LONG, Hold: 300s
- Expected net return: 0.900% (conservative estimate)
- Win rate: Train 68.3% / Test 47.7%
- Sample: Train 328 / Test 329

**NKN-USD - rsi_24**
- Condition: below 42.33 (p20)
- Direction: LONG, Hold: 300s
- Expected net return: 0.875% (conservative estimate)
- Win rate: Train 56.9% / Test 52.3%
- Sample: Train 652 / Test 652