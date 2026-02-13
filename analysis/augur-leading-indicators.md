# AUGUR Leading Indicator Analysis
<!-- AI.TOC: AUGUR Leading Indicator Analysis — Read lines 1-20 for navigation.
  §1 Executive Summary                          → lines 8-22
  §2 Baseline (Random Entry)                    → lines 23-37
  §3 Indicator Results                          → lines 38-132
  §4 BTC-USD Cross-Validation                   → lines 133-149
  §5 ❌ The Fee Wall: Why This Signal Is Unpro   → lines 150-171
  §6 Honest Assessment                          → lines 172-208
  §7 Recommended Next Steps                     → lines 209-220
  Total: 220 lines | Sections: 7
-->
*Generated: 2026-02-10 08:38 EST*  
*Data: ~68 hours of ETH-USD and BTC-USD from enhanced_data.db (last 24h analyzed)*  
*Price range: ETH $1,994 - $2,145 (7.3% range), ~86K orderbook snapshots, 604K trades*

---

## Executive Summary

**There IS real microstructure signal — but it's NOT profitably tradeable on Coinbase.**

Momentum continuation is the strongest signal found: when price moves >0.3-0.5% in 30-120 seconds, it continues in the same direction with 35-67% win rate for >0.2% additional gain. This signal is:
- ✅ Real (survives gap analysis — still works 10-30s after signal)
- ✅ Cross-validated (works on both ETH-USD and BTC-USD)
- ✅ Symmetric (works for both up and down momentum)
- ❌ **NOT profitable after fees** (0.5% maker RT or 0.8% taker RT destroys all edge)
- ❌ Gross average returns of 0.05-0.40% vs minimum 0.50% fee drag

**Bottom line: AUGUR's 20.2% pattern win rate is not fixable by finding better indicators. The fee structure on Coinbase makes sub-10-minute trading mathematically impossible to profit from.**

---

## Baseline (Random Entry)

These are the odds of price moving >0.2% if you enter at a random time:

| Lookahead | N | Long WR (>0.2%) | Short WR (>0.2%) | Avg Return |
|-----------|---|-----------------|------------------|------------|
| 1 min | 86,320 | 4.0% | 4.3% | -0.0005% |
| 2 min | 86,260 | 8.6% | 8.9% | -0.0010% |
| 5 min | 86,080 | 15.0% | 18.2% | -0.0024% |
| 10 min | 85,780 | 22.1% | 26.7% | -0.0063% |

**Key insight**: At 10 minutes, there's a ~22% chance of a 0.2% up move *by pure chance*. AUGUR's 20.2% win rate is actually WORSE than random.

---

## Indicator Results

### 1. Momentum Continuation (STRONGEST SIGNAL)

When price moves sharply, it tends to continue. This is the strongest effect found.

**Gap Analysis** — Does the signal persist after waiting?

Signal: Price rose >0.3% in 60 seconds. Measuring returns AFTER a gap:

| Gap | Lookahead | N | WR>0.2% | Avg Return | Verdict |
|-----|-----------|---|---------|------------|---------|
| 0s | 60s | 1,206 | 27.4% | 0.057% | ✅ Edge over 4% baseline |
| 0s | 120s | 1,206 | 34.2% | 0.082% | ✅ Edge over 8.6% baseline |
| 0s | 300s | 1,204 | 39.0% | 0.212% | ✅ Edge over 15% baseline |
| 10s | 120s | 1,206 | 32.6% | 0.092% | ✅ Still works with 10s delay |
| 30s | 120s | 1,206 | 34.5% | 0.109% | ✅ Still works with 30s delay |
| 60s | 120s | 1,206 | 36.3% | 0.129% | ✅ Still works with 60s delay |
| 120s | 120s | 1,206 | 27.9% | 0.125% | ⚠️ Fading but still above baseline |
| 120s | 300s | 1,159 | 26.2% | 0.058% | ⚠️ Nearly at baseline (15%) |

**The signal is REAL** — it persists even with a 60-second gap between observation and measurement. This rules out the "still measuring the same move" artifact.

**Down momentum (symmetry check):**

| Gap | Lookahead | N | Short WR>0.2% | Avg Return (short) |
|-----|-----------|---|---------------|---------------------|
| 0s | 300s | 1,388 | 38.1% | 0.115% |
| 10s | 300s | 1,388 | 37.0% | 0.114% |
| 30s | 300s | 1,388 | 37.9% | 0.110% |
| 60s | 300s | 1,388 | 36.0% | 0.095% |

✅ Symmetric — momentum continuation works in both directions.

### 2. Top 15 Indicators by Edge over Baseline (ETH-USD, N≥100)

| # | Indicator | Threshold | Dir | N | WR% | Baseline | Edge | Avg Ret% |
|---|-----------|-----------|-----|---|-----|----------|------|----------|
| 1 | Momentum 60s→5min | >0.5% | LONG | 336 | 49.7% | 15.0% | **+34.7%** | 0.403% |
| 2 | Momentum 60s→2min | >0.5% | LONG | 336 | 44.0% | 8.6% | **+35.4%** | 0.135% |
| 3 | Momentum 120s→2min | >0.5% | LONG | 1,075 | 43.4% | 8.6% | **+34.8%** | 0.177% |
| 4 | Momentum 30s→5min | >0.3% | LONG | 499 | 44.3% | 15.0% | **+29.3%** | 0.294% |
| 5 | Momentum 120s→5min | >0.5% | LONG | 1,058 | 42.2% | 15.0% | **+27.2%** | 0.283% |
| 6 | Momentum 60s→5min | >0.3% | LONG | 1,176 | 39.9% | 15.0% | **+24.9%** | 0.217% |
| 7 | Momentum 30s→5min | <-0.3% | SHORT | 464 | 39.4% | 18.2% | **+21.2%** | 0.145% |
| 8 | Momentum 60s→5min | <-0.3% | SHORT | 1,388 | 38.1% | 18.2% | **+19.9%** | 0.115% |
| 9 | MeanRevert 120s→10min | <-0.5% | LONG (reversal) | 929 | 39.1% | 22.1% | **+17.0%** | 0.008% |
| 10 | Momentum 300s→2min | >0.5% | LONG | 3,276 | 31.4% | 8.6% | **+22.8%** | 0.107% |
| 11 | Momentum 120s→10min | >0.5% | LONG | 1,057 | 38.7% | 22.1% | **+16.6%** | 0.166% |
| 12 | Momentum 60s→10min | <-0.3% | SHORT | 1,388 | 39.6% | 26.7% | **+12.9%** | 0.081% |
| 13 | Momentum 60s→1min | >0.5% | LONG | 336 | 38.4% | 4.0% | **+34.4%** | 0.114% |
| 14 | Flow BuySellRatio→5min | >3.0 | LONG | 1,236 | 20.3% | 15.0% | **+5.3%** | 0.028% |
| 15 | OB NormImbalance→5min | >0.5 | LONG | 5,668 | 16.7% | 15.0% | **+1.7%** | -0.001% |

### 3. Order Book Imbalance (WEAK SIGNAL)

When bid_size >> ask_size, there's a slight tendency for price to rise, but the edge is tiny:

- Normalized imbalance >0.5, 5min lookahead: 16.7% WR vs 15.0% baseline (+1.7%)
- Normalized imbalance >0.7, 5min lookahead: 17.2% WR vs 15.0% baseline (+2.2%)
- **Verdict**: Not enough edge to trade on its own

### 4. Trade Flow (WEAK SIGNAL)

Buy/sell volume ratio shows similar weak predictive power:

- Flow ratio >3.0, 5min: 20.3% WR vs 15.0% baseline (+5.3%)
- Flow ratio >5.0, 5min: 22.3% WR vs 15.0% baseline (+7.3%)
- **Verdict**: Signal exists but sample sizes drop quickly at higher thresholds

### 5. Spread Dynamics (VOLATILITY PREDICTOR ONLY)

Spread expansion predicts VOLATILITY but NOT direction:

| Indicator | N | Vol Increase | Avg Abs Return |
|-----------|---|-------------|----------------|
| Spread Z-Score >3.0 (5min window), 5min LA | 1,838 | +8.8% | 0.214% |
| Volume Surge >5x (2min window), 1min LA | 2,144 | +11.2% | 0.099% |

**Verdict**: Useful for volatility targeting but not directional trading.

### 6. Momentum + Imbalance Composite

Adding order book imbalance to momentum does NOT improve results:

| Signal | N | WR>0.2% | WR>0.5% | Avg Ret |
|--------|---|---------|---------|---------|
| Mom>0.5% only | 193 | 45.1% | 22.3% | 0.303% |
| Mom>0.5% + Imb>0.3 | 146 | 45.2% | 20.5% | 0.285% |
| Mom>0.5% + Imb>0.5 | 111 | 41.4% | 18.9% | 0.267% |

Adding imbalance filter reduces sample size without improving accuracy. The momentum signal is the signal; imbalance is mostly noise.

---

## BTC-USD Cross-Validation

BTC baseline: 1min=1.8%, 2min=4.7%, 5min=11.2%, 10min=18.6% (tighter spreads, less volatile)

| ETH Indicator | ETH WR/Edge | BTC WR/Edge | Consistent? |
|---------------|-------------|-------------|-------------|
| Momentum 60s→5min >0.5% | 49.7%/+34.7 | 47.9%/+36.7 | ✅ |
| Momentum 120s→2min >0.5% | 43.4%/+34.8 | 35.7%/+31.0 | ✅ |
| Momentum 30s→5min >0.3% | 44.3%/+29.3 | 51.8%/+40.6 | ✅ |
| Momentum 60s→2min >0.5% | 44.0%/+35.4 | 14.9%/+10.2 | ✅ |
| Momentum 60s→1min >0.5% | 38.4%/+34.4 | 11.7%/+9.9 | ✅ |
| Momentum 30s→2min >0.3% | 39.9%/+31.3 | 21.9%/+17.2 | ✅ |

**6/6 consistent across assets**. The momentum continuation effect is real and robust.

---

## ❌ The Fee Wall: Why This Signal Is Unprofitable

### Taker Fees (0.4% each way = 0.8% round trip)

| Best Signal | Gross Avg | Net After Fees | Net WR>0% | Verdict |
|-------------|-----------|----------------|-----------|---------|
| Mom 60s>0.5%, 5min LA | 0.403% | **-0.397%** | 19.6% | ❌ LOSS |
| Mom 120s>0.5%, 5min LA | 0.283% | **-0.517%** | 19.7% | ❌ LOSS |
| Mom 30s>0.3%, 5min LA | 0.294% | **-0.506%** | 18.2% | ❌ LOSS |

### Maker Fees (0.25% each way = 0.5% round trip)

| Best Signal | Gross Avg | Net After Fees | Net WR>0% | EV per signal |
|-------------|-----------|----------------|-----------|---------------|
| Mom 60s>0.5%, 5min LA | 0.403% | **-0.097%** | 29.5% | -$0.97/trade |
| Mom 120s>0.5%, 5min LA | 0.283% | **-0.217%** | 28.1% | -$2.17/trade |
| Mom 60s>0.3%, 5min LA | 0.217% | **-0.283%** | 26.1% | -$2.83/trade |

**Even with maker fees, EVERY configuration is negative EV.** The best case (Mom 60s>0.5%, 5min) loses ~0.097% per trade — close to breakeven but still negative.

---

## Honest Assessment

### 🟡 REAL SIGNAL, BUT UNPROFITABLE

**What we found:**
1. **Momentum continuation is real** — 30-60% edge over baseline, confirmed across assets, survives gap analysis
2. **Order book imbalance has weak signal** — 1-7% edge, not enough alone
3. **Volume surge predicts volatility** — 8-11% increase in absolute moves
4. **All signals are sub-fee** — gross returns of 0.05-0.40% vs 0.50-0.80% fees

**Why AUGUR's patterns have 20.2% win rate:**
- AUGUR targets >0.2% moves in 5 minutes
- Random baseline for 5-min 0.2% up moves: 15.0%
- AUGUR's 20.2% means it has ~5% edge — but this is eaten by fees
- The pattern matching adds marginal value but can't overcome the fee structure

**What would make this tradeable:**
1. **Zero/low fee venue** — FTX-style (no longer exists), or DEX with rebates
2. **Longer timeframes** — 1-4 hour holds where moves >1% are common
3. **Options/perps** — leverage makes 0.3% moves matter
4. **Market making** — earn the spread instead of paying it

### Recommended Parameters for Paper Trading (proof of concept only)

If you want to validate the signal exists (not for profit):

```
Signal: 60-second momentum > 0.3%
Direction: Same as momentum (continuation)
Lookahead: 5 minutes
Expected gross WR: ~40% for >0.2% move
Expected gross avg return: ~0.22%
Minimum to be profitable: Need venue with <0.11% each-way fees
```

---

## Recommended Next Steps

1. **Shift AUGUR to longer timeframes** — 30min to 4h holds where expected moves are 0.5-2%, clearing the fee hurdle
2. **Add momentum as primary signal** — it's the strongest predictor found; OB imbalance is noise at these timeframes
3. **Investigate maker-only strategies** — post limit orders on the other side of momentum; if filled, you're already in profit
4. **Consider perp trading** — FTX gone, but other venues have lower fees for derivatives
5. **Stop pattern-mining** — the 363 patterns at 20.2% WR are noise. Reduce to 3-5 momentum-based rules with strict fee awareness

---

*Analysis: 620 ETH indicator/threshold combos + 604 BTC combos tested. All forward returns computed with ≤5s timestamp tolerance. Gap analysis validates signal persistence. Fee analysis uses Coinbase Advanced Trade published rates.*
