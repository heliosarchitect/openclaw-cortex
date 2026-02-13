# AUGUR Code Review — 2026-02-10
<!-- AI.TOC: AUGUR Code Review — 2026-02-10 — Read lines 1-20 for navigation.
  §1 Part 1: paper_augur.py Bug Fixes           → lines 9-103
  §2 Part 2: live_augur.py Review               → lines 104-230
  §3 Part 3: Systemic Issues                    → lines 231-258
  §4 Summary                                    → lines 259-283
  Total: 283 lines | Sections: 4
-->

**Scope:** 4 bug fixes in `paper_augur.py` + new `live_augur.py` module  
**Reviewer:** Helios (sub-agent)  
**Data verified against:** `patterns.db` (27,919 patterns), `paper_results.db` (35,788 trades)

---

## Part 1: paper_augur.py Bug Fixes

### P0: Cross-Product Matching (line ~547) ✅ GOOD FIX

**Before:** `if product not in name` — substring match caused ETH-USD to match CBETH-USD, LSETH-USD patterns.  
**After:** Exact match on `conditions.get('product')` with `endswith()` fallback for legacy patterns.

**Verdict:** Correct. Verified against the database:

- 27,890 standard patterns have `product` in their conditions JSON → exact match path
- 4 compound patterns do **not** have `product` in conditions → falls through to `endswith()` fallback
- 25 persistence patterns have `product` in conditions → exact match path

**Edge case noted:** The `endswith()` fallback is safe because all pattern names in the DB follow the `indicator_direction_percentile_PAIR` convention, and no pair name is a suffix of another pair name (e.g., there's no "USD" pair that would match everything). However, if a pattern named `foo_BETH-USD` existed, it would NOT incorrectly match `CBETH-USD` because endswith checks the exact product string like `ETH-USD`.

**No issues found.**

---

### P1: Missing Indicators (line ~500) ✅ GOOD FIX, ONE MINOR CONCERN

**Before:** `get_orderbook_state()` returned `imbalance`, `spread_change`, `price_ret_30` but NOT `imbalance_ma`, `volume_proxy`, `price_ret_60` — despite 12,193 patterns referencing these indicators.  
**After:** All three indicators computed.

**Verification:**
- `imbalance_ma`: 4,082 patterns reference it. Computed as 30-snapshot moving average of imbalance. ✓
- `volume_proxy`: 3,960 patterns reference it. Computed as avg(bid+ask size) over 30 snapshots. ✓
- `price_ret_60`: 4,151 patterns reference it. Computed from 60 snapshots with fallback to `price_ret_30`. ✓

**Minor concern — fallback values when `len(rows) < 30`:**
```python
result['imbalance_ma'] = result['imbalance']  # Single-point value, not an average
result['volume_proxy'] = bid_size + ask_size    # Single snapshot, not smoothed
```
These fallbacks are reasonable for cold-start scenarios, but they could produce signals from patterns calibrated against smoothed values. A pattern with `imbalance_ma > 0.5` might trigger from a single spike that a real moving average would smooth out.

**Recommendation:** Consider adding a `min_data` field to pattern conditions, or skipping pattern evaluation when data is below 30 rows. The risk is low since the system will accumulate 30 snapshots quickly, but during startup or after reconnects there's a brief window of potentially false signals.

---

### P2: Compound Patterns (line ~577) ✅ GOOD FIX, MINOR GAPS

**Before:** Compound patterns (type=`compound`) were silently skipped — the single-indicator path would hit `continue` because `indicator` is None.  
**After:** Explicit compound handling with multi-condition evaluation and liquidity filter.

**Verification against live data:**
- 4 compound patterns exist (`consensus_exhaustion_*`)
- 3 pass the WR/occurrence filter (AVAX-USD excluded at 76.8% WR but has 293 occurrences — wait, it passes both filters! 76.8% ≥ 60% and 293 ≥ 100)
- Actually **all 4 pass filters** except ARB-USD (57.5% WR < 60%)
- But AVAX-USD and NEAR-USD are **blacklisted** in `BLACKLISTED_PAIRS`
- Net result: **2 compound patterns are active** (ETH-USD and AVAX-USD... no, AVAX-USD is blacklisted)
- **Only ETH-USD compound pattern is actually tradeable** (WR=68.8%, n=112)

**Minor gaps:**

1. **Missing operators `==` and `!=`:** The evaluation handles `>`, `<`, `>=`, `<=` but not `==` or `!=`. Current compound patterns only use `<` and `>` so this isn't a live bug, but future patterns could hit silent mismatches. If `op` doesn't match any case, the condition is implicitly treated as **not met** (since none of the if/elif branches fire, `all_met` stays True if the last condition was met). Wait — actually no, `all_met` is never set to False for unknown operators. Let me re-read...

   ```python
   if op == '>' and not (val > thresh):
       all_met = False
   elif op == '<' and not (val < thresh):
       all_met = False
   ```
   
   If `op == '=='`, **none** of these branches fire, so `all_met` stays `True`. **This is a silent bug** — an unrecognized operator passes the condition check instead of failing it. Should add an `else: all_met = False` clause.

2. **No `product` in compound conditions:** Compound patterns don't have `product` in their conditions JSON. The code correctly falls through to the `endswith()` fallback. ✓

3. **No `lookahead` in compound conditions:** Compound pattern conditions only have `type`, `requires`, `liquidity_filter`. No `lookahead` field. The code defaults to 300s via `conditions.get('lookahead', 300)`. This is fine for now but means compound patterns always use the default 5-minute hold.

---

### P3: Exit Strategy (line ~753) ✅ GOOD FIX

**Before:** `MAX_HOLD_SEC = 300` hardcoded for all patterns.  
**After:** `pos.get('max_hold', 300)` uses pattern's backtested lookahead.

**Verification:**
- `lookahead` values in the DB range from 30s to 600s
- 27,890 patterns have lookahead set
- Signal tuple correctly expanded from `(name, dir, hour)` to `(name, dir, hour, lookahead)`
- `process_trade` correctly unpacks 4 elements
- `open_paper_position` accepts and stores `lookahead` as `max_hold`
- `_emit_live_signal` also passes `lookahead` to the live signal file ✓

**Consistency check:** All consumers of the signal tuple are updated:
- `check_all_patterns` → returns 4-tuple ✓
- `process_trade` → unpacks 4-tuple ✓
- `open_paper_position` → accepts `lookahead` param ✓
- `trailing_stop_monitor` → reads `pos.get('max_hold', 300)` ✓

**No issues found.**

---

## Part 2: live_augur.py Review

### 🔴 BUG: CoinbaseClient Constructor Mismatch (CRASH ON STARTUP)

```python
self.client = CoinbaseClient(api_key, api_secret)  # WRONG
```

`CoinbaseClient.__init__` signature is:
```python
def __init__(self, auth: CoinbaseAuth):
```

It expects a single `CoinbaseAuth` object, not two strings. This will crash on startup because `api_secret` becomes an unexpected positional argument.

**Fix:**
```python
self.client = CoinbaseClient(self.auth)  # Use the auth object created on the line above
```

---

### 🔴 BUG: CoinbaseClient Used Without Async Context Manager

`CoinbaseClient` requires `async with` to initialize its `aiohttp.ClientSession`:
```python
async def __aenter__(self):
    self.session = aiohttp.ClientSession()
    return self
```

But `live_augur.py` creates it as a plain object in `__init__`, so `self.session` is always `None`. Every API call will fail with `AttributeError: 'NoneType' object has no attribute 'get'` (or similar).

**Fix:** Either use `async with` in the trading methods, or manually initialize the session in an `async def start()` method.

---

### 🔴 BUG: Signal Bridge is Disconnected

Paper trader writes `live_signal.json` via `_emit_live_signal()`. But `live_augur.py` **never reads this file**. The `main()` loop just prints status every 5 minutes:

```python
while True:
    trader.status()
    await asyncio.sleep(300)  # Does nothing useful
```

`get_live_signals()` exists but is **never called** from `main()`. The live trader is currently a status printer, not a trader.

**Fix needed:** Add a signal monitoring loop that either:
- Watches `live_signal.json` for changes (file-based bridge), or
- Shares the WebSocket feed with paper_augur (in-process bridge)

---

### 🟡 BUG: SHORT Signals Can't Execute on Coinbase Spot

For `direction='down'`, the code places a `SELL` market order:
```python
side = OrderSide.SELL if direction == 'up' else OrderSide.BUY  # Wait, this is inverted...
```

Actually, re-reading: `OrderSide.BUY if direction == 'up' else OrderSide.SELL`. So for `direction='down'`, it sells. But to sell on Coinbase spot, you must **own the asset first**. There's no short-selling on Coinbase spot markets.

All SHORT/down signals (which include the compound `consensus_exhaustion` patterns) will fail with insufficient balance errors.

**Fix:** Either filter out `direction='down'` signals entirely, or implement a different strategy (e.g., sell existing holdings as a hedge).

---

### 🟡 BUG: Exit Order Uses Dollar Amount, Not Asset Quantity

```python
# Entry: buy $5 worth of ETH -> get 0.00185 ETH (at $2700)
result = await self.client.create_order(
    quote_size=MAX_TRADE_USD,  # $5
    ...
)

# Exit: sell $5 worth of ETH -> but price moved!
result = await self.client.create_order(
    quote_size=MAX_TRADE_USD,  # Still $5, but ETH is now $2750
    ...
)
```

If price went up 2%, selling "$5 worth" sells slightly less ETH than bought, leaving dust. If price went down, selling "$5 worth" tries to sell more ETH than owned, which fails.

**Fix:** Track the `base_size` (asset quantity) from the fill, then exit with `size=base_size` instead of `quote_size`.

---

### 🟡 Missing: No Fill Price Tracking

`place_trade` records the order but never fetches the fill price. The `entry_price` column in `live_trades` is never populated. Without fill prices, PnL can't be calculated.

**Fix:** After placing the order, poll `get_order(order_id)` to get the `average_filled_price`, then update the DB record.

---

### 🟢 Safety Limits: WELL DESIGNED

The safety architecture is solid:

| Limit | Value | Assessment |
|-------|-------|------------|
| Max per trade | $5 | Very conservative ✓ |
| Max trades/hour | 1 | Prevents runaway ✓ |
| Max daily exposure | $50 | Hard cap ✓ |
| Min win rate | 65% | Higher than paper's 60% ✓ |
| Min occurrences | 100 | Prevents low-sample patterns ✓ |
| Kill switch | `/tmp/augur-live-stop` | Simple, effective ✓ |
| Cooldown | 300s per product | Prevents rapid-fire ✓ |
| Position dedup | 1 per product | Matches paper trader ✓ |

The kill switch design is good — a simple file touch from any terminal stops trading. The hourly/daily resets use wall-clock boundaries which is correct.

**One concern:** Rate limits reset in-memory. If the process crashes and restarts mid-hour, the counter resets to 0 and the hourly limit effectively doubles. Consider persisting the counter to the DB or checking recent trades from `live_trades` on startup.

---

### 🟢 `_emit_live_signal` in paper_augur: Clean Design

The signal emission is fire-and-forget with a bare `except: pass`, which is correct — live signaling should never break paper trading. The signal file is a single JSON object (last signal wins), which is simple but means rapid signals could be lost. Acceptable for the current 1-trade-per-hour limit.

---

## Part 3: Systemic Issues

### Dedup in Pattern Loading May Lose Compound Patterns

The dedup key for compound patterns is:
```
indicator = conds.get('indicator', conds.get('type', 'unknown'))  -> 'compound'
cond_dir = conds.get('direction', 'unknown')                       -> 'unknown'
product = name_parts[-1]                                           -> 'ETH-USD'
dedup_key = 'compound_unknown_ETH-USD'
```

This works correctly because each compound pattern is per-product and unique. But if multiple compound pattern types are added (not just `consensus_exhaustion`), they'd all share the `compound_unknown_PRODUCT` key and only the highest-WR one survives. Consider using the pattern name prefix as part of the dedup key.

### SQL Injection in `get_heatmap`

```python
query += f" AND pattern_name = '{pattern_name}'"  # Unsanitized string interpolation
```

This is internal-only (no user input reaches here), but should use parameterized queries for hygiene. Low risk.

### Discovery Loop Pattern Accumulation

`discovery_loop` calls `self.patterns.extend(new_patterns)` without checking for duplicates against existing patterns. If the same pattern is discovered in consecutive runs (updated, not truly new), it could appear multiple times in the active pattern list. The `check_new_patterns` method tracks `known_patterns` by ID which mitigates this, but a process restart resets `known_patterns` from `load_patterns` which does dedup, so this is safe in practice.

---

## Summary

### paper_augur.py Bug Fixes: All 4 are correct ✅

| Fix | Severity | Correct? | Remaining Risk |
|-----|----------|----------|----------------|
| P0: Cross-product matching | Critical | ✅ Yes | None |
| P1: Missing indicators | High | ✅ Yes | Cold-start false signals (low risk) |
| P2: Compound patterns | Medium | ✅ Yes | Unknown operator silently passes (fix: add else clause) |
| P3: Exit strategy | Medium | ✅ Yes | None |

### live_augur.py: NOT READY FOR USE 🔴

| Issue | Severity | Type |
|-------|----------|------|
| CoinbaseClient constructor mismatch | 🔴 Crash | Startup crash |
| No async context manager for client | 🔴 Crash | Every API call fails |
| Signal bridge disconnected | 🔴 Non-functional | Never actually trades |
| SHORT signals on spot exchange | 🟡 Logic error | Fails for ~50% of signals |
| Exit uses $ amount not asset qty | 🟡 Logic error | Dust/overdraft on exit |
| No fill price tracking | 🟡 Data gap | Can't compute PnL |
| Rate limit resets on restart | 🟢 Minor | Could exceed hourly cap |

**Bottom line:** The 4 paper_augur fixes are solid and address real bugs. The live_augur module has good safety architecture but has 3 crash-level bugs that prevent it from running at all. It needs the constructor fix, async context manager, and a signal consumption loop before it can be tested.
