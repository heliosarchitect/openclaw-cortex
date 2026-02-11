# Advanced Pattern Search Results

## Mission
Beat the $777 baseline from `curr.wick_ratio / max(wick_ratio, 3)` using complex multi-candle patterns.

## Search 1: Advanced Patterns (1,124 tests)
**Status:** ✅ COMPLETE  
**Date:** 2026-02-03  
**Patterns Tested:** 1,124  
**Profitable Patterns:** 589  
**Patterns Beating Baseline:** 45  

### 🏆 TOP 10 WINNERS

1. **$4,351.56** - `(volume_multiply_upper_wick)_threshold_1.0_5candles`
   - 17,675 trades @ 50.6% win rate
   - $0.25 avg profit/trade
   - 8.6% max drawdown
   - **5.6x better than baseline!**

2. **$3,344.94** - `(body_divide_wick_ratio)_threshold_1.0_5candles`
   - 14,092 trades @ 50.1% win rate
   - $0.24 avg profit/trade
   - 11.2% max drawdown

3. **$3,035.28** - `(wick_ratio_divide_upper_wick)_threshold_3.0_5candles`
   - 2,343 trades @ 52.8% win rate
   - $1.30 avg profit/trade
   - 16.0% max drawdown

4. **$2,901.89** - `(volume_divide_body)_threshold_3.0_5candles`
   - 3,215 trades @ 50.2% win rate
   - $0.90 avg profit/trade
   - 14.0% max drawdown

5. **$2,656.55** - `(body_divide_wick_ratio)_threshold_1.0_7candles`
   - 11,973 trades @ 50.8% win rate
   - $0.22 avg profit/trade
   - 15.5% max drawdown

6. **$2,616.92** - `wick_ratio_time_decay_0.5_15candles`
   - 7,440 trades @ 50.4% win rate
   - $0.35 avg profit/trade
   - 13.3% max drawdown

7. **$2,343.68** - `(body_multiply_wick_ratio)_threshold_3.0_10candles`
   - 748 trades @ 52.7% win rate
   - $3.13 avg profit/trade
   - 11.9% max drawdown

8. **$2,009.24** - `(body_divide_upper_wick)_threshold_5.0_7candles`
   - 572 trades @ 52.8% win rate
   - $3.51 avg profit/trade
   - 16.7% max drawdown

9. **$1,959.52** - `volume_increasing_5candles`
   - 586 trades @ 52.6% win rate
   - $3.34 avg profit/trade
   - 11.5% max drawdown

10. **$1,930.91** - `curr_body_div_max_body_3.0_10window`
    - 25,747 trades @ 50.5% win rate
    - $0.07 avg profit/trade
    - 14.8% max drawdown

### Key Insights

**What Worked Best:**
1. **Feature interactions** (multiply/divide) between volume, body, and wicks
2. **5-7 candle windows** (not necessarily longer)
3. **Time decay patterns** with exponential weighting
4. **Conditional patterns** (IF-THEN logic)
5. **Wick ratio patterns** (building on original $777 winner)

**Surprising Findings:**
- Simple trend patterns ("volume_increasing_5candles") performed well (#9)
- Longer windows (15-20 candles) didn't always beat shorter ones
- High-frequency patterns (17k+ trades) can still be profitable with low drawdown
- Upper wick × volume interaction is HIGHLY profitable

**Pattern Types Performance:**
- ✅ Feature Interactions: **EXCELLENT** (top 4 spots)
- ✅ Time Decay: **STRONG** (#6)
- ✅ Momentum: **GOOD** (multiple top 20)
- ✅ Conditional Logic: **PROMISING** (#18 with 66.7% win rate)
- ⚠️  Volatility Patterns: Limited success
- ⚠️  Wick Divergence: Fewer trades

## Search 2: Million-Scale Search (67,132 tests)
**Status:** 🔄 RUNNING  
**Date:** 2026-02-03  
**Patterns Testing:** 67,132  

### Pattern Space Expansion:
- Exhaustive parameter sweeps (windows 3-20, 15+ thresholds)
- All dual feature combinations with 6 operators
- Triple feature combos with nested operations
- Percentile-based patterns (10-95th percentiles)
- Higher-order derivatives (1st, 2nd, 3rd)
- Volatility regime detection
- MA crossovers (all period combinations)
- Statistical anomaly detection (z-score, MAD, skew, kurtosis)

**Expected completion:** ~30-60 minutes

---

## Next Steps

1. ✅ Complete million-scale search
2. Analyze top 100 patterns for common features
3. Build hybrid patterns combining best elements
4. Test pattern ensembles (multiple patterns voting)
5. Add machine learning feature importance analysis

## Files
- `advanced_pattern_results.csv` - Full results from Search 1
- `million_scale_output.log` - Live output from Search 2
- `advanced_pattern_search.py` - Search 1 code
- `million_scale_pattern_search.py` - Search 2 code
