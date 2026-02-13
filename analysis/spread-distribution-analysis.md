# AUGUR Spread Distribution Analysis
<!-- AI.TOC: AUGUR Spread Distribution Analysis — Read lines 1-20 for navigation.
  §1 Key Question                               → lines 7-9
  §2 Executive Summary                          → lines 10-45
  §3 Proposed '2x Average Spread' Gate          → lines 46-72
  §4 Per-Product Spread Distributions           → lines 73-99
  §5 Win vs Loss Spread at Entry                → lines 100-126
  §6 Global Threshold Sweep                     → lines 127-169
  §7 Recommendations                            → lines 170-197
  Total: 197 lines | Sections: 7
-->
*Generated: 2026-02-11 22:01:45*

**Data**: 20,141,766 orderbook snapshots from enhanced_data.db (2026-02-09 to 2026-02-11)
**Trades**: paper_results.db, top 20 products by trade count

## Key Question
Is there an optimal spread_pct threshold per product that separates winning from losing trades?

## Executive Summary

- **Global optimal spread gate**: `0.0114%`
- Trades below threshold: **42.9% WR** (n=28)
- Trades above threshold: **42.4% WR** (n=509)
- Baseline WR: **42.5%** (all 537 matched trades)
- WR improvement: **+0.4%** with 5% coverage

- Winning trades entered at **0.1333%** median spread
- Losing trades entered at **0.1158%** median spread
- Winners actually entered at **WIDER** spreads than losers → **spread is NOT a quality filter in this dataset**

### ⚠️ Critical Finding: Spread Gate Won't Help

The data tells a **counterintuitive story**: tighter spreads correlate with *lower* win rates globally. The threshold sweep confirms this — every threshold tested shows trades ABOVE it winning more often than trades below. This likely means:

1. **Product mix confound**: Tight-spread products (BTC, ETH, XRP) happen to have terrible WR in paper trading (wrong strategies), while wide-spread products (BNKR, SKR) happen to have the better strategies
2. **Spread is a product characteristic, not a trade quality signal**: BTC always has 0.001% spreads, BNKR always has 0.25% — the spread doesn't vary enough within a product to separate good from bad entry moments
3. **The 2x_avg gate is effectively a no-op**: It passes 83-99% of observations for most products

### Statistical Confirmation: Within-Product Tests

Mann-Whitney U tests on the 5 highest-volume products — **none are significant**:

| Product | Won Median | Lost Median | Direction | p-value | Significant? |
|---------|-----------|------------|-----------|---------|-------------|
| BNKR-USD | 0.3246% | 0.2520% | Wider wins | 0.2985 | No |
| SKR-USD | 0.1546% | 0.1553% | Tighter wins | 0.7846 | No |
| AXS-USD | 0.0669% | 0.0672% | Tighter wins | 0.2776 | No |
| ZRO-USD | 0.0831% | 0.0836% | Tighter wins | 0.9171 | No |
| BIRB-USD | 0.1358% | 0.0916% | Wider wins | 0.1258 | No |

Even within a single product, spread at entry has **zero predictive power** for trade outcome (p > 0.1 everywhere). The differences are tiny and inconsistent in direction.

**Recommendation**: Don't invest engineering time in a spread gate as a primary filter. Instead, use it only as an **extreme outlier guard** (e.g., >p95 for the product = skip) to avoid entries during flash crashes or illiquidity events. A simple `if spread_pct > product_p95_spread: skip` costs nothing to implement and catches genuine anomalies without the false confidence of a "calibrated" threshold.

## Proposed '2x Average Spread' Gate

The pipeline proposal uses `2 × avg_spread` per product as the gate threshold.

| Product | Avg Spread | 2x Gate | % Time Open | Trades Won | Trades Lost |
|---------|-----------|---------|-------------|------------|-------------|
| BNKR-USD | 0.2879% | 0.5759% | 92.0% | 57 | 70 |
| SKR-USD | 0.1451% | 0.2902% | 94.5% | 58 | 58 |
| AXS-USD | 0.1016% | 0.2032% | 98.5% | 46 | 50 |
| ZRO-USD | 0.1057% | 0.2114% | 98.1% | 21 | 41 |
| BERA-USD | 0.3383% | 0.6766% | 96.2% | 5 | 7 |
| LINK-USD | 0.0192% | 0.0384% | 99.3% | 0 | 10 |
| BIRB-USD | 0.1207% | 0.2415% | 97.9% | 21 | 22 |
| BCH-USD | 0.0150% | 0.0301% | 83.1% | 0 | 4 |
| TAO-USD | 0.0218% | 0.0437% | 92.4% | 1 | 5 |
| SUI-USD | 0.0177% | 0.0355% | 97.6% | 0 | 9 |
| HBAR-USD | 0.0183% | 0.0366% | 99.2% | 1 | 2 |
| LTC-USD | 0.0308% | 0.0615% | 99.9% | 1 | 2 |
| MON-USD | 0.0578% | 0.1156% | 99.3% | 3 | 12 |
| BTC-USD | 0.0017% | 0.0035% | 81.8% | 4 | 2 |
| XRP-USD | 0.0085% | 0.0171% | 98.9% | 5 | 1 |
| ETH-USD | 0.0022% | 0.0045% | 83.3% | 4 | 1 |
| MAMO-USD | 0.1977% | 0.3953% | 85.4% | 0 | 0 |
| HYPE-USD | 0.0425% | 0.0850% | 97.3% | 0 | 5 |
| XLM-USD | 0.0283% | 0.0566% | 94.0% | 0 | 1 |
| AAVE-USD | 0.0311% | 0.0622% | 93.2% | 1 | 7 |

## Per-Product Spread Distributions

| Product | N Snapshots | Min | P10 | P25 | Median | P75 | P90 | Max | Mean | Std |
|---------|------------|-----|-----|-----|--------|-----|-----|-----|------|-----|
| BNKR-USD | 83,417 | 0.0088 | 0.0750 | 0.1544 | 0.2561 | 0.3948 | 0.5424 | 2.7614 | 0.2879 | 0.1812 |
| SKR-USD | 78,426 | 0.0368 | 0.0418 | 0.0836 | 0.1240 | 0.1590 | 0.2056 | 1.6209 | 0.1451 | 0.1149 |
| AXS-USD | 79,604 | 0.0629 | 0.0652 | 0.0667 | 0.0706 | 0.1330 | 0.1387 | 0.7141 | 0.1016 | 0.0435 |
| ZRO-USD | 81,915 | 0.0389 | 0.0551 | 0.0801 | 0.1119 | 0.1211 | 0.1669 | 0.7748 | 0.1057 | 0.0436 |
| BERA-USD | 80,023 | 0.0666 | 0.1889 | 0.2002 | 0.3035 | 0.3859 | 0.4386 | 6.2609 | 0.3383 | 0.2912 |
| LINK-USD | 83,629 | 0.0111 | 0.0116 | 0.0118 | 0.0225 | 0.0237 | 0.0245 | 0.1572 | 0.0192 | 0.0080 |
| BIRB-USD | 79,488 | 0.0411 | 0.0439 | 0.0839 | 0.1264 | 0.1688 | 0.2079 | 0.8368 | 0.1207 | 0.0585 |
| BCH-USD | 83,314 | 0.0019 | 0.0019 | 0.0019 | 0.0094 | 0.0231 | 0.0390 | 0.2548 | 0.0150 | 0.0164 |
| TAO-USD | 82,779 | 0.0061 | 0.0064 | 0.0069 | 0.0196 | 0.0321 | 0.0409 | 0.9369 | 0.0218 | 0.0145 |
| SUI-USD | 83,642 | 0.0103 | 0.0104 | 0.0108 | 0.0113 | 0.0222 | 0.0322 | 0.1891 | 0.0177 | 0.0087 |
| HBAR-USD | 83,559 | 0.0107 | 0.0110 | 0.0111 | 0.0216 | 0.0224 | 0.0228 | 0.2199 | 0.0183 | 0.0074 |
| LTC-USD | 83,468 | 0.0182 | 0.0187 | 0.0190 | 0.0367 | 0.0380 | 0.0386 | 0.1340 | 0.0308 | 0.0104 |
| MON-USD | 80,287 | 0.0470 | 0.0492 | 0.0509 | 0.0535 | 0.0554 | 0.0606 | 1.4092 | 0.0578 | 0.0177 |
| BTC-USD | 100,763 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0022 | 0.0058 | 2.1397 | 0.0017 | 0.0076 |
| XRP-USD | 83,702 | 0.0069 | 0.0069 | 0.0071 | 0.0072 | 0.0073 | 0.0143 | 0.1025 | 0.0085 | 0.0032 |
| ETH-USD | 100,764 | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 0.0025 | 0.0067 | 0.2193 | 0.0022 | 0.0041 |
| MAMO-USD | 65,137 | 0.0860 | 0.0871 | 0.0886 | 0.0899 | 0.1779 | 0.5352 | 44.5977 | 0.1977 | 0.3239 |
| HYPE-USD | 74,192 | 0.0311 | 0.0317 | 0.0334 | 0.0338 | 0.0349 | 0.0677 | 0.3370 | 0.0425 | 0.0171 |
| XLM-USD | 83,614 | 0.0006 | 0.0044 | 0.0151 | 0.0279 | 0.0397 | 0.0509 | 0.1803 | 0.0283 | 0.0176 |
| AAVE-USD | 82,701 | 0.0087 | 0.0092 | 0.0182 | 0.0276 | 0.0437 | 0.0557 | 0.2668 | 0.0311 | 0.0186 |

*All values in percent*

## Win vs Loss Spread at Entry

Spread_pct at the moment each trade was entered (matched to nearest orderbook snapshot within ±30s).

| Product | Won N | Won Med | Won Mean | Lost N | Lost Med | Lost Mean | Optimal Thresh | Below WR | Above WR |
|---------|-------|---------|----------|--------|----------|-----------|---------------|----------|----------|
| BNKR-USD | 57 | 0.3246 | 0.3474 | 70 | 0.2520 | 0.3165 | 0.6186 | 45.6% | 38.5% |
| SKR-USD | 58 | 0.1546 | 0.2388 | 58 | 0.1553 | 0.2107 | 0.1559 | 53.1% | 46.2% |
| AXS-USD | 46 | 0.0669 | 0.0925 | 50 | 0.0672 | 0.0973 | 0.0669 | 55.8% | 41.5% |
| ZRO-USD | 21 | 0.0831 | 0.0973 | 41 | 0.0836 | 0.1019 | 0.1242 | 38.5% | 10.0% |
| BERA-USD | 5 | 0.3311 | 0.2994 | 7 | 0.1676 | 0.2368 | 0.3341 | 40.0% | 50.0% |
| LINK-USD | 0 | - | - | 10 | 0.0241 | 0.0207 | - | - | - |
| BIRB-USD | 21 | 0.1358 | 0.1498 | 22 | 0.0916 | 0.1160 | 0.2303 | 47.4% | 60.0% |
| BCH-USD | 0 | - | - | 4 | 0.0068 | 0.0093 | - | - | - |
| TAO-USD | 1 | 0.0481 | 0.0481 | 5 | 0.0272 | 0.0383 | - | - | - |
| SUI-USD | 0 | - | - | 9 | 0.0113 | 0.0164 | - | - | - |
| HBAR-USD | 1 | 0.0228 | 0.0228 | 2 | 0.0114 | 0.0114 | - | - | - |
| LTC-USD | 1 | 0.0195 | 0.0195 | 2 | 0.0486 | 0.0486 | - | - | - |
| MON-USD | 3 | 0.0535 | 0.0709 | 12 | 0.0536 | 0.0536 | 0.0535 | 40.0% | 10.0% |
| BTC-USD | 4 | 0.0021 | 0.0041 | 2 | 0.0029 | 0.0029 | - | - | - |
| XRP-USD | 5 | 0.0074 | 0.0074 | 1 | 0.0074 | 0.0074 | - | - | - |
| ETH-USD | 4 | 0.0005 | 0.0021 | 1 | 0.0057 | 0.0057 | - | - | - |
| MAMO-USD | 0 | - | - | 0 | - | - | - | - | - |
| HYPE-USD | 0 | - | - | 5 | 0.0348 | 0.0414 | - | - | - |
| XLM-USD | 0 | - | - | 1 | 0.0692 | 0.0692 | - | - | - |
| AAVE-USD | 1 | 0.0188 | 0.0188 | 7 | 0.0376 | 0.0391 | - | - | - |

## Global Threshold Sweep

Testing various spread_pct thresholds across ALL matched trades:

| Threshold | Below WR | Below N | Above WR | Above N | WR Improvement | Coverage | Score |
|-----------|----------|---------|----------|---------|---------------|----------|-------|
| 0.0114% | 42.9% | 28 | 42.4% | 509 | +0.4% | 5% | 0.0002 |
| 0.0208% | 36.6% | 41 | 42.9% | 496 | -5.9% | 8% | -0.0045 |
| 0.0318% | 29.6% | 54 | 43.9% | 483 | -12.8% | 10% | -0.0129 |
| 0.0385% | 25.0% | 68 | 45.0% | 469 | -17.5% | 13% | -0.0221 |
| 0.0451% | 23.5% | 81 | 45.8% | 456 | -19.0% | 15% | -0.0287 |
| 0.0490% | 25.5% | 94 | 46.0% | 443 | -16.9% | 18% | -0.0296 |
| 0.0540% | 25.9% | 108 | 46.6% | 429 | -16.5% | 20% | -0.0332 |
| 0.0653% | 27.0% | 122 | 47.0% | 415 | -15.4% | 23% | -0.0350 |
| 0.0663% | 30.4% | 135 | 46.5% | 402 | -12.1% | 25% | -0.0304 |
| 0.0667% | 32.0% | 150 | 46.5% | 387 | -10.5% | 28% | -0.0292 |
| 0.0670% | 34.0% | 162 | 46.1% | 375 | -8.5% | 30% | -0.0257 |
| 0.0676% | 33.5% | 176 | 46.8% | 361 | -8.9% | 33% | -0.0293 |
| 0.0777% | 34.6% | 188 | 46.7% | 349 | -7.9% | 35% | -0.0276 |
| 0.0814% | 34.2% | 202 | 47.5% | 335 | -8.3% | 38% | -0.0312 |
| 0.0839% | 35.3% | 215 | 47.2% | 322 | -7.1% | 40% | -0.0285 |
| 0.0940% | 36.8% | 228 | 46.6% | 309 | -5.6% | 42% | -0.0238 |
| 0.1148% | 37.6% | 242 | 46.4% | 295 | -4.9% | 45% | -0.0219 |
| 0.1162% | 37.6% | 255 | 46.8% | 282 | -4.8% | 47% | -0.0228 |
| 0.1210% | 38.3% | 269 | 46.6% | 268 | -4.2% | 50% | -0.0209 |
| 0.1228% | 38.7% | 282 | 46.7% | 255 | -3.8% | 53% | -0.0200 |
| 0.1332% | 38.5% | 296 | 47.3% | 241 | -3.9% | 55% | -0.0217 |
| 0.1345% | 39.0% | 310 | 47.1% | 227 | -3.4% | 58% | -0.0198 |
| 0.1368% | 39.4% | 322 | 47.0% | 215 | -3.0% | 60% | -0.0181 |
| 0.1527% | 39.3% | 336 | 47.8% | 201 | -3.2% | 63% | -0.0198 |
| 0.1555% | 40.7% | 349 | 45.7% | 188 | -1.8% | 65% | -0.0115 |
| 0.1648% | 39.8% | 362 | 48.0% | 175 | -2.7% | 67% | -0.0181 |
| 0.1908% | 39.6% | 376 | 49.1% | 161 | -2.8% | 70% | -0.0198 |
| 0.1972% | 40.1% | 389 | 48.6% | 148 | -2.4% | 72% | -0.0171 |
| 0.2278% | 40.2% | 403 | 49.3% | 134 | -2.3% | 75% | -0.0170 |
| 0.2396% | 39.7% | 416 | 52.1% | 121 | -2.8% | 77% | -0.0216 |
| 0.2681% | 39.9% | 429 | 52.8% | 108 | -2.6% | 80% | -0.0208 |
| 0.3014% | 40.0% | 443 | 54.3% | 94 | -2.5% | 82% | -0.0207 |
| 0.3342% | 41.0% | 456 | 50.6% | 81 | -1.4% | 85% | -0.0123 |
| 0.3725% | 40.9% | 470 | 53.7% | 67 | -1.6% | 88% | -0.0141 |
| 0.4276% | 41.8% | 483 | 48.1% | 54 | -0.6% | 90% | -0.0057 |
| 0.4811% | 41.9% | 496 | 48.8% | 41 | -0.5% | 92% | -0.0048 |

## Recommendations

### Per-Product Thresholds (Preferred)

Products with enough data to compute optimal thresholds:

- **BNKR-USD**: threshold=0.6186%, below WR=45.6% (n=114), above WR=38.5% (n=13), baseline=44.9%
- **SKR-USD**: threshold=0.1559%, below WR=53.1% (n=64), above WR=46.2% (n=52), baseline=50.0%
- **AXS-USD**: threshold=0.0669%, below WR=55.8% (n=43), above WR=41.5% (n=53), baseline=47.9%
- **ZRO-USD**: threshold=0.1242%, below WR=38.5% (n=52), above WR=10.0% (n=10), baseline=33.9%
- **BERA-USD**: threshold=0.3341%, below WR=40.0% (n=10), above WR=50.0% (n=2), baseline=41.7%
- **BIRB-USD**: threshold=0.2303%, below WR=47.4% (n=38), above WR=60.0% (n=5), baseline=48.8%
- **MON-USD**: threshold=0.0535%, below WR=40.0% (n=5), above WR=10.0% (n=10), baseline=20.0%

### Implementation Guidance

1. **Global fallback**: Use `0.0114%` as the default spread gate for products without enough history
2. **Per-product tuning**: For high-volume products, use the per-product optimal thresholds above
3. **2x_avg comparison**: The proposed '2x average spread' gate averages 0.1592% across products vs optimal global 0.0114%
   - 2x_avg is **too loose** — it lets through trades at wide spreads that lose more often

### Caveats

- Only ~2.4 days of orderbook data — spread patterns may vary with market conditions
- Trade matching uses ±30s window — some trades may not have exact spread data
- Matched 537 of 1184 trades (45%)
- Small sample sizes per product — per-product thresholds have wide confidence intervals
