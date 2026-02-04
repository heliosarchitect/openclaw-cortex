# Active Trader - Quick Start Card

## First Time Setup (5 minutes)

```bash
cd ~/.openclaw/workspace

# 1. Generate configs for all 10 assets
python generate_asset_configs.py

# 2. Edit master config (REQUIRED)
nano config/active_trader_config.json
# → Set starting_capital: 2495.58
# → Set signal_notifications.target: "+18033169860"
# → Set assets to just 2-3 for first test: ["ETH-USD", "SOL-USD"]

# 3. Test single asset first
cd ~/Projects/Chad2930/Chad_Profit_Bot
python profit_aware_bot.py --config ~/.openclaw/workspace/config/active_eth_config.yaml
# Let run 5-10 min, verify it works, then Ctrl+C

# 4. Start active trader (with dashboard)
cd ~/.openclaw/workspace
./start_trading.sh --dashboard
```

## Daily Operation

### Morning (Before 9 AM)
```bash
# Start in tmux so it persists
tmux new -s trading
cd ~/.openclaw/workspace
./start_trading.sh --dashboard

# Detach: Ctrl+B, then D
# It will wait until 9 AM EST to start trading
```

### During Day
- Check Signal notifications on your phone
- Optional: `tmux attach -t trading` to view dashboard

### Evening (After 6 PM)
System auto-exits at 17:45 EST, sends final report.

```bash
# Analyze session
python analyze_trades.py --today

# Review logs
cat logs/session_report_$(date +%Y-%m-%d).txt
```

## Key Commands

```bash
# View live dashboard
python dashboard.py

# Analyze today's trades
python analyze_trades.py --today

# Check if running
ps aux | grep active_trader

# View logs
tail -f logs/active_trader.log
tail -f logs/trades/trades_$(date +%Y-%m-%d).jsonl

# Reattach tmux
tmux attach -t trading

# Stop gracefully (cancels buys, completes sells)
pkill -TERM -f active_trader.py

# Force stop (emergency only)
pkill -KILL -f active_trader.py
```

## Signal Notifications

You'll receive:
- 🚀 **09:00** - Startup (lists assets trading)
- ✅ **During day** - Profits ≥$5
- 📉 **During day** - Losses ≥$3
- 📊 **Every 30 min** - Status update
- 🚨 **17:45** - Exit notification
- 📈 **~18:00** - Session report

## Files Location

```
~/.openclaw/workspace/
├── active_trader.py          # Master controller
├── config/
│   ├── active_trader_config.json  # Edit this first
│   └── active_*_config.yaml       # Per-asset configs
├── logs/
│   ├── active_trader.log          # Master log
│   ├── trades/                     # Trade history (JSONL)
│   └── session_report_*.txt       # Daily summaries
└── start_trading.sh          # Startup script
```

## Configuration Quick Tweaks

### Add/Remove Assets
Edit `config/active_trader_config.json`:
```json
{
  "assets": ["ETH-USD", "SOL-USD", "XRP-USD"]
}
```

### Adjust Profit Targets (per asset)
Edit `config/active_eth_config.yaml` (for example):
```yaml
base_profit_target_bps: 10    # 0.10% profit target
min_profit_ticks: 3           # Minimum $0.03 profit
```

### Adjust Order Timeout
Edit any asset config:
```yaml
min_order_age_seconds: 30     # Cancel unfilled orders after 30s
```

### Adjust Signal Thresholds
Edit `config/active_trader_config.json`:
```json
{
  "signal_notifications": {
    "notify_on_profit_threshold": 5.0,   # Alert on $5+ profit
    "notify_on_loss_threshold": 3.0      # Alert on $3+ loss
  }
}
```

## Trading Schedule (EST)

| Time | Event |
|------|-------|
| 09:00 | Trading starts |
| 09:00-17:45 | Active scalping (30s order timeout) |
| 17:45 | Exit all positions |
| ~18:00 | Session report sent |

## Safety Limits

- **30s timeout**: Unfilled orders auto-cancel
- **Max position**: 20-40% per asset (varies by asset)
- **Max loss**: 0.15% per position
- **Reserve**: 10% capital held back
- **Max restarts**: 5 per asset per session

## Troubleshooting

**Bot won't start?**
```bash
cat logs/active_trader.log  # Check for errors
ls -l ~/Projects/Chad2930/Chad_Profit_Bot/profit_aware_bot.py  # Verify path
```

**No trades?**
```bash
ps aux | grep profit_aware_bot  # Check bots running
tail -f logs/active_trader.log  # Watch for activity
```

**Dashboard empty?**
```bash
ls logs/trades/  # Check logs exist
cat logs/trades/trades_$(date +%Y-%m-%d).jsonl  # View raw trades
```

## Performance Analysis

After each session:
```bash
# Run analysis
python analyze_trades.py --today

# Review:
# 1. Which assets made money?
# 2. Which hours were profitable?
# 3. What's the win rate?
# 4. Follow the recommendations
```

## Scaling Up

**Week 1**: 2-3 assets, watch closely
**Week 2**: Add profitable hours, tune configs
**Week 3**: Add more assets (4-6 total)
**Week 4**: Full 10 assets if performing well

Start conservative, scale based on results.

## Important Notes

- This is **learning capital** - expect losses while tuning
- **30-second timeout** is aggressive - may need adjustment
- **17:45 exit** protects from 18:30 market dumps
- **VIP2 fees**: 0.050% maker / 0.100% taker
- Target **0.1% scalps** = tight margins, high volume needed

## Documentation

- **README_ACTIVE_TRADER.md** - Full features
- **DEPLOYMENT_GUIDE.md** - Step-by-step deployment  
- **SUMMARY.md** - System overview
- **QUICK_START.md** - This card

---

**Ready to trade? Run: `./start_trading.sh --dashboard`** 🎯
