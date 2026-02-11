# Active Trader Deployment Guide

Step-by-step guide to deploy the multi-asset trading monitor.

## Prerequisites

1. **Working profit_aware_bot.py**
   - Located at: `~/Projects/Chad2930/Chad_Profit_Bot/profit_aware_bot.py`
   - Tested and working for at least one asset
   - Coinbase API keys configured in `.env`

2. **Python Dependencies**
   ```bash
   pip install pyyaml pytz
   ```

3. **Sufficient Capital**
   - Minimum: $500 (spread thin across 10 assets)
   - Recommended: $2,000+ (allows meaningful position sizes)
   - Your capital: $2,495.58 ✅

## Step 1: Generate Configs

```bash
cd ~/.openclaw/workspace
python generate_asset_configs.py
```

This creates 10 config files in `config/` directory:
- `active_eth_config.yaml`
- `active_sol_config.yaml`
- `active_doge_config.yaml`
- ... etc

**Review and adjust** if needed. Each asset has parameters tuned for its characteristics.

## Step 2: Configure Master Settings

Edit `config/active_trader_config.json`:

```json
{
  "bot_directory": "/home/bonsaihorn/Projects/Chad2930/Chad_Profit_Bot",
  "starting_capital": 2495.58,
  
  "assets": [
    "ETH-USD",
    "SOL-USD",
    "DOGE-USD"
    // Start with just 2-3 assets for testing
  ],
  
  "signal_notifications": {
    "target": "+18033169860",
    "notify_on_profit_threshold": 5.0,
    "notify_on_loss_threshold": 3.0
  }
}
```

**Important**: Start with 2-3 assets first, then expand.

## Step 3: Test Single Asset First

Before running multi-asset, verify each bot works individually:

```bash
cd ~/Projects/Chad2930/Chad_Profit_Bot
python profit_aware_bot.py --config ~/.openclaw/workspace/config/active_eth_config.yaml
```

Let it run for 5-10 minutes. Verify:
- ✅ Connects to Coinbase
- ✅ Places orders
- ✅ Handles fills
- ✅ Logs trades
- ✅ Cancels stale orders (30s timeout)

Press Ctrl+C to stop gracefully.

## Step 4: Test Active Trader (Dry Run)

Start with just ETH to validate the wrapper:

```bash
cd ~/.openclaw/workspace

# Edit config to only include ETH
# Then start:
python active_trader.py
```

Watch for:
- ✅ Bot starts successfully
- ✅ Output is captured and parsed
- ✅ Trade logging works
- ✅ Signal notifications appear (in console for now)
- ✅ Graceful shutdown on Ctrl+C

## Step 5: Run with Dashboard

```bash
chmod +x start_trading.sh
./start_trading.sh --dashboard
```

You'll see a real-time dashboard showing:
- Current P&L
- Per-asset breakdown
- Trade counts
- Last trade times

## Step 6: Deploy for Real Trading

### Option A: Tmux Session (Recommended)

```bash
# Start tmux session
tmux new -s trading

# In tmux:
cd ~/.openclaw/workspace
./start_trading.sh --dashboard

# Detach: Ctrl+B, then D
# Reattach later: tmux attach -t trading
```

### Option B: Background Service

```bash
# Start in background
cd ~/.openclaw/workspace
python active_trader.py > logs/active_trader.log 2>&1 &
echo $! > logs/trader.pid

# Check status
tail -f logs/active_trader.log

# Stop
kill $(cat logs/trader.pid)
```

### Option C: Systemd Service (Advanced)

Create `/etc/systemd/system/active-trader.service`:

```ini
[Unit]
Description=Active Trading Monitor
After=network.target

[Service]
Type=simple
User=bonsaihorn
WorkingDirectory=/home/bonsaihorn/.openclaw/workspace
ExecStart=/usr/bin/python3 active_trader.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable active-trader
sudo systemctl start active-trader
sudo systemctl status active-trader
```

## Step 7: Monitor Throughout Day

### Check Dashboard

```bash
cd ~/.openclaw/workspace
python dashboard.py
```

### Check Logs

```bash
# Master log
tail -f logs/active_trader.log

# Today's trades
tail -f logs/trades/trades_$(date +%Y-%m-%d).jsonl

# Formatted trades
tail -f logs/trades/trades_$(date +%Y-%m-%d).jsonl | jq '.'
```

### Check Signal Notifications

You should receive:
- 🚀 Startup notification (9:00 AM EST)
- ✅ Profit alerts (>$5)
- 📉 Loss alerts (>$3)
- 📊 Status updates (every 30 min)
- 🚨 Exit notification (5:45 PM EST)
- 📈 Session report (end of day)

## Trading Schedule

The system runs on EST timezone:

| Time | Event |
|------|-------|
| 09:00 | Start trading (or wait if started earlier) |
| 09:00-17:45 | Active trading hours |
| 17:45 | Begin position exit |
| 18:00 | All bots stopped, positions closed |
| 18:30 | Market typically dumps (we're out by now) |

## Capital Allocation

With $2,495.58 starting capital:
- **Reserve**: $249.56 (10%)
- **Trading**: $2,246.02 (90%)

Split across assets (example with 5 assets):
- ETH: ~$600 (high priority)
- SOL: ~$500 (high priority)
- XRP: ~$400 (medium)
- ADA: ~$400 (medium)
- DOGE: ~$346 (medium)

**Performance-based rebalancing** happens every 30 minutes:
- Winners get 1.3x allocation
- 2+ consecutive losses: 0.5x allocation
- 3+ consecutive losses: Asset paused

## Safety Limits

The system has multiple safety nets:

1. **30-Second Timeout**: Unfilled orders cancelled
2. **Position Limits**: Max 40% per asset (usually 20-25%)
3. **Loss Limits**: 0.15% max loss per position
4. **Total Loss Pause**: Stop all trading if down 5%
5. **Max Restarts**: 5 per asset per session
6. **Reserved Capital**: 10% always held back
7. **Time-Based Exit**: Dump everything by 17:45 EST

## Troubleshooting

### Bot won't start
```bash
# Check logs
cat logs/active_trader.log

# Verify bot path
ls ~/Projects/Chad2930/Chad_Profit_Bot/profit_aware_bot.py

# Check config
cat config/active_trader_config.json
```

### No trades happening
```bash
# Check if bots are running
ps aux | grep profit_aware_bot

# Check individual bot output
tail -f ~/Projects/Chad2930/Chad_Profit_Bot/logs/*.log

# Check market data connection
# Should see ticker updates in bot logs
```

### Signal notifications not working
```bash
# Test OpenClaw Signal integration manually
# (This needs to be set up separately)

# For now, notifications print to console/logs
```

### Dashboard shows no data
```bash
# Check if trades log exists
ls -l logs/trades/

# Verify log format
cat logs/trades/trades_$(date +%Y-%m-%d).jsonl

# Make sure active_trader is running
ps aux | grep active_trader
```

## Performance Tuning

After a few days of trading, review:

1. **Asset Performance**
   - Which assets are most profitable?
   - Adjust `"assets"` list to focus on winners

2. **Profit Targets**
   - Too tight? Increase `base_profit_target_bps`
   - Too wide? Decrease for faster turnover

3. **Order Timeout**
   - 30s too aggressive? Increase `min_order_age_seconds`
   - Not aggressive enough? Decrease (min 15s)

4. **Capital Allocation**
   - Modify `allocate_capital()` logic
   - Consider time-of-day weighting

5. **Position Sizing**
   - Adjust `min_order_size` / `max_order_size` per asset
   - Tune `max_position_percent`

## Daily Checklist

**Before Market Open (9 AM EST)**:
- [ ] Check system is running (`ps aux | grep active_trader`)
- [ ] Review yesterday's session report
- [ ] Verify API keys are valid
- [ ] Check Coinbase account balance matches expectation
- [ ] Ensure logs directory has space

**During Trading Day**:
- [ ] Check Signal notifications periodically
- [ ] Monitor dashboard if available
- [ ] Watch for unusual restart patterns
- [ ] Verify trades are executing (check logs)

**After Market Close (6 PM EST)**:
- [ ] Review session report in Signal
- [ ] Check `logs/session_report_YYYY-MM-DD.txt`
- [ ] Analyze `logs/trades/trades_YYYY-MM-DD.jsonl`
- [ ] Note which assets performed best
- [ ] Adjust configs for next session

## Learning & Analysis

Use the trade logs to learn:

```bash
# Most profitable asset today
cat logs/trades/trades_$(date +%Y-%m-%d).jsonl | \
  jq -s 'group_by(.asset) | map({asset: .[0].asset, profit: (map(.profit) | add)}) | sort_by(.profit) | reverse'

# Total trades per asset
cat logs/trades/trades_$(date +%Y-%m-%d).jsonl | \
  jq -s 'group_by(.asset) | map({asset: .[0].asset, count: length})'

# Hourly P&L distribution
cat logs/trades/trades_$(date +%Y-%m-%d).jsonl | \
  jq -r '[.timestamp[:13], .profit] | @tsv'
```

## Next Steps

1. **Start Small**: 2-3 assets, $500-1000 allocated
2. **Monitor Closely**: First few days, watch constantly
3. **Learn Patterns**: Which hours are profitable?
4. **Scale Up**: Add assets, increase capital allocation
5. **Optimize**: Tune configs based on observed behavior
6. **Automate**: Set up systemd service for hands-off operation

## Emergency Stop

If something goes wrong:

```bash
# Graceful stop (cancels buys, lets sells complete)
pkill -TERM -f active_trader.py

# Force stop (immediate)
pkill -KILL -f active_trader.py
pkill -KILL -f profit_aware_bot.py

# Cancel ALL orders on Coinbase
# (Use Coinbase web UI or API)
```

---

**Remember**: This is learning capital. Start conservative, scale cautiously. The goal is to learn what works, not to get rich quick. 🎯
