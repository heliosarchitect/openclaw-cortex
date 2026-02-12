# AUGUR Baseline — Pre-Exit-Improvements Snapshot
**Captured**: 2026-02-11 22:18 EST  
**Branch**: `ev-halt-gate-layer` @ df95b2e (just restarted)  
**Total Trades**: 2,401 (from ~12hrs of trading)  

## Per-Strategy Performance

| Strategy | Trades | WR | Total PnL | Avg Win | Avg Loss | W/L Ratio | Avg Hold |
|----------|--------|------|-----------|---------|----------|-----------|----------|
| spread_pct | 566 | 34.8% | +$13.70 | $0.156 | -$0.046 | 3.38x | 311s |
| imbalance_ma | 321 | 22.7% | +$3.58 | $0.178 | -$0.038 | 4.70x | 140s |
| volume_proxy | 178 | 16.9% | +$1.85 | $0.114 | -$0.011 | 10.75x | 167s |
| price_ret_60 | 115 | 20.0% | +$1.60 | $0.442 | -$0.093 | 4.75x | 165s |
| spread_change | 9 | 22.2% | +$0.41 | $0.232 | -$0.008 | 28.96x | 385s |
| price_ret_30 | 179 | 21.8% | +$0.03 | $0.307 | -$0.085 | 3.60x | 70s |
| imbalance | 369 | 16.8% | -$5.88 | $0.182 | -$0.056 | 3.25x | 106s |

## Key Observations
- **spread_pct** still dominant: 34.8% WR, only profitable strategy by volume
- **imbalance** is the only truly losing strategy (-$5.88, 16.8% WR, lowest W/L ratio)
- **volume_proxy** has insane W/L ratio (10.75x) but only 16.9% WR — rare big wins
- **price_ret_60** has highest avg_win ($0.442) — best candidate for fee-clearing at live
- All WRs below 35% — edge comes from W/L ratio, not frequency

## What Changes with New Branch
- Strategy-adaptive trailing stops (ACTIVE): spread_pct 0.5%, fast strategies 0.2%
- 30s min hold (ACTIVE): eliminates 0-30s noise exits
- Per-strategy EV halt (DISABLED): tracking only
- Spread gate (DISABLED): tracking only
- Conditional time-decay (DISABLED): tracking only

## Purpose
Compare against 48hr post-restart data to measure exit improvement impact.
