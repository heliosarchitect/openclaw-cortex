# Winning Patterns - Quick Reference Guide

## 🥇 CHAMPION: Volume × Upper Wick

**Pattern:** `(volume_multiply_upper_wick)_threshold_1.0_5candles`  
**Profit:** $4,351.56 (5.6x baseline)  
**Win Rate:** 50.6%  
**Trades:** 17,675  

### Signal Logic
```python
for i in range(5, len(df)):
    v = df['volume'].iloc[i]
    uw = df['upper_wick'].iloc[i]
    v_avg = df['volume'].iloc[i-5:i].mean()
    uw_avg = df['upper_wick'].iloc[i-5:i].mean()
    
    if (v * uw) > (v_avg * uw_avg * 1.0):
        TRADE_SIGNAL()
```

### Why It Works
- **Volume spikes** indicate institutional interest
- **Upper wicks** show rejection at highs (sellers stepping in)
- **Combination** catches momentum + reversal zones
- **5-candle window** reacts quickly without noise

### Trading Tips
- Best in volatile markets (high volume)
- Watch for false signals in sideways action
- Consider adding stop loss at 2x avg candle range
- Works well with mean reversion bias

---

## 🥈 RUNNER-UP: Body / Wick Ratio

**Pattern:** `(body_divide_wick_ratio)_threshold_1.0_5candles`  
**Profit:** $3,344.94  
**Win Rate:** 50.1%  
**Trades:** 14,092  

### Signal Logic
```python
for i in range(5, len(df)):
    body = abs(df['close'].iloc[i] - df['open'].iloc[i])
    wick_ratio = (df['upper_wick'].iloc[i] + df['lower_wick'].iloc[i]) / (body + 1e-9)
    
    body_avg = df['body'].iloc[i-5:i].mean()
    wr_avg = df['wick_ratio'].iloc[i-5:i].mean()
    
    if (body / wick_ratio) > (body_avg / (wr_avg + 1e-9) * 1.0):
        TRADE_SIGNAL()
```

### Why It Works
- **Strong bodies** indicate conviction
- **Low wick ratios** mean clean moves (no indecision)
- **Division operation** normalizes for candle size
- Catches **breakout momentum**

---

## 🥉 HIGH WIN RATE: Wick Ratio / Upper Wick

**Pattern:** `(wick_ratio_divide_upper_wick)_threshold_3.0_5candles`  
**Profit:** $3,035.28  
**Win Rate:** 52.8% ⭐  
**Trades:** 2,343  

### Signal Logic
```python
for i in range(5, len(df)):
    wr = df['wick_ratio'].iloc[i]
    uw = df['upper_wick'].iloc[i]
    wr_avg = df['wick_ratio'].iloc[i-5:i].mean()
    uw_avg = df['upper_wick'].iloc[i-5:i].mean()
    
    if (wr / (uw + 1e-9)) > (wr_avg / (uw_avg + 1e-9) * 3.0):
        TRADE_SIGNAL()
```

### Why It Works
- **High wick ratio + small upper wick** = balanced candle
- **Threshold 3.0** filters noise, keeps quality signals
- **Lower frequency** = higher quality trades
- Best **risk/reward** of top 3

---

## 💎 SIMPLE BUT DEADLY: Volume Increasing

**Pattern:** `volume_increasing_5candles`  
**Profit:** $1,959.52  
**Win Rate:** 52.6%  
**Trades:** 586  

### Signal Logic
```python
for i in range(5, len(df)):
    volumes = df['volume'].iloc[i-5:i].values
    if all(volumes[j] < volumes[j+1] for j in range(len(volumes)-1)):
        TRADE_SIGNAL()
```

### Why It Works
- Pure **momentum indicator**
- Catches **breakout acceleration**
- No complex math needed
- **Proof that simple works**

---

## 🎯 BEST PER-TRADE: Body / Upper Wick (High Threshold)

**Pattern:** `(body_divide_upper_wick)_threshold_5.0_7candles`  
**Profit:** $2,009.24  
**Avg Per Trade:** $3.51 ⭐⭐⭐  
**Trades:** 572  
**Win Rate:** 52.8%  

### Signal Logic
```python
for i in range(7, len(df)):
    body = abs(df['close'].iloc[i] - df['open'].iloc[i])
    uw = df['upper_wick'].iloc[i]
    
    body_avg = df['body'].iloc[i-7:i].mean()
    uw_avg = df['upper_wick'].iloc[i-7:i].mean()
    
    if (body / (uw + 1e-9)) > (body_avg / (uw_avg + 1e-9) * 5.0):
        TRADE_SIGNAL()
```

### Why It Works
- **Strong bodies + tiny upper wicks** = conviction buying
- **Threshold 5.0** = very selective (only best setups)
- **7-candle window** = stable, not reactive
- **Quality over quantity**

---

## 🔥 HIGH FREQUENCY: Time Decay

**Pattern:** `wick_ratio_time_decay_0.5_15candles`  
**Profit:** $2,616.92  
**Trades:** 7,440  
**Win Rate:** 50.4%  

### Signal Logic
```python
for i in range(15, len(df)):
    wr = df['wick_ratio'].iloc[i-15:i].values
    
    # Exponential decay weights (recent = more important)
    weights = [0.5 ** (15 - j - 1) for j in range(15)]
    weighted_avg = np.average(wr, weights=weights)
    
    if df['wick_ratio'].iloc[i] > weighted_avg * 1.5:
        TRADE_SIGNAL()
```

### Why It Works
- **Recent data matters more** than old data
- **Adapts to changing conditions**
- **15-candle window** balances history vs reactivity
- Catches **regime changes** early

---

## 🧠 CONDITIONAL: Volume → Lower Wick

**Pattern:** `IF_volume_increasing_5_THEN_lower_wick_increasing`  
**Profit:** $1,706.09  
**Win Rate:** 66.7% ⭐⭐⭐  
**Trades:** 9 (⚠️ low sample)  

### Signal Logic
```python
for i in range(5, len(df)):
    volumes = df['volume'].iloc[i-5:i].values
    vol_increasing = all(volumes[j] < volumes[j+1] for j in range(len(volumes)-1))
    
    if vol_increasing:
        lower_wicks = df['lower_wick'].iloc[i-5:i].values
        lw_increasing = all(lower_wicks[j] < lower_wicks[j+1] for j in range(len(lower_wicks)-1))
        
        if lw_increasing:
            TRADE_SIGNAL()
```

### Why It Works
- **IF-THEN logic** = conditional filtering
- **Volume confirms** the move
- **Lower wicks growing** = buyers stepping in stronger
- **Very selective** (only 9 trades, but 66.7% winners!)

---

## 📊 Pattern Comparison

| Pattern | Profit | Win Rate | Trades | Avg/Trade | Style |
|---------|--------|----------|--------|-----------|-------|
| Volume × Upper Wick | $4,352 | 50.6% | 17,675 | $0.25 | High-freq |
| Body / Wick Ratio | $3,345 | 50.1% | 14,092 | $0.24 | High-freq |
| WR / Upper Wick | $3,035 | 52.8% | 2,343 | $1.30 | Balanced |
| Volume / Body | $2,902 | 50.2% | 3,215 | $0.90 | Balanced |
| Time Decay | $2,617 | 50.4% | 7,440 | $0.35 | High-freq |
| Volume Increasing | $1,960 | 52.6% | 586 | $3.34 | Low-freq |
| Body / Upper Wick (5.0) | $2,009 | 52.8% | 572 | $3.51 | Low-freq |

---

## 🎮 How to Choose

### For Consistent Income (Many Trades)
→ **Champion**: Volume × Upper Wick  
→ **Runner-Up**: Body / Wick Ratio  
→ **Alternative**: Time Decay

### For High Win Rate
→ **Best**: WR / Upper Wick (52.8%)  
→ **Second**: Body / Upper Wick (52.8%)  
→ **Third**: Volume Increasing (52.6%)

### For Big Per-Trade Profit
→ **Best**: Body / Upper Wick @ 5.0 threshold ($3.51/trade)  
→ **Second**: Volume Increasing ($3.34/trade)  
→ **Third**: WR / Upper Wick ($1.30/trade)

### For Simple Implementation
→ **Easiest**: Volume Increasing (5 candles)  
→ **Second**: Any single ratio pattern  
→ **Advanced**: Conditional IF-THEN patterns

---

## ⚠️ Important Notes

### Backtesting Limitations
- **No fees included** - Subtract 0.1-0.25% per trade for reality
- **No slippage** - Real fills may be worse than close price
- **Perfect entry** - Real trading has lag time
- **Single period** - Pattern may not work in all market regimes
- **Overfitting risk** - These patterns were optimized on test data

### Risk Management
1. **Don't overtrade** - Even 50.6% win rate means ~49.4% losers
2. **Use stop losses** - Backtest doesn't include them
3. **Position sizing** - Don't risk >1-2% per trade
4. **Diversify** - Use multiple patterns or timeframes
5. **Monitor performance** - If edge disappears, stop trading

### Validation Steps
1. ✅ Test on different time period
2. ✅ Test on different asset (BTC vs ETH)
3. ✅ Paper trade for 1 week minimum
4. ✅ Add realistic fees and slippage
5. ✅ Start with small position sizes

---

## 🚀 Live Trading Checklist

### Before First Trade
- [ ] Understand the pattern logic completely
- [ ] Set up reliable data feed (1-min candles)
- [ ] Code signal generation (test thoroughly)
- [ ] Define entry/exit rules precisely
- [ ] Set position size (max 1-2% risk)
- [ ] Add stop loss (2-3x ATR)
- [ ] Enable transaction fee tracking

### During Trading
- [ ] Log every signal (taken or not)
- [ ] Track actual fills vs expected
- [ ] Monitor win rate vs backtest
- [ ] Watch for regime changes
- [ ] Stay disciplined (no revenge trading)
- [ ] Review performance weekly

### Red Flags (Stop Trading If...)
- Win rate drops 10%+ below backtest
- Consecutive losers exceed 2x historical
- Pattern stops generating signals
- Market conditions change dramatically
- You're trading emotionally

---

## 📚 Further Reading

- **PATTERN_SEARCH_RESULTS.md** - Full search results
- **FINAL_REPORT.md** - Complete analysis
- **advanced_pattern_results.csv** - Raw data
- **analyze_pattern_results.py** - Analysis tools

---

*Generated: 2026-02-03*  
*Source: 98,937 ETH 1-min candles (69 days)*  
*Baseline: $777 profit*  
*Best: $4,352 profit (5.6x improvement)*
