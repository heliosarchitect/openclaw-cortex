# Reflections - 2026-02-04

## Morning Trading Bot Launch (9:00-9:35 AM)

### What Went Wrong
Spent 30+ minutes debugging bot "crashes" that turned out to be my own testing mistakes. Used `timeout` commands and improper backgrounding that killed the process, then blamed the code.

### What I Learned
1. **Test end-to-end before production** - Matthew was right. Should have run a full cycle in pre-market instead of rushing to launch at 9:00 AM.
2. **Process management matters** - `setsid` for proper daemon detachment, not `&` alone
3. **Exception handling scope** - Critical code (opportunity sorting) was outside try/except block
4. **Stop seeking permission** - Matthew: "Be proactive, you don't need my permission to fix something that is broken"

### Actual Bugs Found
1. `KeyError: 'size'` - Position dict uses `size_usd`, not `size`
2. Try/except scope bug - Opportunity sorting outside exception handler caused silent crashes
3. Order timeout too aggressive - 60s → 300s for limit orders to fill

### What Worked
- VolumeWick strategy (ID 546986) loaded successfully
- Bot processes stop losses correctly
- Time-segment logic functioning
- Multi-pair scanning working (50 assets)

### Decision Quality
**Bad:** Wasted Matthew's morning trading time (9:00-9:35) debugging during prime market hours with Extreme Fear conditions.

**Good:** Once I stopped asking permission and just fixed things, got bot stable in ~10 minutes.

### Next Time
- Test bot fully in pre-market (6-9 AM)
- Use proper daemon tools (`systemd` service?)
- Don't launch untested code at market open
- Fix first, report results after

## Bot Performance (Current)
- 755 trades total
- $65.35 P/L
- 80.4% win rate (607W/148L)
- Running stable for 4+ minutes after fixes

---

*Lesson: Competence > asking permission. Act decisively when something is broken.*
