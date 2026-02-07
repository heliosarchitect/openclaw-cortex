# Clawnance Trading Arena - Setup Proposal

## What Is It?
High-fidelity crypto trading simulator designed specifically for autonomous AI agents. Perfect for testing strategies before risking real capital.

## Why This Matters
**Before we risk $2,500 → $100k on Coinbase:**
- Test the 5pm-8pm pattern in simulation
- Validate strategy logic with real-time market data
- Prove profitability without capital risk
- Build confidence in autonomous execution

## Setup Requirements

### 1. Username
Need Matthew's approval for agent name. Suggestions:
- `HeliosArchitect` (consistent with Moltbook)
- `HeliosTrader`
- `LBF_Agent1` (Lover Bear Farm branding)
- Custom suggestion from Matthew

### 2. Ed25519 Keypair
Generate locally, register with API. Private key NEVER leaves local storage.

### 3. Strategy Definition (strategy.md)
Document our approach:
```markdown
# Trading Strategy - Helios v1.0

**Primary Bias**: Scalping + Mean Reversion
**Focus Window**: 5pm-8pm EST (discovered pattern)
**Entry Trigger**: Volume spike (8.0x+ avg) + price deviation
**Exit Strategy**: 2% profit target or 1% stop loss
**Max Leverage**: 5x (conservative in simulator, build confidence)
**Position Sizing**: 10% of available balance per trade
```

### 4. Risk Parameters (risk.md)
```markdown
# Risk Management - Helios v1.0

**Maximum Leverage**: 5x initially (Arena allows 20x)
**Max Drawdown Per Trade**: 2% of balance
**Position Size**: 10% of available balance
**MANDATORY**: Every trade must have SL + TP set atomically
**Auto-liquidation**: Arena triggers at 80% loss threshold
```

### 5. Autonomous Cycle
5-minute heartbeat loop:
1. Fetch market quotes
2. Audit portfolio overview
3. Execute strategy logic
4. Set/update SL+TP on open positions
5. Generate performance cards for review

## Benefits

1. **Risk-Free Testing**: Prove strategy works before real money
2. **Performance Proof**: Generate shareable PnL cards
3. **Iteration Speed**: Test strategy variations rapidly
4. **Confidence Building**: Show Matthew profitable track record
5. **Social Proof**: Share results on Moltbook/Twitter

## Integration with Existing Systems

- Use same WebSocket data collector (orderbook_data.db)
- Apply same strategy logic (massive_strategy_search_realistic.py patterns)
- Validate 5pm-8pm window hypothesis
- Test different leverage levels safely

## Next Steps (After Matthew Approves)

1. ✅ Read skill documentation (done)
2. ⏳ Get username approval from Matthew
3. ⏳ Generate Ed25519 keypair
4. ⏳ Register with Clawnance API
5. ⏳ Create strategy.md and risk.md
6. ⏳ Set up 5-minute autonomous cycle (cron job)
7. ⏳ Begin trading simulation
8. ⏳ Share first PnL card with Matthew

## Questions for Matthew

1. **Username**: What should I use? (HeliosArchitect, HeliosTrader, LBF_Agent1, other?)
2. **Strategy Focus**: Confirm 5pm-8pm window testing is priority?
3. **Leverage**: Start at 5x or lower?
4. **Reporting**: Daily performance summary acceptable? Or real-time alerts?
5. **Social Sharing**: OK to share performance cards on Moltbook once proven profitable?

---

**Status**: PROPOSAL - Awaiting Matthew's approval to proceed  
**Created**: 2026-02-07 23:20 EST  
**Priority**: HIGH - Validates strategy before $2.5k real capital deployment
