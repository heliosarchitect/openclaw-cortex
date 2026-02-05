# Websocket Crash Analysis - 2026-02-05

## Pattern
- Crashes every ~30 minutes exactly
- Error: RuntimeError: Event loop is closed
- Preceded by: OSError: Bad file descriptor

## Attempted Fixes
1. ✗ Removed duplicate trader.run() call (13:35) - didn't solve it
2. ✗ Made asyncio task cancellation graceful (14:16) - didn't solve it

## Hypothesis
The websocket heartbeat logic disconnects after 30min of silence, then the reconnection code tries to use a closed event loop.

## Next Investigation Steps
1. Check if there's a 30-minute timeout in Coinbase websocket protocol
2. Look for event loop closure in websocket reconnection paths
3. Check if the ping/pong mechanism is actually working
4. Look for file descriptor cleanup issues before reconnect

## Key Code Locations
- core/market_data.py: Lines 762-767, 794-802 (ping_task cancellation)
- Websocket reconnection logic needs deeper review
