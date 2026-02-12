# AUGUR Strategy Pruning Analysis
**Date:** 2026-02-12 06:55 EST
**Dataset:** 6,274 paper trades since wide-open launch (~8.5 hours of data)

## Strategy Performance (All Time)

| Strategy | Trades | Wins | WR% | PnL ($) | Avg PnL | Gross Win | Gross Loss |
|----------|--------|------|-----|---------|---------|-----------|------------|
| **spread_pct** | 1,911 | 599 | **31.3** | **+$29.86** | +$0.0156 | $115.61 | -$85.76 |
| **imbalance_ma** | 1,123 | 232 | **20.7** | **+$13.52** | +$0.0120 | $47.83 | -$34.31 |
| spread_change | 30 | 5 | 16.7 | +$0.70 | +$0.0233 | $0.88 | -$0.18 |
| price_ret_30 | 450 | 90 | 20.0 | -$0.12 | -$0.0003 | $26.10 | -$26.22 |
| price_ret_60 | 341 | 53 | 15.5 | -$0.26 | -$0.0008 | $19.70 | -$19.96 |
| volume_proxy | 595 | 95 | 16.0 | -$1.32 | -$0.0022 | $15.72 | -$17.04 |
| **imbalance** | **1,160** | **205** | **17.7** | **-$14.07** | **-$0.0121** | $30.79 | -$44.85 |

**Legacy (no strategy tag):** 664 trades, 39.9% WR, +$4.66 (these predate the strategy column)

## The Big Picture

**Total PnL:** +$32.68 across 6,274 trades
- Winners (spread_pct + imbalance_ma): +$43.38 from 3,034 trades (48% of volume)
- Losers (imbalance + volume_proxy + price_ret_*): -$15.77 from 2,546 trades (41% of volume)
- Near-zero (spread_change + legacy): +$5.36 from 694 trades (11%)

**If we pruned the 4 losers from live trading:**
- PnL would increase by ~$15.77 (48% improvement)
- Trade count drops by 41% → less fees, less exposure
- WR jumps from 24.6% to ~27.4% (winners-only pool)

## Strategy-Level Verdict

| Strategy | Verdict | Reason |
|----------|---------|--------|
| spread_pct | ✅ **KEEP** | Best edge. 31.3% WR, +$29.86. Consistent across hours. |
| imbalance_ma | ✅ **KEEP** | Second best. 20.7% WR, +$13.52. Moving average version works. |
| imbalance | ❌ **DISABLE** | Biggest loser. -$14.07. Raw imbalance has no edge — the MA version does. |
| volume_proxy | ❌ **DISABLE** | -$1.32. No edge at any time window. |
| price_ret_30 | ⚠️ **WATCH** | Near zero (-$0.12). Borderline. May have edge in specific products. |
| price_ret_60 | ⚠️ **WATCH** | Near zero (-$0.26). Similar to price_ret_30. |
| spread_change | 🔍 **INSUFFICIENT** | Only 30 trades. Need more data before judging. |

## Recommendation

**Paper trader:** Keep running ALL strategies (its job is to generate comparison data).

**Live trader config (when activated):**
```python
ENABLED_STRATEGIES = {'spread_pct', 'imbalance_ma'}
# Everything else disabled until proven profitable over 2+ days
```

## Next Steps
- [ ] Continue collecting paper data through Feb 13 for 2-day confirmation
- [ ] Check if losing strategies have product-specific pockets of alpha (e.g., price_ret_60 on SKR-USD was +$4.43 in legacy data)
- [ ] Build strategy filter into live_augur.py / augur_pipeline.py
