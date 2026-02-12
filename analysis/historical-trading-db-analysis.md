# Historical Trading Database Analysis

**Source:** `~/Projects/augur-collector/trading_data.db` (683MB)  
**Date:** 2026-02-11 23:00 EST  

---

## Overview

| Metric | Value |
|--------|-------|
| Total fills | 1,834,862 |
| Date range | 2025-08-11 → 2025-11-26 (~3.5 months) |
| Unique products | 218 |
| Accounts | 3 (CHADSQUARED, OGCHAD, BABYCHAD) |
| Total volume | $179,934,009 |

## Account Breakdown

| Account | Fills | Date Range | Products | Volume | Strategy |
|---------|-------|------------|----------|--------|----------|
| CHADSQUARED | 704,216 | Aug 29 – Nov 26 | 4 | $82.8M | HFT market-making (ETH-USD primary) |
| OGCHAD | 655,213 | Aug 23 – Oct 17 | 3 | $41.9M | HFT market-making (XRP-USD primary) |
| BABYCHAD | 475,433 | Aug 11 – Nov 11 | 216 | $55.2M | Multi-product directional/market-making |

## Product Focus

### CHADSQUARED (ETH specialist)
- ETH-USD: 660,489 fills, $78.3M volume (94% of account)
- MON-USD: 43,669 fills, $4.5M
- XRP-USD: 32 fills (test only)

### OGCHAD (XRP specialist)
- XRP-USD: 655,178 fills, $41.9M volume (99.9% of account)

### BABYCHAD (multi-product explorer)
- ETH-USD: 360,175 fills, $40.8M (primary)
- Then ~215 other products with 1K-20K fills each
- Top runners: ADA, BIO, LA, AIOZ, ENA, LOKA, PUMP, GODS, ZORA, FARTCOIN

## PnL Summary

| Account | Realized PnL | Notes |
|---------|-------------|-------|
| BABYCHAD | +$1,781,518 | Across 215 products (SOL-USD entry corrupt) |
| CHADSQUARED | -$128,093 | Concentrated losses on ETH |
| OGCHAD | -$3,227,493 | Major loss on XRP |

**Note:** OGCHAD/CHADSQUARED PnL likely affected by position tracking methodology — these were market-making bots that held inventory. Realized PnL ≠ total performance for MM strategies.

### BABYCHAD Top Earners
1. ETH-USD: +$2,709,863
2. ERN-USD: +$48,317
3. LCX-USD: +$43,089
4. PRIME-USD: +$42,125
5. 1INCH-USD: +$28,455

## The Legendary Sept 21, 2025

Peak day across all recorded history:

| Account | Fills | Volume |
|---------|-------|--------|
| CHADSQUARED | 37,858 | $9,202,864 |
| OGCHAD | 19,632 | $3,715,843 |
| **TOTAL** | **57,490** | **$12,918,707** |

That's ~40 fills/minute sustained over 24 hours, or roughly one fill every 1.5 seconds per bot.

## September 2025 Daily Breakdown (Peak Month)

The bots ran with varying intensity throughout September:
- Low days: 200-1,000 fills
- Medium days: 5,000-15,000 fills  
- Peak days: 20,000-57,000 fills

Volume correlated heavily with market volatility — bots filled more when spreads widened.

## Key Insights for AUGUR

1. **Scale gap**: Chad bots did 28K-57K fills/day. AUGUR paper trader does ~100 trades/day. Two completely different operating regimes.
2. **Product focus**: The winning strategy was extreme concentration (1-2 products per bot), not diversification. BABYCHAD's 216-product approach generated volume but CHADSQUARED/OGCHAD were the specialists.
3. **Market-making vs directional**: These bots rested limit orders on both sides. AUGUR is directional (buy signal → wait → sell). Different strategy entirely.
4. **Sub-second holds**: At 40 fills/minute, average hold time was likely 2-5 seconds. AUGUR's signal miner only tests 60s+ holds. The data that made money lives in a timescale the miner can't see.
5. **Fee structure matters**: At this volume, 0 bps fees are essential. Even 0.01% would be $18K/day in fees on $180M volume.

## Data Quality Notes
- SOL-USD position in BABYCHAD has corrupt realized_pnl (-$2.05 quadrillion) — excluded from totals
- Fills table appears clean, no obvious timestamp gaps or anomalies
- Hourly PnL and summary tables exist but weren't analyzed here
