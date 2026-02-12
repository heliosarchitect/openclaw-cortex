# Per-Strategy Rolling EV Analysis

**Generated:** 2026-02-11 22:01:34
**Database:** paper_results.db
**Window:** 50 trades
**Total trades:** 2292
**Strategies:** 8

## Summary Table

| Strategy | Trades | WR% | PnL | EV Min | EV Max | EV Mean | %EV>0 | Neg Periods | Longest Neg |
|----------|--------|-----|-----|--------|--------|---------|-------|-------------|-------------|
| price_ret_60 | 107 | 21.5% | $1.70 | $-0.0080 | $0.0614 | $0.0260 | 89.7% | 2 | 3 trades |
| spread_pct | 529 | 34.8% | $13.74 | $-0.0323 | $0.1050 | $0.0260 | 80.2% | 9 | 68 trades |
| volume_proxy | 166 | 16.9% | $1.66 | $-0.0145 | $0.0371 | $0.0140 | 76.9% | 1 | 27 trades |
| imbalance | 349 | 16.9% | $-5.96 | $-0.1869 | $0.0881 | $-0.0222 | 54.3% | 5 | 61 trades |
| legacy_imbalance | 664 | 39.9% | $4.66 | $-0.1554 | $0.1547 | $0.0042 | 53.5% | 14 | 121 trades |
| price_ret_30 | 168 | 23.2% | $0.58 | $-0.0912 | $0.1083 | $-0.0059 | 50.4% | 1 | 59 trades |
| imbalance_ma | 302 | 22.2% | $3.51 | $-0.0420 | $0.1103 | $0.0126 | 48.6% | 5 | 73 trades |
| spread_change | 7 | — | — | — | — | — | — | — | — |

## legacy_imbalance

**Trades:** 664
**Overall WR:** 39.9% | **Total PnL:** $4.66
**EV Stats:** min=$-0.1554, max=$0.1547, mean=$0.0042, median=$0.0064
**% windows EV>0:** 53.5%
**Negative EV periods:** 14

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 58 | 69 | 12 trades | no |
| 2 | 74 | 92 | 19 trades | no |
| 3 | 151 | 192 | 42 trades | no |
| 4 | 195 | 199 | 5 trades | no |
| 5 | 201 | 201 | 1 trades | no |
| 6 | 209 | 215 | 7 trades | no |
| 7 | 229 | 278 | 50 trades | no |
| 8 | 339 | 459 | 121 trades | no |
| 9 | 619 | 619 | 1 trades | no |
| 10 | 623 | 623 | 1 trades | no |
| 11 | 626 | 626 | 1 trades | no |
| 12 | 637 | 638 | 2 trades | no |
| 13 | 640 | 649 | 10 trades | no |
| 14 | 651 | 664 | 14 trades | YES ⚠️ |

### Rolling EV Curve (sampled, 615 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $0.0816 | 30% | $0.3927 | $0.0517 |
| 75 | $-0.0084 | 18% | $0.4334 | $0.1053 |
| 100 | $0.0595 | 36% | $0.3307 | $0.0931 |
| 116 | $0.1547 ⬆️MAX | 46% | $0.4033 | $0.0569 |
| 125 | $0.1360 | 38% | $0.3825 | $0.0151 |
| 150 | $0.0133 | 22% | $0.3543 | $0.0829 |
| 171 | $-0.1554 ⬇️MIN | 20% | $0.0763 | $0.2133 |
| 175 | $-0.1433 | 26% | $0.1054 | $0.2306 |
| 200 | $0.0003 | 36% | $0.3637 | $0.2041 |
| 225 | $0.0590 | 40% | $0.3529 | $0.1369 |
| 250 | $-0.1046 | 38% | $0.2459 | $0.3195 |
| 275 | $-0.0235 | 42% | $0.3617 | $0.3024 |
| 300 | $0.1074 | 50% | $0.4142 | $0.1995 |
| 325 | $0.0272 | 44% | $0.3529 | $0.2287 |
| 350 | $-0.0586 | 36% | $0.2776 | $0.2478 |
| 375 | $-0.1361 | 32% | $0.3148 | $0.3482 |
| 400 | $-0.0472 | 44% | $0.3555 | $0.3636 |
| 425 | $-0.0722 | 50% | $0.3738 | $0.5182 |
| 450 | $-0.0807 | 46% | $0.3382 | $0.4375 |
| 475 | $0.1006 | 52% | $0.4129 | $0.2377 |
| 500 | $0.0486 | 46% | $0.3756 | $0.2299 |
| 525 | $0.0482 | 48% | $0.2467 | $0.1351 |
| 550 | $0.0813 | 54% | $0.3102 | $0.1874 |
| 575 | $0.0603 | 52% | $0.3477 | $0.2509 |
| 600 | $0.0309 | 50% | $0.2918 | $0.2300 |
| 625 | $0.0047 | 48% | $0.2743 | $0.2442 |
| 650 | $0.0014 | 38% | $0.3081 | $0.1866 |
| 664 | $-0.0598 | 26% | $0.2786 | $0.1787 |

## spread_pct

**Trades:** 529
**Overall WR:** 34.8% | **Total PnL:** $13.74
**EV Stats:** min=$-0.0323, max=$0.1050, mean=$0.0260, median=$0.0236
**% windows EV>0:** 80.2%
**Negative EV periods:** 9

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 149 | 150 | 2 trades | no |
| 2 | 226 | 228 | 3 trades | no |
| 3 | 234 | 236 | 3 trades | no |
| 4 | 240 | 243 | 4 trades | no |
| 5 | 248 | 248 | 1 trades | no |
| 6 | 339 | 406 | 68 trades | no |
| 7 | 411 | 411 | 1 trades | no |
| 8 | 417 | 428 | 12 trades | no |
| 9 | 440 | 440 | 1 trades | no |

### Rolling EV Curve (sampled, 480 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $0.0366 | 32% | $0.1675 | $0.0250 |
| 75 | $0.0645 | 34% | $0.2146 | $0.0129 |
| 99 | $0.1050 ⬆️MAX | 44% | $0.2451 | $0.0051 |
| 100 | $0.1050 | 44% | $0.2451 | $0.0051 |
| 125 | $0.0329 | 38% | $0.1671 | $0.0494 |
| 150 | $-0.0016 | 38% | $0.0882 | $0.0567 |
| 175 | $0.0612 | 46% | $0.1502 | $0.0147 |
| 200 | $0.0484 | 40% | $0.1708 | $0.0332 |
| 225 | $0.0012 | 36% | $0.1005 | $0.0546 |
| 250 | $0.0228 | 42% | $0.1161 | $0.0448 |
| 275 | $0.0219 | 44% | $0.1123 | $0.0492 |
| 300 | $0.0179 | 42% | $0.1191 | $0.0553 |
| 325 | $0.0220 | 36% | $0.1262 | $0.0365 |
| 350 | $-0.0160 | 20% | $0.0873 | $0.0418 |
| 361 | $-0.0323 ⬇️MIN | 12% | $0.1120 | $0.0520 |
| 375 | $-0.0239 | 14% | $0.1686 | $0.0553 |
| 400 | $-0.0101 | 30% | $0.1402 | $0.0745 |
| 425 | $-0.0052 | 32% | $0.1407 | $0.0738 |
| 450 | $0.0163 | 34% | $0.1388 | $0.0468 |
| 475 | $0.0600 | 42% | $0.1784 | $0.0257 |
| 500 | $0.0697 | 30% | $0.3168 | $0.0362 |
| 525 | $0.0074 | 24% | $0.2322 | $0.0636 |
| 529 | $0.0155 | 26% | $0.2292 | $0.0596 |

## imbalance

**Trades:** 349
**Overall WR:** 16.9% | **Total PnL:** $-5.96
**EV Stats:** min=$-0.1869, max=$0.0881, mean=$-0.0222, median=$0.0038
**% windows EV>0:** 54.3%
**Negative EV periods:** 5

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 59 | 119 | 61 trades | no |
| 2 | 179 | 184 | 6 trades | no |
| 3 | 235 | 245 | 11 trades | no |
| 4 | 261 | 269 | 9 trades | no |
| 5 | 292 | 341 | 50 trades | no |

### Rolling EV Curve (sampled, 300 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $0.0145 | 14% | $0.2206 | $0.0190 |
| 75 | $-0.1825 | 16% | $0.1063 | $0.2375 |
| 76 | $-0.1869 ⬇️MIN | 14% | $0.1089 | $0.2350 |
| 100 | $-0.1433 | 14% | $0.3505 | $0.2236 |
| 125 | $0.0187 | 22% | $0.1963 | $0.0315 |
| 129 | $0.0881 ⬆️MAX | 24% | $0.4584 | $0.0289 |
| 150 | $0.0405 | 24% | $0.3184 | $0.0473 |
| 175 | $0.0517 | 10% | $0.7370 | $0.0245 |
| 200 | $0.0048 | 10% | $0.2076 | $0.0178 |
| 225 | $0.0123 | 16% | $0.2316 | $0.0295 |
| 250 | $0.0023 | 18% | $0.1159 | $0.0227 |
| 275 | $0.0058 | 24% | $0.0568 | $0.0103 |
| 300 | $-0.0427 | 24% | $0.0626 | $0.0759 |
| 325 | $-0.0441 | 20% | $0.0464 | $0.0667 |
| 349 | $0.0049 | 14% | $0.0610 | $0.0043 |

## imbalance_ma

**Trades:** 302
**Overall WR:** 22.2% | **Total PnL:** $3.51
**EV Stats:** min=$-0.0420, max=$0.1103, mean=$0.0126, median=$-0.0003
**% windows EV>0:** 48.6%
**Negative EV periods:** 5

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 50 | 84 | 35 trades | no |
| 2 | 88 | 90 | 3 trades | no |
| 3 | 92 | 164 | 73 trades | no |
| 4 | 170 | 181 | 12 trades | no |
| 5 | 199 | 205 | 7 trades | no |

### Rolling EV Curve (sampled, 253 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $-0.0172 | 22% | $0.0450 | $0.0347 |
| 75 | $-0.0162 | 14% | $0.0738 | $0.0309 |
| 100 | $-0.0074 | 18% | $0.1246 | $0.0364 |
| 125 | $-0.0315 | 20% | $0.1020 | $0.0649 |
| 126 | $-0.0420 ⬇️MIN | 18% | $0.0550 | $0.0633 |
| 150 | $-0.0067 | 20% | $0.0850 | $0.0297 |
| 175 | $-0.0013 | 20% | $0.1040 | $0.0276 |
| 200 | $-0.0106 | 18% | $0.0899 | $0.0326 |
| 225 | $0.0159 | 18% | $0.2948 | $0.0453 |
| 250 | $0.0506 | 22% | $0.4416 | $0.0596 |
| 275 | $0.0934 | 28% | $0.4195 | $0.0335 |
| 283 | $0.1103 ⬆️MAX | 26% | $0.4734 | $0.0173 |
| 300 | $0.0628 | 32% | $0.2652 | $0.0325 |
| 302 | $0.0616 | 32% | $0.2659 | $0.0345 |

## price_ret_30

**Trades:** 168
**Overall WR:** 23.2% | **Total PnL:** $0.58
**EV Stats:** min=$-0.0912, max=$0.1083, mean=$-0.0059, median=$0.0199
**% windows EV>0:** 50.4%
**Negative EV periods:** 1

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 50 | 108 | 59 trades | no |

### Rolling EV Curve (sampled, 119 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $-0.0199 | 26% | $0.1894 | $0.0935 |
| 75 | $-0.0614 | 14% | $0.2618 | $0.1140 |
| 83 | $-0.0912 ⬇️MIN | 8% | $0.2327 | $0.1193 |
| 100 | $-0.0471 | 20% | $0.1635 | $0.0998 |
| 125 | $0.0454 | 24% | $0.5046 | $0.0996 |
| 150 | $0.0654 | 22% | $0.6470 | $0.0987 |
| 158 | $0.1083 ⬆️MAX | 26% | $0.5765 | $0.0562 |
| 168 | $0.0330 | 26% | $0.2705 | $0.0504 |

## volume_proxy

**Trades:** 166
**Overall WR:** 16.9% | **Total PnL:** $1.66
**EV Stats:** min=$-0.0145, max=$0.0371, mean=$0.0140, median=$0.0179
**% windows EV>0:** 76.9%
**Negative EV periods:** 1

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 50 | 76 | 27 trades | no |

### Rolling EV Curve (sampled, 117 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $-0.0112 | 8% | $0.1075 | $0.0215 |
| 72 | $-0.0145 ⬇️MIN | 10% | $0.0348 | $0.0200 |
| 75 | $-0.0145 | 10% | $0.0348 | $0.0200 |
| 100 | $0.0071 | 14% | $0.0506 | $0.0000 |
| 125 | $0.0293 | 24% | $0.1558 | $0.0106 |
| 141 | $0.0371 ⬆️MAX | 28% | $0.1616 | $0.0112 |
| 150 | $0.0346 | 26% | $0.1660 | $0.0116 |
| 166 | $0.0146 | 20% | $0.1061 | $0.0082 |

## price_ret_60

**Trades:** 107
**Overall WR:** 21.5% | **Total PnL:** $1.70
**EV Stats:** min=$-0.0080, max=$0.0614, mean=$0.0260, median=$0.0259
**% windows EV>0:** 89.7%
**Negative EV periods:** 2

### Negative EV Periods

| # | Start (trade) | End (trade) | Length | Ongoing? |
|---|---------------|-------------|--------|----------|
| 1 | 66 | 68 | 3 trades | no |
| 2 | 103 | 105 | 3 trades | no |

### Rolling EV Curve (sampled, 58 total points)

| Trade# | EV | WR | Avg Win | Avg Loss |
|--------|----|----|---------|----------|
| 50 | $0.0382 | 24% | $0.4892 | $0.1043 |
| 66 | $-0.0080 ⬇️MIN | 26% | $0.3467 | $0.1326 |
| 75 | $0.0164 | 24% | $0.3738 | $0.0965 |
| 82 | $0.0614 ⬆️MAX | 24% | $0.5615 | $0.0965 |
| 100 | $0.0005 | 18% | $0.4502 | $0.0982 |
| 107 | $0.0041 | 18% | $0.4539 | $0.0947 |

## spread_change

**Trades:** 7

⚠️ Skipped: Only 7 trades, need 50 for rolling window

## Key Findings

### imbalance — Consistently Negative or Bad Patch?

**VERDICT: MIXED.** 54.3% of windows are EV>0.
Mean EV: $-0.0222, 5 negative periods, longest: 61 trades
Last 50 windows: 16.0% positive

### spread_pct — Extended EV<0 Periods?

**WARNING: Has extended negative period of 68 trades.**
Overall 80.2% of windows are EV>0, mean EV=$0.0260
Despite low WR (34.8%), wins are large enough to maintain positive EV.

## Per-Strategy EV Halt Validation

Would per-strategy EV halt (halt when rolling EV < 0) correctly isolate losers?

- **price_ret_60** (89.7% EV>0): ✅ KEEP — rarely EV<0, halt would almost never trigger
- **spread_pct** (80.2% EV>0): ✅ KEEP — rarely EV<0, halt would almost never trigger
- **volume_proxy** (76.9% EV>0): ⚠️ KEEP WITH CAUTION — sometimes EV<0, halt would pause occasionally
- **imbalance** (54.3% EV>0): ⚠️ KEEP WITH CAUTION — sometimes EV<0, halt would pause occasionally
- **legacy_imbalance** (53.5% EV>0): ⚠️ KEEP WITH CAUTION — sometimes EV<0, halt would pause occasionally
- **price_ret_30** (50.4% EV>0): ⚠️ KEEP WITH CAUTION — sometimes EV<0, halt would pause occasionally
- **imbalance_ma** (48.6% EV>0): 🔶 MARGINAL — frequently EV<0, halt would significantly reduce trading

### Conclusion

**Would halt (0):** none
**Marginal (1):** imbalance_ma
**Would keep (6):** legacy_imbalance, spread_pct, imbalance, price_ret_30, volume_proxy, price_ret_60