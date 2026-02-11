# Active Trading Monitor

Multi-asset trading bot wrapper for profit_aware_bot.py

## Overview

The Active Trader monitors and manages multiple instances of profit_aware_bot.py across different crypto assets, handling failures, time-based exits, and providing live updates via Signal.

## Features

- ✅ **Multi-Asset Management**: Simultaneously trade ETH, SOL, DOGE, ADA, LINK, XRP, DOT, AVAX, ATOM, NEAR
- ✅ **Auto-Restart**: Automatically restart failed bots with exponential backoff
- ✅ **Time-Based Exit**: Dump all positions by 17:45 EST (before 18:30 market dump)
- ✅ **30-Second Rule**: Bots cancel unfilled orders after 30 seconds
- ✅ **Signal Notifications**: Real-time P&L updates sent to your phone
- ✅ **Capital Allocation**: Dynamic allocation based on performance
- ✅ **Comprehensive Logging**: All trades logged to JSONL for analysis
- ✅ **Graceful Shutdown**: Cancel buy orders, let sells complete

## Quick Start

### 1. Generate Asset Configs

```bash
cd ~/.openclaw/workspace
python generate_asset_configs.py
```

This creates optimized configs for all 10 assets in `config/` directory.

### 2. Review Configuration

Edit `config/active_trader_config.json`:

```json
{
  "starting_capital": 2495.58,
  "signal_notifications": {
    "target": "+18033169860",
    "notify_on_profit_threshold": 5.0,
    "notify_on_loss_threshold": 3.0
  }
}
```

### 3. Run Active Trader

```bash
python active_trader.py
```

## Architecture

```
active_trader.py (master controller)
├── Bot Process: ETH-USD (PID 1234)
├── Bot Process: SOL-USD (PID 1235)
├── Bot Process: DOGE-USD (PID 1236)
└── ... (up to 10 assets)
```

Each bot process:
- Runs independently with its own config
- Reports trades via stdout (parsed by master)
- Restarts automatically on failure
- Stops gracefully on shutdown signal

## Capital Allocation Strategy

**Initial**: Equal distribution across active assets

**Performance-Based Adjustment**:
- Win rate > 70%: 1.3x allocation
- Consecutive losses ≥ 2: 0.5x allocation
- Consecutive losses ≥ 3: Pause asset

**Reserve**: 10% held back for safety

## Trading Schedule

- **Start**: 09:00 EST (waits if started earlier)
- **Active Trading**: 09:00 - 17:45 EST
- **Exit All Positions**: 17:45 EST
- **Stop**: After all sell orders complete (~18:00 EST)

## Signal Notifications

Notifications sent when:
- ✅ Profit ≥ $5.00
- 📉 Loss ≥ $3.00
- 📊 Status update every 30 minutes
- 🚨 Emergency exit triggered
- 📈 Session report at end of day

## Logs

All logs stored in `logs/` directory:

```
logs/
├── active_trader.log          # Master controller log
├── trades/
│   └── trades_2026-02-02.jsonl  # Daily trade log (JSONL)
└── session_report_2026-02-02.txt  # End-of-day summary
```

### Trade Log Format (JSONL)

```json
{"timestamp": "2026-02-02T14:23:45-05:00", "asset": "ETH-USD", "profit": 2.34, "total_capital": 2497.92, "asset_total": 12.45}
{"timestamp": "2026-02-02T14:25:12-05:00", "asset": "SOL-USD", "profit": -1.12, "total_capital": 2496.80, "asset_total": 3.22}
```

## Asset Configuration

Each asset has optimized parameters based on:
- **Volatility**: Wider targets for volatile assets (DOGE, SOL)
- **Liquidity**: Faster rebalance for liquid markets (ETH)
- **Tick Size**: Appropriate profit targets per tick size

### Example: ETH Config

```yaml
symbol: ETH-USD
crypto_symbol: ETH
tick_size: 0.01
min_profit_ticks: 3           # $0.03 min profit
base_profit_target_bps: 10    # 0.10% target
max_position_percent: 40      # Allow 40% position size
rebalance_check_interval_seconds: 15  # Fast market
```

### Example: DOGE Config

```yaml
symbol: DOGE-USD
crypto_symbol: DOGE
tick_size: 0.00001
min_profit_ticks: 5
base_profit_target_bps: 15    # Wider target for volatility
max_position_percent: 20      # Smaller position for risk
rebalance_check_interval_seconds: 25  # Slower checks
```

## Risk Management

1. **30-Second Timeout**: Orders cancelled if not filled
2. **Position Limits**: Max 40% per asset (usually 20-25%)
3. **Loss Limits**: 0.15% max loss per position
4. **Total Loss Pause**: Pause all trading if down 5%
5. **Max Restarts**: 5 per session per asset
6. **Reserved Capital**: 10% always held back

## Performance Optimization

### High-Priority Assets (Most Capital)
- **ETH**: Most liquid, stable, fast rebalance
- **SOL**: High volume, good for scalping

### Medium-Priority Assets
- **XRP, ADA, LINK**: Moderate volatility and volume
- **DOGE**: High volatility but unpredictable

### Low-Priority Assets (Fill remainder)
- **DOT, AVAX, ATOM, NEAR**: Less liquid, wider spreads

## Troubleshooting

### Bot keeps restarting for an asset
- Check `logs/active_trader.log` for errors
- Review asset-specific config in `config/`
- May need to adjust `min_order_size` or `tick_size`

### No Signal notifications
- Verify `signal_target` in `config/active_trader_config.json`
- Check OpenClaw Signal integration is working
- Test with: `message.send(target="+1234567890", text="test")`

### Positions not exiting at 17:45
- Check system time is synced with EST
- Verify `exit_all_time` in config
- Bot may need restart if timezone is wrong

### Capital allocation seems off
- Review `allocate_capital()` method in `active_trader.py`
- Check `max_position_percent` per asset
- Ensure `reserve_percent` is reasonable

## Strategy Notes

This is **play money for learning**. The bot is configured to be:

- **Aggressive**: 30s timeout on orders, fast capital rotation
- **High Volume**: Multiple assets, compound gains
- **Risk-Aware**: But willing to take calculated losses
- **Learning-Focused**: Extensive logging for post-analysis

### Key Learnings to Track

1. Which assets are most profitable during 9am-6pm EST?
2. What's the optimal capital allocation per asset?
3. Does the 30-second timeout help or hurt?
4. Is 17:45 exit early enough? (market dumps at 18:30)
5. Which volatility profile works best for scalping?

## Advanced Usage

### Custom Asset Selection

Edit `config/active_trader_config.json`:

```json
{
  "assets": ["ETH-USD", "SOL-USD", "BTC-USD"],  // Only trade these
  "risk_management": {
    "max_concurrent_bots": 3  // Limit active bots
  }
}
```

### Manual Override

Stop all bots:
```bash
pkill -f profit_aware_bot.py
```

Stop master only:
```bash
pkill -f active_trader.py
```

### View Live Trades

```bash
tail -f logs/trades/trades_$(date +%Y-%m-%d).jsonl | jq '.'
```

## Files Reference

```
active_trader.py                    # Main controller
generate_asset_configs.py          # Config generator
config/
  ├── active_trader_config.json    # Master config
  ├── active_eth_config.yaml       # ETH bot config
  ├── active_sol_config.yaml       # SOL bot config
  └── ... (one per asset)
logs/
  ├── active_trader.log            # Master log
  ├── trades/                       # Trade logs (JSONL)
  └── session_report_*.txt         # Daily summaries
```

## Safety Checklist

Before running live:

- [ ] Verify `starting_capital` is correct
- [ ] Test Signal notifications work
- [ ] Check all asset configs generated properly
- [ ] Confirm trading hours are EST (not UTC)
- [ ] Review risk limits (5% total loss pause, etc.)
- [ ] Ensure `profit_aware_bot.py` path is correct
- [ ] Check API keys are in environment (.env)
- [ ] Test with small capital first ($100-200)

## Exit Strategy

**Normal Exit (17:45 EST)**:
1. Master sends termination signal to all bots
2. Bots cancel all BUY orders
3. SELL orders remain active
4. Wait 5 minutes for sells to complete
5. Generate session report
6. Send final P&L to Signal

**Emergency Exit (manual)**:
```bash
# Graceful shutdown
pkill -TERM -f active_trader.py

# Force kill (last resort)
pkill -KILL -f active_trader.py
pkill -KILL -f profit_aware_bot.py
```

## Next Steps

1. **Run in paper trading mode first** (if available)
2. **Start with 1-2 assets** to validate
3. **Gradually add more assets** as confidence grows
4. **Analyze logs daily** to refine configs
5. **Adjust profit targets** based on observed spreads
6. **Track which hours are most profitable**

---

**Remember**: This is for learning. Don't risk money you can't afford to lose. The market doesn't care about your config file. 🎯
