# Active Trading Monitor - Complete System

## What You Now Have

A comprehensive multi-asset trading system that wraps `profit_aware_bot.py` with intelligent monitoring, management, and reporting.

## Files Created

### Core System
- **`active_trader.py`** - Master controller that manages bot instances
- **`alert_manager.py`** - Smart Signal notification system
- **`dashboard.py`** - Real-time terminal dashboard
- **`analyze_trades.py`** - Post-session analysis tool

### Configuration
- **`generate_asset_configs.py`** - Creates optimized configs for each asset
- **`config/active_trader_config.json`** - Master configuration
- **`config/active_*_config.yaml`** - Per-asset bot configs (generated)

### Utilities
- **`start_trading.sh`** - Startup script with dashboard support
- **`README_ACTIVE_TRADER.md`** - Complete feature documentation
- **`DEPLOYMENT_GUIDE.md`** - Step-by-step deployment instructions
- **`SUMMARY.md`** - This file

## Quick Start

```bash
# 1. Generate configs
python generate_asset_configs.py

# 2. Edit master config (set Signal number, starting capital)
nano config/active_trader_config.json

# 3. Test with 1-2 assets first
#    Edit config/active_trader_config.json, set assets to ["ETH-USD", "SOL-USD"]

# 4. Start trading
./start_trading.sh --dashboard
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     active_trader.py                        │
│                   (Master Controller)                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Bot: ETH-USD │  │ Bot: SOL-USD │  │ Bot: DOGE-USD│    │
│  │  PID: 1234   │  │  PID: 1235   │  │  PID: 1236   │ ...│
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │          AlertManager (Signal Notifier)          │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Logs & Analysis                          │
│  • logs/active_trader.log         (master log)             │
│  • logs/trades/trades_*.jsonl     (trade history)          │
│  • logs/session_report_*.txt      (daily summary)          │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Multi-Asset Portfolio Management
- Simultaneously trade up to 10 crypto assets
- Dynamic capital allocation based on performance
- Automatic rebalancing every 30 minutes

### 2. Intelligent Monitoring
- Parse bot output for trade completions
- Track P&L per asset and overall
- Auto-restart crashed bots (up to 5 times)
- Health checks every 60 seconds

### 3. Time-Based Control
- Start: 09:00 EST (waits if started earlier)
- Active trading: 09:00-17:45 EST
- Auto-exit: 17:45 EST (before 18:30 market dump)
- Graceful shutdown: Cancel buys, complete sells

### 4. Smart Alerting (Signal)
- Profit threshold: $5.00+ (configurable)
- Loss threshold: $3.00+ (configurable)
- Status updates: Every 30 minutes
- Startup/shutdown notifications
- Bot restart alerts (if significant)
- Prevents notification spam with smart throttling

### 5. Comprehensive Logging
- JSONL format for easy analysis
- Per-trade records with timestamps
- Asset performance tracking
- Session reports at end of day

### 6. Real-Time Dashboard
- Terminal UI shows live P&L
- Per-asset breakdown
- Trade counts
- Last trade times
- Auto-refresh every 5 seconds

### 7. Post-Session Analysis
- Win rate by asset
- Hourly P&L patterns
- Best/worst performers
- Actionable recommendations

## Configuration Highlights

### Per-Asset Optimization

Each asset has tuned parameters:

- **ETH**: Fast rebalance (15s), 40% max position, 10 bps target
- **SOL**: Medium speed (20s), 30% position, 12 bps (volatile)
- **DOGE**: Slower (25s), 20% position, 15 bps (meme coin)
- **XRP/ADA/LINK**: Moderate settings, 25% position
- **DOT/AVAX/ATOM/NEAR**: Conservative, 20% position

### Risk Management

Built-in safety limits:
- 30-second order timeout (keep money moving)
- Max 0.15% loss per position
- Total loss pause at 5%
- Reserved capital: 10%
- Max restarts: 5 per asset per session

### Capital Allocation

Dynamic allocation:
- Winners (>70% win rate): 1.3x allocation
- Struggling (2+ losses): 0.5x allocation  
- Failed (3+ losses): Paused

## Signal Notification Flow

```
Trade Completed
     ↓
Check threshold ($5 profit or $3 loss)
     ↓
Check cooldown (5 min per asset)
     ↓
[Below threshold] → Accumulate for next status update
[Above threshold] → Send immediate alert
     ↓
Every 30 min: Status update with accumulated small trades
```

## Trading Schedule (EST)

| Time | Event | Action |
|------|-------|--------|
| 09:00 | Market open | Start bots, send startup notification |
| 09:00-17:45 | Active trading | Continuous scalping, 30s order timeout |
| 17:45 | Pre-exit | Stop placing new buys |
| 17:45-18:00 | Exit phase | Cancel all buys, let sells complete |
| 18:00 | Session end | Generate report, send to Signal |
| 18:30 | Market dump | We're already out ✅ |

## Example Workflow

### Morning (Before 9 AM)
```bash
# Start in tmux for persistence
tmux new -s trading
cd ~/.openclaw/workspace
./start_trading.sh --dashboard

# Detach: Ctrl+B, D
```

**You receive**: 🚀 Startup notification on Signal

### During Day (9 AM - 6 PM)
System runs autonomously. You receive:
- ✅ Profit alerts (>$5)
- 📉 Loss alerts (>$3)  
- 📊 Status updates every 30 min
- 🔄 Restart notifications (if needed)

### Evening (After 6 PM)
**You receive**: 📊 Session report with:
- Final P&L
- Top 3 performers
- Worst performer
- Total trades

### Later
```bash
# Analyze what happened
python analyze_trades.py --today

# Review recommendations
# Adjust configs for tomorrow
```

## Monitoring Commands

```bash
# View dashboard
python dashboard.py

# Tail master log
tail -f logs/active_trader.log

# Watch trades live
tail -f logs/trades/trades_$(date +%Y-%m-%d).jsonl | jq '.'

# Check bot processes
ps aux | grep profit_aware_bot

# Reattach to tmux
tmux attach -t trading
```

## Safety Features

1. **30-Second Timeout**: Unfilled orders auto-cancel
2. **Position Limits**: Never exceed configured max per asset
3. **Loss Limits**: Stop-loss on individual positions
4. **Time-Based Exit**: Forced exit by 17:45 EST
5. **Reserved Capital**: Always keep 10% in reserve
6. **Max Restarts**: Prevent runaway restart loops
7. **Graceful Shutdown**: Ctrl+C cancels buys, completes sells

## What to Tune After First Session

Based on your results, adjust:

1. **Asset Selection**: Remove losers, focus on winners
2. **Profit Targets**: Too tight → increase `base_profit_target_bps`
3. **Order Timeout**: Too aggressive? → increase `min_order_age_seconds`
4. **Position Sizing**: Winning asset? → increase `max_position_percent`
5. **Capital Allocation**: Rebalance more/less frequently?

## Learning Objectives

This is **learning capital**. Focus on:

1. ✅ Which assets are profitable during your trading hours?
2. ✅ What times of day are most profitable?
3. ✅ Is 30-second timeout optimal?
4. ✅ How does 0.1% scalping perform across assets?
5. ✅ Which volatility profiles work best?
6. ✅ Is dynamic allocation effective?
7. ✅ Does early exit (17:45) save money?

## Success Metrics

After 1 week of trading:
- [ ] Overall positive P&L
- [ ] Identified 2-3 consistently profitable assets
- [ ] Understood optimal trading hours
- [ ] Refined config parameters
- [ ] No catastrophic losses (safety systems work)
- [ ] System runs reliably without intervention

## Next Steps

1. **Deploy**: Follow `DEPLOYMENT_GUIDE.md` step-by-step
2. **Start Small**: 2-3 assets, $500-1000 allocated first
3. **Monitor**: Watch closely for first few sessions
4. **Analyze**: Use `analyze_trades.py` daily
5. **Tune**: Adjust configs based on observations
6. **Scale**: Add assets and capital gradually
7. **Automate**: Set up systemd service for hands-off operation

## Emergency Procedures

**Graceful Stop**:
```bash
pkill -TERM -f active_trader.py
# Waits for sells to complete
```

**Force Stop**:
```bash
pkill -KILL -f active_trader.py
pkill -KILL -f profit_aware_bot.py
# Immediate termination
```

**Cancel All Orders** (Coinbase):
```bash
# Use Coinbase web UI or API
# Emergency only
```

## Support Files

- **README_ACTIVE_TRADER.md**: Complete feature documentation
- **DEPLOYMENT_GUIDE.md**: Step-by-step deployment
- **SUMMARY.md**: This overview (you are here)

## Questions?

Review the documentation:
1. `README_ACTIVE_TRADER.md` for features
2. `DEPLOYMENT_GUIDE.md` for deployment
3. `analyze_trades.py --help` for analysis options

Check logs:
- `logs/active_trader.log` - Master controller
- `logs/trades/` - Trade history
- `logs/session_report_*.txt` - Daily summaries

---

**You're ready to trade. Start conservative, learn constantly, scale wisely.** 🎯

Good luck, Matthew! 🚀
