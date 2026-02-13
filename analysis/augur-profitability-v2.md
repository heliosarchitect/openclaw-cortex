# AUGUR Profitability Reanalysis v2
<!-- AI.TOC: AUGUR Profitability Reanalysis v2 — Read lines 1-20 for navigation.
  §1 Executive Summary                          → lines 10-34
  §2 ETH-USD                                    → lines 35-376
  §3 BTC-USD                                    → lines 377-702
  §4 Final Recommendations                      → lines 703-767
  Total: 767 lines | Sections: 4
-->
*Generated: 2026-02-10 08:54 EST*
*Fee structure: Taker 0.10%/side (0.20% RT) | Maker 0.05%/side (0.10% RT)*
*Previous report used 0.25%/side (0.50% RT) — was 2.5× too high*
*Data: ~68h of live Coinbase data, 5-second resolution*
*Train/test split: first 34h / last 34h*

---

## Executive Summary

### The Fee Correction Changes Everything

The previous analysis concluded ALL signals were unprofitable because it used 0.50% round-trip fees.
The actual Coinbase Advanced fees at VIP 2 tier are:
- **Taker: 0.10% per side → 0.20% round trip**
- **Maker: 0.05% per side → 0.10% round trip**

This is 2.5× lower than assumed. Signals with gross returns of 0.20-0.40% flip from losers to winners.

### ETH-USD
- Total strategies tested: 510
- **Profitable (full dataset, taker fees): 9**
- **Profitable (full dataset, maker fees): 48**
- Profitable in BOTH train+test (taker): 0

### BTC-USD
- Total strategies tested: 417
- **Profitable (full dataset, taker fees): 0**
- **Profitable (full dataset, maker fees): 8**
- Profitable in BOTH train+test (taker): 0

---

## ETH-USD

### Top 30 Strategies by Net Return (Taker 0.20% RT, Full Dataset)

| # | Strategy | N | Gross | Net (Taker) | Net (Maker) | WR | Kelly | PF | Train Net | Test Net | Verdict |
|---|----------|---|-------|-------------|-------------|-----|-------|-----|-----------|----------|---------|
| 1 | Mom60s>0.5%+Flow>1.5→300s | 39 | 0.4159% | 0.2159% | 0.3159% | 48.7% | 33.7% | 3.25 | — | 0.3065% | ⚠️ PARTIAL |
| 2 | Mom 60s>0.5%→300s long | 83 | 0.3641% | 0.1641% | 0.2641% | 43.4% | 25.0% | 2.36 | -0.1449% | 0.2622% | ⚠️ PARTIAL |
| 3 | Mom60s>0.5%+Flow>1.5→600s | 39 | 0.2749% | 0.0749% | 0.1749% | 38.5% | 12.7% | 1.49 | — | 0.1684% | ⚠️ PARTIAL |
| 4 | Mom60s>0.5%+Imb>0.3→300s | 39 | 0.2542% | 0.0542% | 0.1542% | 38.5% | 11.8% | 1.44 | — | 0.1115% | ⚠️ PARTIAL |
| 5 | Mom60s>0.5%+Imb>0.2→300s | 41 | 0.2475% | 0.0475% | 0.1475% | 36.6% | 10.3% | 1.39 | — | 0.1050% | ⚠️ PARTIAL |
| 6 | Mom 15s>0.25%→300s long | 57 | 0.2321% | 0.0321% | 0.1321% | 40.4% | 5.6% | 1.16 | -0.2783% | 0.1640% | ⚠️ PARTIAL |
| 7 | Mom30s>0.3%+Flow>2.0→300s | 52 | 0.2231% | 0.0231% | 0.1231% | 42.3% | 3.9% | 1.10 | -0.3596% | 0.2089% | ⚠️ PARTIAL |
| 8 | Mom 60s>0.5%→600s long | 83 | 0.2087% | 0.0087% | 0.1087% | 32.5% | 1.5% | 1.05 | -0.2840% | 0.1017% | ⚠️ PARTIAL |
| 9 | Mom 60s>0.4%→300s long | 175 | 0.2030% | 0.0030% | 0.1030% | 36.0% | 0.5% | 1.01 | -0.2300% | 0.1070% | ⚠️ PARTIAL |
| 10 | Mom 120s>0.5%→300s long | 280 | 0.1962% | -0.0038% | 0.0962% | 33.9% | 0.0% | 0.98 | -0.2995% | 0.0786% | ❌ |
| 11 | Mom 15s>0.25%→600s long | 56 | 0.1891% | -0.0109% | 0.0891% | 42.9% | 0.0% | 0.95 | -0.3038% | 0.1062% | ❌ |
| 12 | Mom30s>0.3%+Flow>1.5→300s | 63 | 0.1857% | -0.0143% | 0.0857% | 39.7% | 0.0% | 0.94 | -0.3321% | 0.1335% | ❌ |
| 13 | Mom60s>0.5%+Flow>1.5→120s | 39 | 0.1750% | -0.0250% | 0.0750% | 46.2% | 0.0% | 0.80 | — | -0.0064% | ❌ |
| 14 | Mom60s>0.5%+Imb>0.3→600s | 39 | 0.1726% | -0.0274% | 0.0726% | 30.8% | 0.0% | 0.84 | — | 0.0318% | ❌ |
| 15 | Mom 30s>0.3%→300s long | 137 | 0.1705% | -0.0295% | 0.0705% | 36.5% | 0.0% | 0.87 | -0.2665% | 0.0790% | ❌ |
| 16 | Mom 15s>0.25%→600s short | 53 | 0.1700% | -0.0300% | 0.0700% | 39.6% | 0.0% | 0.85 | -0.2279% | 0.0218% | ❌ |
| 17 | Mom 30s>0.4%→300s long | 52 | 0.1673% | -0.0327% | 0.0673% | 36.5% | 0.0% | 0.85 | -0.2963% | 0.0844% | ❌ |
| 18 | Mom60s>0.5%+Imb>0.2→600s | 41 | 0.1643% | -0.0357% | 0.0643% | 29.3% | 0.0% | 0.79 | — | 0.0287% | ❌ |
| 19 | Mom 15s>0.2%→300s long | 138 | 0.1578% | -0.0422% | 0.0578% | 36.2% | 0.0% | 0.81 | -0.1966% | 0.0325% | ❌ |
| 20 | Mom 120s>0.4%→300s long | 493 | 0.1570% | -0.0430% | 0.0570% | 33.7% | 0.0% | 0.81 | -0.2062% | 0.0376% | ❌ |
| 21 | Mom 30s>0.25%→300s long | 246 | 0.1533% | -0.0467% | 0.0533% | 34.1% | 0.0% | 0.80 | -0.2002% | 0.0245% | ❌ |
| 22 | Mom 15s>0.3%→300s long | 30 | 0.1509% | -0.0491% | 0.0509% | 33.3% | 0.0% | 0.77 | — | 0.0252% | ❌ |
| 23 | Mom 120s>0.5%→120s long | 280 | 0.1406% | -0.0594% | 0.0406% | 36.1% | 0.0% | 0.63 | -0.2168% | -0.0155% | ❌ |
| 24 | Mom30s>0.3%+Imb>0.5→300s | 37 | 0.1400% | -0.0600% | 0.0400% | 37.8% | 0.0% | 0.71 | — | 0.0333% | ❌ |
| 25 | MeanRev 60s>0.5%→600s buy_dip | 56 | 0.1358% | -0.0642% | 0.0358% | 39.3% | 0.0% | 0.54 | 0.0559% | -0.1211% | ❌ |
| 26 | Mom 60s>0.5%→120s long | 83 | 0.1316% | -0.0684% | 0.0316% | 39.8% | 0.0% | 0.53 | -0.1212% | -0.0517% | ❌ |
| 27 | Mom30s>0.3%+Imb>0.2→300s | 57 | 0.1299% | -0.0701% | 0.0299% | 33.3% | 0.0% | 0.71 | -0.3654% | 0.0354% | ❌ |
| 28 | Mom60s>0.5%+Imb>0.2→120s | 41 | 0.1292% | -0.0708% | 0.0292% | 34.1% | 0.0% | 0.50 | — | -0.0436% | ❌ |
| 29 | Mom 15s>0.25%→300s short | 53 | 0.1220% | -0.0780% | 0.0220% | 30.2% | 0.0% | 0.61 | -0.3580% | -0.0046% | ❌ |
| 30 | Mom60s>0.5%+Imb>0.3→120s | 39 | 0.1190% | -0.0810% | 0.0190% | 33.3% | 0.0% | 0.44 | — | -0.0570% | ❌ |

### Detailed Analysis — Top 10

#### #1: Mom60s>0.5%+Flow>1.5→300s

**Full Dataset (39 signals across 68h):**
- Gross avg: 0.4159%
- **Net (taker 0.20% RT): 0.2159%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.3159%**
- Win rate: 48.7%
- Avg win: +0.6399%, Avg loss: -0.1869%
- Profit factor: 3.25
- Kelly: 33.7%
- Sharpe (per-trade): 0.364

**Test (last 34h, 31 signals):** Net=0.3065%, WR=54.8%

**Daily P&L Projection:**
- Trades/day: ~14
- Taker: **$2.97/day** on $100 (2.97%/day)
- Maker: **$4.35/day** on $100 (4.35%/day)
- Kelly sizing: 25% of bankroll per trade
- Annualized (taker): **1085%**

---

#### #2: Mom 60s>0.5%→300s long

**Full Dataset (83 signals across 68h):**
- Gross avg: 0.3641%
- **Net (taker 0.20% RT): 0.1641%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.2641%**
- Win rate: 43.4%
- Avg win: +0.6575%, Avg loss: -0.2139%
- Profit factor: 2.36
- Kelly: 25.0%
- Sharpe (per-trade): 0.275

**Train (first 34h, 20 signals):** Net=-0.1449%, WR=20.0%
**Test (last 34h, 63 signals):** Net=0.2622%, WR=50.8%

**Daily P&L Projection:**
- Trades/day: ~29
- Taker: **$4.81/day** on $100 (4.81%/day)
- Maker: **$7.74/day** on $100 (7.74%/day)
- Kelly sizing: 25% of bankroll per trade
- Annualized (taker): **1755%**

**Best hours (EST):**
- 11:00: ✅ gross=0.7735%, net=0.5735%, N=22
- 12:00: ✅ gross=0.4429%, net=0.2429%, N=21
- 09:00: ❌ gross=0.1429%, net=-0.0571%, N=12
- 16:00: ❌ gross=0.1355%, net=-0.0645%, N=8
- 20:00: ❌ gross=0.1131%, net=-0.0869%, N=11

---

#### #3: Mom60s>0.5%+Flow>1.5→600s

**Full Dataset (39 signals across 68h):**
- Gross avg: 0.2749%
- **Net (taker 0.20% RT): 0.0749%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1749%**
- Win rate: 38.5%
- Avg win: +0.5898%, Avg loss: -0.2469%
- Profit factor: 1.49
- Kelly: 12.7%
- Sharpe (per-trade): 0.151

**Test (last 34h, 31 signals):** Net=0.1684%, WR=48.4%

**Daily P&L Projection:**
- Trades/day: ~14
- Taker: **$1.03/day** on $100 (1.03%/day)
- Maker: **$2.41/day** on $100 (2.41%/day)
- Kelly sizing: 13% of bankroll per trade
- Annualized (taker): **376%**

---

#### #4: Mom60s>0.5%+Imb>0.3→300s

**Full Dataset (39 signals across 68h):**
- Gross avg: 0.2542%
- **Net (taker 0.20% RT): 0.0542%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1542%**
- Win rate: 38.5%
- Avg win: +0.4594%, Avg loss: -0.1991%
- Profit factor: 1.44
- Kelly: 11.8%
- Sharpe (per-trade): 0.124

**Test (last 34h, 33 signals):** Net=0.1115%, WR=45.5%

**Daily P&L Projection:**
- Trades/day: ~14
- Taker: **$0.75/day** on $100 (0.75%/day)
- Maker: **$2.12/day** on $100 (2.12%/day)
- Kelly sizing: 12% of bankroll per trade
- Annualized (taker): **272%**

---

#### #5: Mom60s>0.5%+Imb>0.2→300s

**Full Dataset (41 signals across 68h):**
- Gross avg: 0.2475%
- **Net (taker 0.20% RT): 0.0475%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1475%**
- Win rate: 36.6%
- Avg win: +0.4594%, Avg loss: -0.1901%
- Profit factor: 1.39
- Kelly: 10.3%
- Sharpe (per-trade): 0.112

**Test (last 34h, 34 signals):** Net=0.1050%, WR=44.1%

**Daily P&L Projection:**
- Trades/day: ~14
- Taker: **$0.69/day** on $100 (0.69%/day)
- Maker: **$2.13/day** on $100 (2.13%/day)
- Kelly sizing: 10% of bankroll per trade
- Annualized (taker): **251%**

---

#### #6: Mom 15s>0.25%→300s long

**Full Dataset (57 signals across 68h):**
- Gross avg: 0.2321%
- **Net (taker 0.20% RT): 0.0321%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1321%**
- Win rate: 40.4%
- Avg win: +0.5702%, Avg loss: -0.3319%
- Profit factor: 1.16
- Kelly: 5.6%
- Sharpe (per-trade): 0.059

**Train (first 34h, 17 signals):** Net=-0.2783%, WR=11.8%
**Test (last 34h, 40 signals):** Net=0.1640%, WR=52.5%

**Daily P&L Projection:**
- Trades/day: ~20
- Taker: **$0.65/day** on $100 (0.65%/day)
- Maker: **$2.66/day** on $100 (2.66%/day)
- Kelly sizing: 6% of bankroll per trade
- Annualized (taker): **236%**

**Best hours (EST):**
- 11:00: ✅ gross=0.8626%, net=0.6626%, N=7
- 12:00: ✅ gross=0.2818%, net=0.0818%, N=8
- 09:00: ✅ gross=0.2118%, net=0.0118%, N=14

---

#### #7: Mom30s>0.3%+Flow>2.0→300s

**Full Dataset (52 signals across 68h):**
- Gross avg: 0.2231%
- **Net (taker 0.20% RT): 0.0231%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1231%**
- Win rate: 42.3%
- Avg win: +0.5985%, Avg loss: -0.3989%
- Profit factor: 1.10
- Kelly: 3.9%
- Sharpe (per-trade): 0.037

**Train (first 34h, 17 signals):** Net=-0.3596%, WR=11.8%
**Test (last 34h, 35 signals):** Net=0.2089%, WR=57.1%

**Daily P&L Projection:**
- Trades/day: ~18
- Taker: **$0.42/day** on $100 (0.42%/day)
- Maker: **$2.26/day** on $100 (2.26%/day)
- Kelly sizing: 4% of bankroll per trade
- Annualized (taker): **154%**

---

#### #8: Mom 60s>0.5%→600s long

**Full Dataset (83 signals across 68h):**
- Gross avg: 0.2087%
- **Net (taker 0.20% RT): 0.0087%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1087%**
- Win rate: 32.5%
- Avg win: +0.5799%, Avg loss: -0.2666%
- Profit factor: 1.05
- Kelly: 1.5%
- Sharpe (per-trade): 0.019

**Train (first 34h, 20 signals):** Net=-0.2840%, WR=0.0%
**Test (last 34h, 63 signals):** Net=0.1017%, WR=42.9%

**Daily P&L Projection:**
- Trades/day: ~29
- Taker: **$0.26/day** on $100 (0.26%/day)
- Maker: **$3.19/day** on $100 (3.19%/day)
- Kelly sizing: 2% of bankroll per trade
- Annualized (taker): **93%**

**Best hours (EST):**
- 11:00: ✅ gross=0.5110%, net=0.3110%, N=22
- 12:00: ✅ gross=0.3558%, net=0.1558%, N=21
- 09:00: ❌ gross=0.0399%, net=-0.1601%, N=12
- 16:00: ❌ gross=-0.0236%, net=-0.2236%, N=8
- 20:00: ❌ gross=-0.0600%, net=-0.2600%, N=11

---

#### #9: Mom 60s>0.4%→300s long

**Full Dataset (175 signals across 68h):**
- Gross avg: 0.2030%
- **Net (taker 0.20% RT): 0.0030%** → ✅ PROFITABLE
- **Net (maker 0.10% RT): 0.1030%**
- Win rate: 36.0%
- Avg win: +0.5883%, Avg loss: -0.3262%
- Profit factor: 1.01
- Kelly: 0.5%
- Sharpe (per-trade): 0.005

**Train (first 34h, 54 signals):** Net=-0.2300%, WR=16.7%
**Test (last 34h, 121 signals):** Net=0.1070%, WR=44.6%

**Daily P&L Projection:**
- Trades/day: ~62
- Taker: **$0.19/day** on $100 (0.19%/day)
- Maker: **$6.36/day** on $100 (6.36%/day)
- Kelly sizing: 1% of bankroll per trade
- Annualized (taker): **68%**

**Best hours (EST):**
- 11:00: ✅ gross=0.6731%, net=0.4731%, N=33
- 12:00: ✅ gross=0.3713%, net=0.1713%, N=27
- 10:00: ✅ gross=0.3060%, net=0.1060%, N=12
- 16:00: ❌ gross=0.1562%, net=-0.0438%, N=18
- 20:00: ❌ gross=0.0780%, net=-0.1220%, N=18

---

#### #10: Mom 120s>0.5%→300s long

**Full Dataset (280 signals across 68h):**
- Gross avg: 0.1962%
- **Net (taker 0.20% RT): -0.0038%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0962%**
- Win rate: 33.9%
- Avg win: +0.6419%, Avg loss: -0.3354%
- Profit factor: 0.98
- Kelly: 0.0%
- Sharpe (per-trade): -0.007

**Train (first 34h, 61 signals):** Net=-0.2995%, WR=8.2%
**Test (last 34h, 219 signals):** Net=0.0786%, WR=41.1%

**Daily P&L Projection:**
- Trades/day: ~99
- Taker: **$-0.37/day** on $100 (-0.37%/day)
- Maker: **$9.51/day** on $100 (9.51%/day)
- Kelly sizing: 0% of bankroll per trade


**Best hours (EST):**
- 12:00: ✅ gross=0.6228%, net=0.4228%, N=44
- 11:00: ✅ gross=0.5541%, net=0.3541%, N=57
- 09:00: ❌ gross=0.1936%, net=-0.0064%, N=25
- 10:00: ❌ gross=0.1089%, net=-0.0911%, N=41
- 16:00: ❌ gross=0.0550%, net=-0.1450%, N=19

---

### Maker Fee Impact (Top 15)

*Using limit orders at 0.05%/side = 0.10% RT (half the taker cost):*

| # | Strategy | N | Taker Net | Maker Net | Maker WR | Maker PF | Daily/$100 |
|---|----------|---|-----------|-----------|----------|----------|------------|
| 1 | Mom60s>0.5%+Flow>1.5→300s | 39 | 0.2159% | 0.3159% | 69.2% | 6.73 | $4.35 |
| 2 | Mom 60s>0.5%→300s long | 83 | 0.1641% | 0.2641% | 61.4% | 4.57 | $7.74 |
| 3 | Mom60s>0.5%+Flow>1.5→600s | 39 | 0.0749% | 0.1749% | 46.2% | 2.88 | $2.41 |
| 4 | Mom60s>0.5%+Imb>0.3→300s | 39 | 0.0542% | 0.1542% | 64.1% | 3.03 | $2.12 |
| 5 | Mom60s>0.5%+Imb>0.2→300s | 41 | 0.0475% | 0.1475% | 63.4% | 3.04 | $2.13 |
| 6 | Mom 15s>0.25%→300s long | 57 | 0.0321% | 0.1321% | 49.1% | 1.93 | $2.66 |
| 7 | Mom30s>0.3%+Flow>2.0→300s | 52 | 0.0231% | 0.1231% | 53.8% | 1.69 | $2.26 |
| 8 | Mom 60s>0.5%→600s long | 83 | 0.0087% | 0.1087% | 41.0% | 1.95 | $3.19 |
| 9 | Mom 60s>0.4%→300s long | 175 | 0.0030% | 0.1030% | 47.4% | 1.68 | $6.36 |
| 10 | Mom 120s>0.5%→300s long | 280 | -0.0038% | 0.0962% | 46.8% | 1.60 | $9.51 |
| 11 | Mom 15s>0.25%→600s long | 56 | -0.0109% | 0.0891% | 50.0% | 1.62 | $1.76 |
| 12 | Mom30s>0.3%+Flow>1.5→300s | 63 | -0.0143% | 0.0857% | 50.8% | 1.49 | $1.91 |
| 13 | Mom60s>0.5%+Flow>1.5→120s | 39 | -0.0250% | 0.0750% | 53.8% | 2.03 | $1.03 |
| 14 | Mom60s>0.5%+Imb>0.3→600s | 39 | -0.0274% | 0.0726% | 38.5% | 1.69 | $1.00 |
| 15 | Mom 30s>0.3%→300s long | 137 | -0.0295% | 0.0705% | 46.0% | 1.41 | $3.41 |

### Category Performance

| Category | Best Strategy | N | Net (Taker) | Net (Maker) |
|----------|---------------|---|-------------|-------------|
| composite | Mom60s>0.5%+Flow>1.5→300s | 39 | 0.2159% | 0.3159% |
| momentum | Mom 60s>0.5%→300s long | 83 | 0.1641% | 0.2641% |
| mean_reversion | MeanRev 60s>0.5%→600s buy_dip | 56 | -0.0642% | 0.0358% |
| flow | Flow>5.0→300s short | 9327 | -0.1867% | -0.0867% |
| orderbook | OB_Imb>0.7→300s short | 6193 | -0.1878% | -0.0878% |

---

## BTC-USD

### Top 30 Strategies by Net Return (Taker 0.20% RT, Full Dataset)

| # | Strategy | N | Gross | Net (Taker) | Net (Maker) | WR | Kelly | PF | Train Net | Test Net | Verdict |
|---|----------|---|-------|-------------|-------------|-----|-------|-----|-----------|----------|---------|
| 1 | MeanRev 300s>0.5%→300s buy_dip | 416 | 0.1289% | -0.0711% | 0.0289% | 31.7% | 0.0% | 0.43 | -0.0510% | -0.0808% | ❌ |
| 2 | MeanRev 60s>0.3%→600s buy_dip | 104 | 0.1256% | -0.0744% | 0.0256% | 35.6% | 0.0% | 0.58 | 0.0364% | -0.1058% | ❌ |
| 3 | Mom 120s>0.5%→120s long | 56 | 0.1246% | -0.0754% | 0.0246% | 33.9% | 0.0% | 0.47 | — | -0.0664% | ❌ |
| 4 | Mom 30s>0.3%→300s long | 38 | 0.1189% | -0.0811% | 0.0189% | 42.1% | 0.0% | 0.55 | -0.1577% | -0.0413% | ❌ |
| 5 | Mom30s>0.15%+Imb>0.5→300s | 65 | 0.1148% | -0.0852% | 0.0148% | 33.8% | 0.0% | 0.51 | -0.0956% | -0.0799% | ❌ |
| 6 | Mom60s>0.3%+Flow>1.5→300s | 65 | 0.1121% | -0.0879% | 0.0121% | 38.5% | 0.0% | 0.50 | -0.2345% | 0.0302% | ❌ |
| 7 | Mom60s>0.3%+Flow>2.0→300s | 53 | 0.1115% | -0.0885% | 0.0115% | 35.8% | 0.0% | 0.50 | -0.2411% | 0.0700% | ❌ |
| 8 | Mom60s>0.3%+Flow>3.0→300s | 42 | 0.1058% | -0.0942% | 0.0058% | 38.1% | 0.0% | 0.46 | -0.2359% | 0.0346% | ❌ |
| 9 | MeanRev 300s>0.5%→600s buy_dip | 416 | 0.0999% | -0.1001% | -0.0001% | 32.9% | 0.0% | 0.38 | -0.0261% | -0.1360% | ❌ |
| 10 | Mom 60s>0.4%→300s long | 38 | 0.0997% | -0.1003% | -0.0003% | 50.0% | 0.0% | 0.52 | — | -0.0779% | ❌ |
| 11 | Mom30s>0.2%+Imb>0.5→300s | 30 | 0.0994% | -0.1006% | -0.0006% | 36.7% | 0.0% | 0.49 | — | -0.0866% | ❌ |
| 12 | MeanRev 30s>0.2%→600s buy_dip | 151 | 0.0906% | -0.1094% | -0.0094% | 33.1% | 0.0% | 0.44 | -0.1302% | -0.1027% | ❌ |
| 13 | Mom30s>0.15%+Imb>0.5→600s | 65 | 0.0879% | -0.1121% | -0.0121% | 29.2% | 0.0% | 0.38 | -0.1019% | -0.1174% | ❌ |
| 14 | MeanRev 30s>0.15%→600s buy_dip | 504 | 0.0820% | -0.1180% | -0.0180% | 32.5% | 0.0% | 0.40 | -0.1507% | -0.1023% | ❌ |
| 15 | Mom30s>0.15%+Imb>0.5→120s | 65 | 0.0801% | -0.1199% | -0.0199% | 21.5% | 0.0% | 0.21 | -0.1127% | -0.1236% | ❌ |
| 16 | Mom 15s>0.2%→600s long | 41 | 0.0752% | -0.1248% | -0.0248% | 36.6% | 0.0% | 0.47 | -0.1311% | -0.1216% | ❌ |
| 17 | Mom 30s>0.25%→300s long | 81 | 0.0733% | -0.1267% | -0.0267% | 33.3% | 0.0% | 0.40 | -0.1931% | -0.0897% | ❌ |
| 18 | Mom 15s>0.2%→300s long | 41 | 0.0710% | -0.1290% | -0.0290% | 36.6% | 0.0% | 0.40 | -0.1670% | -0.1093% | ❌ |
| 19 | MeanRev 60s>0.2%→600s buy_dip | 569 | 0.0706% | -0.1294% | -0.0294% | 28.3% | 0.0% | 0.36 | -0.1362% | -0.1258% | ❌ |
| 20 | Mom 30s>0.2%→300s long | 205 | 0.0704% | -0.1296% | -0.0296% | 28.3% | 0.0% | 0.36 | -0.1751% | -0.1034% | ❌ |
| 21 | Mom 120s>0.5%→300s long | 56 | 0.0704% | -0.1296% | -0.0296% | 46.4% | 0.0% | 0.34 | — | -0.1203% | ❌ |
| 22 | Mom30s>0.15%+Imb>0.2→300s | 140 | 0.0627% | -0.1373% | -0.0373% | 25.7% | 0.0% | 0.32 | -0.1528% | -0.1246% | ❌ |
| 23 | MeanRev 120s>0.2%→600s buy_dip | 1650 | 0.0604% | -0.1396% | -0.0396% | 28.0% | 0.0% | 0.32 | -0.1384% | -0.1404% | ❌ |
| 24 | Mom 60s>0.3%→300s long | 141 | 0.0600% | -0.1400% | -0.0400% | 36.2% | 0.0% | 0.34 | -0.2275% | -0.0840% | ❌ |
| 25 | MeanRev 120s>0.3%→600s buy_dip | 422 | 0.0584% | -0.1416% | -0.0416% | 27.3% | 0.0% | 0.30 | -0.0917% | -0.1650% | ❌ |
| 26 | Mom 120s>0.4%→120s long | 183 | 0.0576% | -0.1424% | -0.0424% | 22.4% | 0.0% | 0.19 | -0.1895% | -0.1232% | ❌ |
| 27 | MeanRev 60s>0.3%→300s buy_dip | 104 | 0.0545% | -0.1455% | -0.0455% | 27.9% | 0.0% | 0.33 | -0.1168% | -0.1537% | ❌ |
| 28 | Mom30s>0.15%+Imb>0.3→300s | 115 | 0.0544% | -0.1456% | -0.0456% | 25.2% | 0.0% | 0.31 | -0.1636% | -0.1332% | ❌ |
| 29 | Mom30s>0.2%+Imb>0.5→120s | 30 | 0.0536% | -0.1464% | -0.0464% | 20.0% | 0.0% | 0.15 | — | -0.1457% | ❌ |
| 30 | Mom60s>0.3%+Imb>0.3→300s | 32 | 0.0526% | -0.1474% | -0.0474% | 37.5% | 0.0% | 0.39 | -0.2115% | -0.1139% | ❌ |

### Detailed Analysis — Top 10

#### #1: MeanRev 300s>0.5%→300s buy_dip

**Full Dataset (416 signals across 68h):**
- Gross avg: 0.1289%
- **Net (taker 0.20% RT): -0.0711%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0289%**
- Win rate: 31.7%
- Avg win: +0.1703%, Avg loss: -0.1832%
- Profit factor: 0.43
- Kelly: 0.0%
- Sharpe (per-trade): -0.293

**Train (first 34h, 136 signals):** Net=-0.0510%, WR=30.9%
**Test (last 34h, 280 signals):** Net=-0.0808%, WR=32.1%

**Daily P&L Projection:**
- Trades/day: ~147
- Taker: **$-10.43/day** on $100 (-10.43%/day)
- Maker: **$4.25/day** on $100 (4.25%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #2: MeanRev 60s>0.3%→600s buy_dip

**Full Dataset (104 signals across 68h):**
- Gross avg: 0.1256%
- **Net (taker 0.20% RT): -0.0744%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0256%**
- Win rate: 35.6%
- Avg win: +0.2830%, Avg loss: -0.2717%
- Profit factor: 0.58
- Kelly: 0.0%
- Sharpe (per-trade): -0.217

**Train (first 34h, 23 signals):** Net=0.0364%, WR=60.9%
**Test (last 34h, 81 signals):** Net=-0.1058%, WR=28.4%

**Daily P&L Projection:**
- Trades/day: ~37
- Taker: **$-2.73/day** on $100 (-2.73%/day)
- Maker: **$0.94/day** on $100 (0.94%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #3: Mom 120s>0.5%→120s long

**Full Dataset (56 signals across 68h):**
- Gross avg: 0.1246%
- **Net (taker 0.20% RT): -0.0754%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0246%**
- Win rate: 33.9%
- Avg win: +0.1983%, Avg loss: -0.2159%
- Profit factor: 0.47
- Kelly: 0.0%
- Sharpe (per-trade): -0.310

**Test (last 34h, 52 signals):** Net=-0.0664%, WR=36.5%

**Daily P&L Projection:**
- Trades/day: ~20
- Taker: **$-1.49/day** on $100 (-1.49%/day)
- Maker: **$0.49/day** on $100 (0.49%/day)
- Kelly sizing: 0% of bankroll per trade


**Best hours (EST):**
- 09:00: ❌ gross=0.1896%, net=-0.0104%, N=31
- 10:00: ❌ gross=0.1687%, net=-0.0313%, N=7
- 11:00: ❌ gross=0.0970%, net=-0.1030%, N=7
- 12:00: ❌ gross=-0.0926%, net=-0.2926%, N=6

---

#### #4: Mom 30s>0.3%→300s long

**Full Dataset (38 signals across 68h):**
- Gross avg: 0.1189%
- **Net (taker 0.20% RT): -0.0811%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0189%**
- Win rate: 42.1%
- Avg win: +0.2325%, Avg loss: -0.3092%
- Profit factor: 0.55
- Kelly: 0.0%
- Sharpe (per-trade): -0.219

**Train (first 34h, 13 signals):** Net=-0.1577%, WR=15.4%
**Test (last 34h, 25 signals):** Net=-0.0413%, WR=56.0%

**Daily P&L Projection:**
- Trades/day: ~13
- Taker: **$-1.09/day** on $100 (-1.09%/day)
- Maker: **$0.25/day** on $100 (0.25%/day)
- Kelly sizing: 0% of bankroll per trade


**Best hours (EST):**
- 09:00: ❌ gross=0.1206%, net=-0.0794%, N=18
- 20:00: ❌ gross=0.0990%, net=-0.1010%, N=6

---

#### #5: Mom30s>0.15%+Imb>0.5→300s

**Full Dataset (65 signals across 68h):**
- Gross avg: 0.1148%
- **Net (taker 0.20% RT): -0.0852%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0148%**
- Win rate: 33.8%
- Avg win: +0.2625%, Avg loss: -0.2632%
- Profit factor: 0.51
- Kelly: 0.0%
- Sharpe (per-trade): -0.254

**Train (first 34h, 22 signals):** Net=-0.0956%, WR=31.8%
**Test (last 34h, 43 signals):** Net=-0.0799%, WR=34.9%

**Daily P&L Projection:**
- Trades/day: ~23
- Taker: **$-1.96/day** on $100 (-1.96%/day)
- Maker: **$0.34/day** on $100 (0.34%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #6: Mom60s>0.3%+Flow>1.5→300s

**Full Dataset (65 signals across 68h):**
- Gross avg: 0.1121%
- **Net (taker 0.20% RT): -0.0879%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0121%**
- Win rate: 38.5%
- Avg win: +0.2254%, Avg loss: -0.2838%
- Profit factor: 0.50
- Kelly: 0.0%
- Sharpe (per-trade): -0.283

**Train (first 34h, 29 signals):** Net=-0.2345%, WR=13.8%
**Test (last 34h, 36 signals):** Net=0.0302%, WR=58.3%

**Daily P&L Projection:**
- Trades/day: ~23
- Taker: **$-2.02/day** on $100 (-2.02%/day)
- Maker: **$0.28/day** on $100 (0.28%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #7: Mom60s>0.3%+Flow>2.0→300s

**Full Dataset (53 signals across 68h):**
- Gross avg: 0.1115%
- **Net (taker 0.20% RT): -0.0885%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0115%**
- Win rate: 35.8%
- Avg win: +0.2424%, Avg loss: -0.2734%
- Profit factor: 0.50
- Kelly: 0.0%
- Sharpe (per-trade): -0.287

**Train (first 34h, 27 signals):** Net=-0.2411%, WR=11.1%
**Test (last 34h, 26 signals):** Net=0.0700%, WR=61.5%

**Daily P&L Projection:**
- Trades/day: ~19
- Taker: **$-1.66/day** on $100 (-1.66%/day)
- Maker: **$0.22/day** on $100 (0.22%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #8: Mom60s>0.3%+Flow>3.0→300s

**Full Dataset (42 signals across 68h):**
- Gross avg: 0.1058%
- **Net (taker 0.20% RT): -0.0942%** → ❌ LOSS
- **Net (maker 0.10% RT): 0.0058%**
- Win rate: 38.1%
- Avg win: +0.2113%, Avg loss: -0.2822%
- Profit factor: 0.46
- Kelly: 0.0%
- Sharpe (per-trade): -0.317

**Train (first 34h, 20 signals):** Net=-0.2359%, WR=10.0%
**Test (last 34h, 22 signals):** Net=0.0346%, WR=63.6%

**Daily P&L Projection:**
- Trades/day: ~15
- Taker: **$-1.40/day** on $100 (-1.40%/day)
- Maker: **$0.09/day** on $100 (0.09%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #9: MeanRev 300s>0.5%→600s buy_dip

**Full Dataset (416 signals across 68h):**
- Gross avg: 0.0999%
- **Net (taker 0.20% RT): -0.1001%** → ❌ LOSS
- **Net (maker 0.10% RT): -0.0001%**
- Win rate: 32.9%
- Avg win: +0.1842%, Avg loss: -0.2397%
- Profit factor: 0.38
- Kelly: 0.0%
- Sharpe (per-trade): -0.384

**Train (first 34h, 136 signals):** Net=-0.0261%, WR=37.5%
**Test (last 34h, 280 signals):** Net=-0.1360%, WR=30.7%

**Daily P&L Projection:**
- Trades/day: ~147
- Taker: **$-14.70/day** on $100 (-14.70%/day)
- Maker: **$-0.01/day** on $100 (-0.01%/day)
- Kelly sizing: 0% of bankroll per trade


---

#### #10: Mom 60s>0.4%→300s long

**Full Dataset (38 signals across 68h):**
- Gross avg: 0.0997%
- **Net (taker 0.20% RT): -0.1003%** → ❌ LOSS
- **Net (maker 0.10% RT): -0.0003%**
- Win rate: 50.0%
- Avg win: +0.2173%, Avg loss: -0.4180%
- Profit factor: 0.52
- Kelly: 0.0%
- Sharpe (per-trade): -0.239

**Test (last 34h, 29 signals):** Net=-0.0779%, WR=62.1%

**Daily P&L Projection:**
- Trades/day: ~13
- Taker: **$-1.35/day** on $100 (-1.35%/day)
- Maker: **$-0.00/day** on $100 (-0.00%/day)
- Kelly sizing: 0% of bankroll per trade


**Best hours (EST):**
- 12:00: ✅ gross=0.3394%, net=0.1394%, N=6
- 03:00: ❌ gross=0.0196%, net=-0.1804%, N=5
- 09:00: ❌ gross=-0.0189%, net=-0.2189%, N=20

---

### Maker Fee Impact (Top 15)

*Using limit orders at 0.05%/side = 0.10% RT (half the taker cost):*

| # | Strategy | N | Taker Net | Maker Net | Maker WR | Maker PF | Daily/$100 |
|---|----------|---|-----------|-----------|----------|----------|------------|
| 1 | MeanRev 300s>0.5%→300s buy_dip | 416 | -0.0711% | 0.0289% | 51.4% | 1.43 | $4.25 |
| 2 | MeanRev 60s>0.3%→600s buy_dip | 104 | -0.0744% | 0.0256% | 50.0% | 1.22 | $0.94 |
| 3 | Mom 120s>0.5%→120s long | 56 | -0.0754% | 0.0246% | 50.0% | 1.29 | $0.49 |
| 4 | Mom 30s>0.3%→300s long | 38 | -0.0811% | 0.0189% | 65.8% | 1.14 | $0.25 |
| 5 | Mom30s>0.15%+Imb>0.5→300s | 65 | -0.0852% | 0.0148% | 53.8% | 1.12 | $0.34 |
| 6 | Mom60s>0.3%+Flow>1.5→300s | 65 | -0.0879% | 0.0121% | 47.7% | 1.10 | $0.28 |
| 7 | Mom60s>0.3%+Flow>2.0→300s | 53 | -0.0885% | 0.0115% | 43.4% | 1.10 | $0.22 |
| 8 | Mom60s>0.3%+Flow>3.0→300s | 42 | -0.0942% | 0.0058% | 42.9% | 1.05 | $0.09 |
| 9 | MeanRev 300s>0.5%→600s buy_dip | 416 | -0.1001% | -0.0001% | 50.0% | 1.00 | $-0.01 |
| 10 | Mom 60s>0.4%→300s long | 38 | -0.1003% | -0.0003% | 63.2% | 1.00 | $-0.00 |
| 11 | Mom30s>0.2%+Imb>0.5→300s | 30 | -0.1006% | -0.0006% | 60.0% | 1.00 | $-0.01 |
| 12 | MeanRev 30s>0.2%→600s buy_dip | 151 | -0.1094% | -0.0094% | 41.7% | 0.93 | $-0.50 |
| 13 | Mom30s>0.15%+Imb>0.5→600s | 65 | -0.1121% | -0.0121% | 44.6% | 0.89 | $-0.28 |
| 14 | MeanRev 30s>0.15%→600s buy_dip | 504 | -0.1180% | -0.0180% | 42.7% | 0.87 | $-3.21 |
| 15 | Mom30s>0.15%+Imb>0.5→120s | 65 | -0.1199% | -0.0199% | 46.2% | 0.77 | $-0.46 |

### Category Performance

| Category | Best Strategy | N | Net (Taker) | Net (Maker) |
|----------|---------------|---|-------------|-------------|
| mean_reversion | MeanRev 300s>0.5%→300s buy_dip | 416 | -0.0711% | 0.0289% |
| momentum | Mom 120s>0.5%→120s long | 56 | -0.0754% | 0.0246% |
| composite | Mom30s>0.15%+Imb>0.5→300s | 65 | -0.0852% | 0.0148% |
| flow | Flow>5.0→120s short | 10182 | -0.1938% | -0.0938% |
| orderbook | OB_Imb>0.7→60s short | 8360 | -0.1952% | -0.0952% |

---

## Final Recommendations

### ✅ Profitable Strategies (Full Dataset, Taker Fees)

**9 strategies show positive expected value with 0.20% RT fees.**

| # | Product | Strategy | N | Net/Trade | WR | PF | Kelly | Trades/Day | Daily/$100 | Train/Test |
|---|---------|----------|---|-----------|-----|-----|-------|------------|------------|------------|
| 1 | ETH-USD | Mom 60s>0.5%→300s long | 83 | 0.1641% | 43.4% | 2.36 | 25.0% | 29 | $4.81 | -0.145/0.262 |
| 2 | ETH-USD | Mom60s>0.5%+Flow>1.5→300s | 39 | 0.2159% | 48.7% | 3.25 | 33.7% | 14 | $2.97 |  |
| 3 | ETH-USD | Mom60s>0.5%+Flow>1.5→600s | 39 | 0.0749% | 38.5% | 1.49 | 12.7% | 14 | $1.03 |  |
| 4 | ETH-USD | Mom60s>0.5%+Imb>0.3→300s | 39 | 0.0542% | 38.5% | 1.44 | 11.8% | 14 | $0.75 |  |
| 5 | ETH-USD | Mom60s>0.5%+Imb>0.2→300s | 41 | 0.0475% | 36.6% | 1.39 | 10.3% | 14 | $0.69 |  |
| 6 | ETH-USD | Mom 15s>0.25%→300s long | 57 | 0.0321% | 40.4% | 1.16 | 5.6% | 20 | $0.65 | -0.278/0.164 |
| 7 | ETH-USD | Mom30s>0.3%+Flow>2.0→300s | 52 | 0.0231% | 42.3% | 1.10 | 3.9% | 18 | $0.42 | -0.360/0.209 |
| 8 | ETH-USD | Mom 60s>0.5%→600s long | 83 | 0.0087% | 32.5% | 1.05 | 1.5% | 29 | $0.26 | -0.284/0.102 |
| 9 | ETH-USD | Mom 60s>0.4%→300s long | 175 | 0.0030% | 36.0% | 1.01 | 0.5% | 62 | $0.19 | -0.230/0.107 |

### 🏆 Top Pick: ETH-USD — Mom 60s>0.5%→300s long

- Net return per trade: **0.1641%** (taker) / **0.2641%** (maker)
- Win rate: **43.4%**
- Profit factor: **2.36**
- Kelly criterion: **25.0%** (use half-Kelly: 12%)
- Trades per day: **~29**
- **Daily expected (taker): $4.81 on $100**
- **Daily expected (maker): $7.74 on $100**
- Annualized (taker): **1755%** / (maker): **2824%**

**Robustness (train/test split):**
- Train: net=-0.1449%, WR=20.0%, N=20
- Test: net=0.2622%, WR=50.8%, N=63
- ⚠️ Test profitable but train negative — signal may be regime-dependent

### ⚠️ Important Caveats

1. **Sample size**: 68 hours is a very short period. These results need validation over weeks/months.
2. **Execution assumptions**: Analysis assumes instant execution at mid-price. Real trading faces:
   - Slippage (especially for momentum signals where you're chasing)
   - Fill rate for limit orders (maker fee only works if your order gets filled)
   - Latency between signal detection and order placement
3. **Market regime**: The data covers a specific 68-hour window. Results may not generalize.
4. **Signal frequency**: High-frequency signals (>100/day) may overlap, reducing effective trade count.
5. **The momentum paradox**: Momentum continuation requires TAKER entry (you must buy immediately
   when you see the signal). You cannot use MAKER entry for momentum — by the time your limit
   order fills, the momentum is already gone. Budget 0.20% RT for momentum strategies.

### Recommended Next Steps

1. **Paper trade the top 3 strategies** for 1 week to validate
2. **Start with small size** ($10-50 per trade) for live validation
3. **Track actual execution quality** — slippage, fill rate, latency
4. **Focus on maker strategies** where possible (mean reversion allows limit orders)
5. **Re-run this analysis weekly** as more data accumulates

### Comparison to Previous Report

| Metric | Previous (0.50% RT) | Corrected (0.20% RT taker) |
|--------|--------------------|-----------------------------|
| Fee assumption | 0.50% RT | 0.20% RT (taker) / 0.10% RT (maker) |
| Best signal net | -0.097% | +0.164% |
| Verdict | ❌ Unprofitable | ✅ 9 profitable strategies |
| Profitable strategies (full dataset) | 0 | 9 |
| Best daily/$100 (taker) | $0 | $4.81 |
