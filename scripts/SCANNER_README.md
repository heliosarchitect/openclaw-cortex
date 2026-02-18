# Multi-Asset Opportunity Scanner
<!-- AI.TOC: Multi-Asset Opportunity Scanner — Read lines 1-20 for navigation.
  §1 Overview                                   → lines 3-5
  §2 Features                                   → lines 6-16
  §3 Files                                      → lines 17-22
  §4 Usage                                      → lines 23-51
  §5 Output Format                              → lines 52-84
  §6 Scoring System                             → lines 85-105
  §7 Cron Configuration                         → lines 106-168
  §8 Configuration                              → lines 169-186
  §9 Troubleshooting                            → lines 187-203
  §10 Integration Examples                       → lines 204-245
  §11 Performance Metrics                        → lines 246-253
  §12 Future Enhancements                        → lines 254-263
  §13 License                                    → lines 264-266
  Total: 266 lines | Sections: 13
-->

## Overview
Scans all liquid Coinbase USD pairs for trading opportunities using technical analysis.

## Features
- **Scans 50-100 top pairs by volume** (configurable)
- **Technical indicators**: RSI, MACD, Bollinger Bands, Volume Profile
- **Multiple strategies**:
  - Mean Reversion (oversold/overbought extremes)
  - Momentum (RSI 55-65 + positive MACD)
  - Trend-aligned setups
- **Intelligent scoring**: 0-100 points based on signal strength
- **Fast execution**: <30 seconds for full scan
- **Efficient caching**: 5-minute cache for API data

## Files
- `scan_opportunities.py` - Main scanner script
- `market_indicators.py` - Technical indicator calculations
- `../market_opportunities.json` - Output file with top 10 opportunities
- `../scan_opportunities.log` - Execution log

## Usage

### Manual Run
```bash
cd ~/.openclaw/workspace
python3 scripts/scan_opportunities.py
```

### View Results
```bash
cat market_opportunities.json | jq '.'
```

### Programmatic Access
```python
import json
from pathlib import Path

# Load opportunities
opportunities_path = Path.home() / '.openclaw' / 'workspace' / 'market_opportunities.json'
with open(opportunities_path) as f:
    opportunities = json.load(f)

# Get top opportunity
if opportunities:
    top = opportunities[0]
    print(f"{top['symbol']}: Score {top['score']}, Setup: {top['setup']}")
```

## Output Format
```json
[
  {
    "symbol": "BTC-USD",
    "base_currency": "BTC",
    "price": 45123.50,
    "volume_24h": 1234567890.12,
    "score": 85,
    "setup": "mean_reversion_long",
    "signals": [
      "⭐ STRONG OVERSOLD (RSI < 30, BB extreme low)",
      "MACD bullish crossover",
      "High volume (2.1x avg)"
    ],
    "indicators": {
      "rsi": 28.5,
      "macd": -12.34,
      "macd_signal": -15.67,
      "macd_histogram": 3.33,
      "bb_upper": 46000.0,
      "bb_middle": 44500.0,
      "bb_lower": 43000.0,
      "bb_percent": 15.2,
      "volume_ratio": 2.1,
      "volatility": 4.5
    },
    "trend": "downtrend",
    "timestamp": "2026-02-03T20:30:00+00:00"
  }
]
```

## Scoring System

### Primary Setups
- **Strong Mean Reversion** (RSI < 30 + BB < 20%): **+50 points**
- **Moderate Mean Reversion** (RSI < 35 + BB < 30%): **+35 points**
- **Momentum** (RSI 55-65 + positive MACD): **+30 points**

### Additional Signals
- **Strong MACD crossover**: **+20 points**
- **Very high volume** (>2x avg): **+20 points**
- **Trend alignment**: **+15 points**
- **Bollinger Band extremes**: **+10 points**
- **High volatility** (>5%): **+10 points**

### Penalties
- **Low volume** (<0.5x avg): **-10 points**
- **Counter-trend momentum**: **-10 points**
- **Very low volatility**: **-5 points**

**Minimum threshold**: 30 points (opportunities below this are filtered out)

## Cron Configuration

### Recommended Schedule

#### Development/Testing (frequent scans)
```bash
# Every 15 minutes during trading hours (9am-5pm EST)
*/15 9-17 * * 1-5 cd /home/bonsaihorn/.openclaw/workspace && /usr/bin/python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```

#### Production (conservative, CPU-friendly)
```bash
# Every hour during active trading (crypto is 24/7, but focus on high-volume periods)
0 8-23 * * * cd /home/bonsaihorn/.openclaw/workspace && /usr/bin/python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1

# Or just 3 times per day at key times
0 9,15,21 * * * cd /home/bonsaihorn/.openclaw/workspace && /usr/bin/python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```

#### Aggressive (every 5 minutes, high frequency)
```bash
# Only recommended if you have CPU headroom and want near-real-time alerts
*/5 * * * * cd /home/bonsaihorn/.openclaw/workspace && /usr/bin/python3 scripts/scan_opportunities.py >> logs/scanner_cron.log 2>&1
```

### CPU Load Considerations

**Scanner resource usage:**
- **Duration**: 1-3 seconds typical
- **CPU**: Minimal (mostly I/O-bound, async HTTP calls)
- **Memory**: ~50-100 MB
- **Network**: ~100-200 KB per scan

**Recommendation based on system load:**
- **Idle system**: Every 5-10 minutes
- **Light usage**: Every 15-30 minutes
- **Heavy usage**: Every 1-2 hours
- **Production trading bot running**: Every 30-60 minutes

### Monitor CPU Temperature
```bash
# Check before deciding on frequency
./scripts/check_cpu_temp.py
```

If CPU temp > 75°C sustained, reduce scan frequency.

### Install Cron Job
```bash
# Edit crontab
crontab -e

# Add one of the schedules above, then save

# Verify
crontab -l
```

### View Cron Logs
```bash
tail -f /home/bonsaihorn/.openclaw/workspace/logs/scanner_cron.log
```

## Configuration

Edit `scan_opportunities.py` to customize:

```python
# Line 37: Number of top pairs to analyze
top_n_pairs = 75  # Default: 75 (increase for more coverage, decrease for speed)

# Line 25: Cache duration
CACHE_DURATION = 300  # 5 minutes (decrease for fresher data, increase for less API load)

# Line 234: Minimum score threshold
if score >= 30:  # Default: 30 (increase for stricter filtering)

# Line 404: Candle granularity
granularity = 3600  # 1 hour (can use 900=15min, 300=5min for more sensitive)
```

## Troubleshooting

### No opportunities found
- **Market is neutral**: Normal! Opportunities come and go.
- **Threshold too high**: Lower the `score >= 30` threshold in line 234
- **Insufficient data**: Some pairs may lack candle history

### Slow execution
- **Too many pairs**: Reduce `top_n_pairs` from 75 to 50
- **Network latency**: Check internet connection
- **API rate limits**: Increase `CACHE_DURATION`

### Missing dependencies
```bash
pip3 install --user --break-system-packages aiohttp attrs numpy
```

## Integration Examples

### Alert on High-Score Opportunities
```bash
#!/bin/bash
# scripts/alert_on_opportunities.sh

cd ~/.openclaw/workspace
python3 scripts/scan_opportunities.py > /dev/null 2>&1

# Check top opportunity score
SCORE=$(jq '.[0].score // 0' market_opportunities.json)

if [ "$SCORE" -ge 70 ]; then
    SYMBOL=$(jq -r '.[0].symbol' market_opportunities.json)
    SETUP=$(jq -r '.[0].setup' market_opportunities.json)
    
    # Send Signal notification
    openclaw message send --target="+1234567890" --message="🚨 High-score opportunity: $SYMBOL (score: $SCORE, $SETUP)"
fi
```

### Auto-Trade on Signals (DANGEROUS - test first!)
```python
# scripts/auto_trade_opportunities.py
import json
from pathlib import Path

opportunities_path = Path.home() / '.openclaw' / 'workspace' / 'market_opportunities.json'

with open(opportunities_path) as f:
    opportunities = json.load(f)

# Only trade high-confidence setups
for opp in opportunities:
    if opp['score'] >= 80 and opp['setup'] == 'mean_reversion_long':
        symbol = opp['symbol']
        # IMPLEMENT YOUR TRADING LOGIC HERE
        # place_order(symbol, side='buy', size=calculate_size(opp))
        print(f"Would trade {symbol} (score {opp['score']})")
```

## Performance Metrics

Typical execution (75 pairs):
- **API calls**: ~150 (products, stats, candles)
- **Cache hits**: 80%+ on repeated runs
- **Total time**: 1.2-2.5 seconds
- **Bandwidth**: ~200 KB per run

## Future Enhancements

- [ ] Database storage for historical tracking
- [ ] Pattern recognition (double bottom, head & shoulders)
- [ ] ML-based scoring refinement
- [ ] Multi-timeframe analysis
- [ ] Backtesting integration
- [ ] Real-time WebSocket streaming
- [ ] Discord/Telegram bot integration

## License
Part of the OpenClaw trading workspace.
