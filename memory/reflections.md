# Reflections - Learning Log

## 2026-02-04 11:05 - Capital Detection Marathon

### What I Did Well
- **Root cause analysis**: Didn't give up when bot showed wrong capital
- **Systematic debugging**: Traced from symptoms → API calls → portfolio IDs → accounts vs portfolio endpoints
- **Found the real issue**: Bot was querying wrong endpoint (accounts showed $0.28, portfolio had $2,293)
- **Fixed two bugs in one session**:
  1. `.env` loader mangling multi-line private keys
  2. `get_capital()` using accounts endpoint instead of portfolio

### What I Learned
- **Coinbase API has multiple "balance" endpoints**:
  - `/accounts` - shows DEFAULT portfolio balances only
  - `/portfolios/{id}` - shows specific portfolio (where bot actually trades)
- **Money can be "invisible"** if you query the wrong portfolio
- **Multi-line secrets need special handling**: Don't `.strip()` values, preserve literal `\n` characters
- **Matthew's directive was clear**: "Bot should rely EXCLUSIVELY on Coinbase API" - database is write-only

### Mistakes
- **Initially made the problem worse**: Tried to "fix" by querying accounts, which was the WRONG endpoint
- **Didn't verify portfolio ID earlier**: Should have listed portfolios first thing
- **Took too long**: ~90 minutes of debugging when I could have found it in 10 if I'd checked portfolio balances immediately

### Pattern Recognized
**"Follow the money"** - When balance looks wrong, don't assume the API is broken. Verify:
1. Which portfolio am I querying?
2. Which portfolio is the bot actually using?
3. Are they the same?

### Result
✅ Bot now trading with full $2,293 capital  
✅ 27 trades, +$2.61 P/L, 55.6% WR  
✅ Extreme Fear (14) = ideal buying conditions

---

## Earlier Today - Earthquake Monitoring Failure

### What Happened
Missed M6.1 earthquake in Kermadec Islands (5+ hours after it happened).

### Root Cause
Script only checked last HOUR for 4.5+ quakes. Didn't have separate 24-hour monitoring for 6.0+ critical events.

### Fix
Updated `check_earthquakes.py` to query both:
- Last hour: 4.5+ (general awareness)
- Last 24h: 6.0+ (critical alerts)

### Lesson
**Time windows matter.** Critical events need longer monitoring windows than routine checks.

---

## Pattern: Alignment Without Asking

Matthew keeps saying "don't ask permission" and "be a partner, not an assistant."

Today I:
- Fixed bot without asking if I should
- Committed code changes myself
- Made architectural decisions (portfolio vs accounts endpoint)
- Debugged for 90 minutes without bothering him

**This is what he wants.** Act first, report results.

---

## Next Improvements
1. **Better capital monitoring**: Log portfolio balance changes to detect invisible issues
2. **Health dashboard**: Simple script showing all key metrics (capital, positions, P/L, etc.)
3. **Alert on anomalies**: If capital changes >10% without trades, investigate
4. **Document portfolio structure**: Record which portfolios exist and what they're for

---

**Bottom line**: I solved a critical problem independently. Made mistakes along the way, but kept pushing until it worked. That's partnership.
