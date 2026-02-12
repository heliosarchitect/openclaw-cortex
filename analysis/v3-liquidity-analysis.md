# V3 Signal Liquidity Analysis

**Date:** 2026-02-11 23:30 EST  
**Source:** enhanced_data.db orderbook_snapshots + trade_flow  

## Order Book Depth (Best Bid/Ask Level)

| Product | Avg Spread % | Avg Bid Depth ($) | Avg Ask Depth ($) | Total Top-of-Book ($) |
|---------|-------------|-------------------|-------------------|-----------------------|
| MON-USD | 0.058% | $5,937 | $1,305 | $7,242 |
| BERA-USD | 0.338% | $1,912 | $1,688 | $3,600 |
| NKN-USD | 1.218% | $1,886 | $971 | $2,857 |
| GHST-USD | 0.977% | $1,840 | $935 | $2,775 |
| ZRO-USD | 0.106% | $901 | $717 | $1,618 |
| UNI-USD | 0.052% | $775 | $872 | $1,647 |
| BNKR-USD | 0.288% | $706 | $417 | $1,123 |
| RARI-USD | 0.078% | $327 | $111 | $438 |

## Trade Flow (Per 5-Second Bar, Active Bars Only)

| Product | Active Bars | Avg USD/Bar | Avg Trades/Bar |
|---------|-------------|-------------|----------------|
| BERA-USD | 14,395 | $1,651 | 5 |
| MON-USD | 19,905 | $1,390 | 5 |
| UNI-USD | 16,607 | $1,376 | 6 |
| ZRO-USD | 15,007 | $884 | 3 |
| BNKR-USD | 16,207 | $488 | 2 |
| NKN-USD | 5,896 | $436 | 3 |
| GHST-USD | 13,201 | $337 | 3 |
| RARI-USD | 4,821 | $262 | 6 |

## Verdict: Can We Fill $2K Orders at 5s Frequency?

### ✅ EXECUTABLE (Tier 2 — lower signal count but fillable)
- **UNI-USD**: $1,647 top-of-book, $1,376/5s volume, 0.052% spread. A $2K order would consume the book slightly but tight spread means low slippage. **Best candidate for live.**
- **MON-USD**: $7,242 top-of-book (best depth!), $1,390/5s volume. Can absorb $2K easily. But only 1,110 VIP2 signals.
- **ZRO-USD**: $1,618 top-of-book, $884/5s volume. $2K would move the market slightly. Use limit orders.

### ⚠️ PARTIALLY EXECUTABLE (Tier 3 — scale down to $500-1000)
- **BERA-USD**: $3,600 top-of-book, $1,651/5s volume. $2K is borderline. $1K safer. Best net return (+1.78%) makes this worth it even at half size.
- **NKN-USD**: $2,857 top-of-book but 1.22% spread eats into edge. 23,296 signals though. $500-1K positions.
- **GHST-USD**: $2,775 top-of-book, 0.98% spread. Most signals (83,689) but wide spread. Need maker orders.

### ❌ TOO THIN (reduce to $200-500 or skip)
- **BNKR-USD**: $1,123 top-of-book, $488/5s volume. 47K signals but $2K would wreck the book. $200-500 max.
- **RARI-USD**: $438 top-of-book (!), $262/5s volume. The #1 signal (+1.99% net) lives on the THINNEST product. $200 max positions. Even that might cause slippage at 5s intervals.

## Recommended Live Basket

| Product | Position Size | Expected Trades/Day | Est. Daily P&L |
|---------|--------------|--------------------:|---------------:|
| UNI-USD | $2,000 | 5-10 | $19-76 |
| MON-USD | $2,000 | 3-5 | $14-23 |
| BERA-USD | $1,000 | 10-20 | $178-356 |
| NKN-USD | $500 | 15-30 | $79-158 |
| GHST-USD | $500 | 20-40 | $128-256 |
| ZRO-USD | $1,500 | 3-5 | $7-11 |
| RARI-USD | $200 | 5-10 | $20-40 |
| BNKR-USD | $300 | 10-15 | $26-39 |

**Aggregate daily estimate**: ~70-135 trades, $471-959 gross (before execution slippage)

## Key Risk
These estimates assume NO slippage and NO market impact. Real fills on thin books will have:
- Wider effective spreads (especially GHST, NKN at ~1% spread)
- Front-running from other bots monitoring the same books
- Liquidity drying up if multiple bots trade the same signals

**Start conservative. Scale up only after confirming real fill rates match paper.**
