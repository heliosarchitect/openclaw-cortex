# Adaptive Win-Rate Strategy
**Built from: Feb 4, 2026 trading analysis**

## The Problem
- Traded all day: 296 trades, 50.3% WR, -$7.34
- Only noon was good: 38 trades, 81.6% WR, +$7.23
- Rest of day: disaster (31-55% WR)

## The Solution
**Stop trading when conditions degrade, resume when they improve.**

## Strategy Rules

### 1. Real-Time Win Rate Tracking
- Track rolling 1-hour win rate
- Update after every trade
- Calculate: (wins in last hour) / (total trades in last hour)

### 2. Auto-Pause Trigger
**STOP TRADING when:**
- Rolling 1-hour WR drops below 55%
- OR: 3 consecutive losses
- OR: More than 40 trades in 1 hour (overtrading)

### 3. Resume Conditions
**Resume trading only when:**
- 30 minutes have passed since pause
- AND market shows 3 consecutive "good" signals:
  - Spread < 0.3%
  - Volume increasing
  - No rapid price swings

### 4. Trade Limits
- **Max 38 trades/hour** (even during good conditions)
- **Max 4 positions per asset** (existing rule)
- **Min 2-minute gap** between trades (prevent churning)

## Implementation

### Phase 1: Add Win-Rate Tracker
```python
class WinRateMonitor:
    def __init__(self):
        self.trades = deque(maxlen=100)  # Last 100 trades
        self.paused = False
        self.pause_time = None
        
    def add_trade(self, won):
        self.trades.append({
            'won': won,
            'time': time.time()
        })
        
    def get_hourly_wr(self):
        hour_ago = time.time() - 3600
        recent = [t for t in self.trades if t['time'] > hour_ago]
        if len(recent) < 10:  # Need at least 10 trades
            return None
        wins = sum(1 for t in recent if t['won'])
        return (wins / len(recent)) * 100
        
    def should_trade(self):
        if self.paused:
            # Check if enough time passed
            if time.time() - self.pause_time < 1800:  # 30 min
                return False
            # Check for resume signals (implement later)
            return self.check_resume_signals()
            
        # Check if we should pause
        wr = self.get_hourly_wr()
        if wr and wr < 55:
            self.pause("Win rate dropped to {wr:.1f}%")
            return False
            
        return True
```

### Phase 2: Integrate into Bot
- Add monitor to live_trader_final.py
- Call `monitor.add_trade()` after every exit
- Check `monitor.should_trade()` before every entry
- Log pause/resume events

### Phase 3: Backtest Validation
- Run on Aug-Nov data with this rule
- Expected: Fewer trades, higher WR, better profit
- Target: 65%+ WR, positive P/L

## Expected Results
If we had used this today:
- **Actual**: 296 trades, 50.3% WR, -$7.34
- **With adaptive WR**: ~56 trades, 73%+ WR, +$10 est.
- **Improvement**: $17+ swing

## Next Steps
1. Implement WinRateMonitor class
2. Add pause/resume logic to bot
3. Test on historical data
4. Deploy with monitoring

---
**Key Insight**: Quality > Quantity. One golden hour beats 9 hours of grinding.
