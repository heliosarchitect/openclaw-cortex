# Multi-Asset Opportunity Scanner - Summary

## ✅ **COMPLETED**

A production-ready scanner that finds trading opportunities across all Coinbase USD pairs.

### Delivered Components

1. **✅ scripts/scan_opportunities.py** - Main scanner (496 lines)
   - Scans top 75 liquid pairs by 24h volume
   - Calculates RSI, MACD, Bollinger Bands, Volume Profile
   - Implements Mean Reversion and Momentum strategies
   - Scores opportunities 0-100 based on signal strength
   - Outputs top 10 to JSON file
   - **Fast**: Completes in ~1.2 seconds
   - **Efficient**: 5-minute caching, async HTTP calls
   - **Cron-ready**: No interactive prompts, logs to file

2. **✅ scripts/market_indicators.py** - Technical indicators library (231 lines)
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands with position percentage
   - Volume Profile (avg volume, ratios)
   - Trend analysis (uptrend/downtrend/sideways)
   - Volatility calculation

3. **✅ market_opportunities.json** - Output file
   - Top 10 opportunities with full details
   - Symbol, price, score, setup type
   - All indicator values
   - Signal descriptions
   - Timestamp

4. **✅ scripts/SCANNER_README.md** - Complete documentation
   - Usage instructions
   - Scoring system explanation
   - Output format reference
   - Integration examples
   - Troubleshooting guide

5. **✅ scripts/scanner_cron.txt** - Cron configuration
   - Multiple schedule options
   - CPU load recommendations
   - Installation instructions
   - Log rotation setup

## Test Results

**Latest Run (Feb 3, 2026 21:53 EST):**
```
Pairs analyzed: 75
Scan duration: 1.2 seconds
Opportunities found: 1
Top opportunity: ASM-USD (score: 40/100, momentum_long)
```

**Performance:**
- ✅ Completes in < 30 seconds requirement (actual: ~1.2s)
- ✅ Scans 50-100 liquid pairs (actual: 75)
- ✅ Calculates all required indicators
- ✅ Outputs ranked JSON file
- ✅ Cron-ready (tested with direct execution)

## Output Example

```json
[
  {
    "symbol": "ASM-USD",
    "base_currency": "ASM",
    "price": 0.00789,
    "volume_24h": 6297485.0,
    "score": 40,
    "setup": "momentum_long",
    "signals": [
      "Momentum zone (RSI 55-65, positive MACD)",
      "MACD strong bullish crossover",
      "⚠️ Low volume warning"
    ],
    "indicators": {
      "rsi": 64.79,
      "macd": 0.000045,
      "macd_signal": 0.000012,
      "macd_histogram": 0.000033,
      "bb_upper": 0.01,
      "bb_middle": 0.01,
      "bb_lower": 0.01,
      "bb_percent": 78.05,
      "volume_ratio": 0.14,
      "volatility": 1.02
    },
    "trend": "sideways",
    "timestamp": "2026-02-04T02:53:45+00:00"
  }
]
```

## Strategies Implemented

### 1. Mean Reversion
**Criteria:**
- RSI < 30 (oversold) or > 70 (overbought)
- Bollinger Band extremes (< 20% or > 80%)
- Score: 35-50 points

**Logic:** Price at extremes tends to revert to the mean

### 2. Momentum (Discovered Pattern)
**Criteria:**
- RSI 55-65 (healthy momentum zone)
- Positive MACD histogram
- Score: 30 points base

**Logic:** Continuation pattern identified in previous analysis

### 3. Enhanced Signals
- MACD crossovers: +12-20 points
- High volume confirmation: +12-20 points
- Trend alignment: +15 points
- Bollinger Band extremes: +10 points
- High volatility: +5-10 points

## Quick Start

### Run Scanner
```bash
cd ~/.openclaw/workspace
python3 scripts/scan_opportunities.py
```

### View Results
```bash
cat market_opportunities.json | jq '.'
```

### Install Cron Job
```bash
# Edit crontab
crontab -e

# Add this line (runs 3x daily at 9am, 3pm, 9pm):
0 9,15,21 * * * cd /home/bonsaihorn/.openclaw/workspace && /usr/bin/python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1

# Save and exit, then verify:
crontab -l
```

### Monitor
```bash
# Watch log file
tail -f scan_opportunities.log

# Check cron execution
tail -f logs/scanner_cron.log
```

## Cron Recommendations

Based on CPU load and requirements:

### Conservative (Recommended)
**Schedule:** 3x daily (9am, 3pm, 9pm EST)
```
0 9,15,21 * * * cd ~/.openclaw/workspace && python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```
**CPU Impact:** ~6 seconds per day (3 runs × 2 seconds)

### Moderate
**Schedule:** Every hour during peak (8am-11pm)
```
0 8-23 * * * cd ~/.openclaw/workspace && python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```
**CPU Impact:** ~32 seconds per day (16 runs × 2 seconds)

### Aggressive
**Schedule:** Every 15 minutes
```
*/15 * * * * cd ~/.openclaw/workspace && python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```
**CPU Impact:** ~3 minutes per day (96 runs × 2 seconds)

## Integration with Existing Code

The scanner is designed to work standalone but can be integrated:

### Alert Manager Integration
```python
from alert_manager import AlertManager

# In scan_opportunities.py, after finding opportunities:
if opportunities and opportunities[0]['score'] >= 70:
    alert_mgr = AlertManager(signal_target="+1234567890")
    top = opportunities[0]
    alert_mgr.send_signal(
        f"🚨 High-score opportunity: {top['symbol']} "
        f"(score: {top['score']}, {top['setup']})"
    )
```

### Active Trader Integration
```python
# In active_trader.py or new auto_trader.py:
import json

with open('market_opportunities.json') as f:
    opportunities = json.load(f)

# Filter for high-confidence setups
for opp in opportunities:
    if opp['score'] >= 80 and opp['setup'] == 'mean_reversion_long':
        # Add to trading queue or execute directly
        schedule_trade(opp['symbol'], strategy='mean_reversion')
```

## Files Created

```
workspace/
├── scripts/
│   ├── scan_opportunities.py       # Main scanner (496 lines)
│   ├── market_indicators.py        # Indicator library (231 lines)
│   ├── SCANNER_README.md           # Full documentation (300+ lines)
│   └── scanner_cron.txt            # Cron configurations
├── market_opportunities.json       # Output file (top 10 opportunities)
├── scan_opportunities.log          # Execution log
└── SCANNER_SUMMARY.md              # This file
```

## Next Steps

1. **Test cron installation**
   ```bash
   crontab -e
   # Add recommended schedule
   # Wait for next run
   tail -f logs/scanner_cron.log
   ```

2. **Monitor results over time**
   - Track which setups are most accurate
   - Adjust scoring thresholds based on performance
   - Consider backtesting top opportunities

3. **Optional enhancements**
   - Alert notifications for high-score opportunities
   - Database storage for historical tracking
   - Auto-trading integration (with proper risk management)
   - Multi-timeframe analysis

## Success Criteria ✅

- [x] Get liquid pairs from Coinbase (top 75 by volume)
- [x] Calculate RSI, MACD, Bollinger Bands, Volume Profile
- [x] Apply Mean Reversion criteria
- [x] Apply discovered momentum pattern (RSI 55-65 + positive MACD)
- [x] Score each opportunity (0-100)
- [x] Output top 10 to JSON file with proper format
- [x] Batch API calls with async
- [x] Cache results for 5 minutes
- [x] Run in < 30 seconds (actual: ~1.2 seconds ✅)
- [x] Create cron-ready standalone script
- [x] No interactive prompts
- [x] Logs to file
- [x] Provide cron configuration recommendations

**All requirements met!** 🎉
