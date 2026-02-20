#!/usr/bin/env python3
"""
AUGUR Signal Webhook Integration

This script can be integrated into AUGUR signal generation to send trading signals to n8n.
It should be called from within the AUGUR signal processing pipeline.

Usage:
    python3 augur-signal-webhook.py <symbol> <signal> <confidence> [additional_data]

Example:
    python3 augur-signal-webhook.py "BTC/USD" "buy" "0.85" '{"price": 52000, "strategy": "V4.5"}'
"""

import sys
import json
import subprocess
import os
from datetime import datetime

def send_trading_signal(symbol, signal, confidence, additional_data=None):
    """Send trading signal event to n8n via openclaw-event"""
    
    # Validate inputs
    if not all([symbol, signal, confidence]):
        print(f"ERROR: Missing required parameters", file=sys.stderr)
        return False
        
    try:
        confidence_float = float(confidence)
        if not (0.0 <= confidence_float <= 1.0):
            print(f"ERROR: Confidence must be between 0.0 and 1.0, got: {confidence}", file=sys.stderr)
            return False
    except ValueError:
        print(f"ERROR: Invalid confidence value: {confidence}", file=sys.stderr)
        return False
    
    if signal.lower() not in ['buy', 'sell', 'hold']:
        print(f"ERROR: Invalid signal type: {signal}", file=sys.stderr)
        return False
    
    # Parse additional data
    metadata = {}
    if additional_data:
        try:
            metadata = json.loads(additional_data)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in additional_data: {e}", file=sys.stderr)
            return False
    
    # Build event data
    event_data = {
        "symbol": symbol,
        "signal": signal.lower(), 
        "confidence": confidence_float,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "strategy": metadata.get("strategy", "unknown"),
        "price": metadata.get("price"),
        "metadata": {
            "source": "augur",
            "version": metadata.get("version", "V4.5"),
            "indicators": metadata.get("indicators", []),
            "timeframe": metadata.get("timeframe", "4h"),
            "additional_info": {k: v for k, v in metadata.items() if k not in ['strategy', 'price', 'version', 'indicators', 'timeframe']}
        }
    }
    
    # Remove None values
    event_data = {k: v for k, v in event_data.items() if v is not None}
    
    # Check if openclaw-event exists
    openclaw_event_path = os.path.expanduser("~/bin/openclaw-event")
    if not os.path.isfile(openclaw_event_path) or not os.access(openclaw_event_path, os.X_OK):
        print(f"ERROR: openclaw-event script not found or not executable at {openclaw_event_path}", file=sys.stderr)
        return False
    
    # Send event
    try:
        result = subprocess.run([
            openclaw_event_path,
            "trading-signal", 
            json.dumps(event_data)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Trading signal sent successfully: {symbol} {signal} ({confidence})")
            return True
        else:
            print(f"ERROR: Failed to send trading signal (exit code {result.returncode})", file=sys.stderr)
            print(f"STDERR: {result.stderr}", file=sys.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"ERROR: Timeout sending trading signal", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Exception sending trading signal: {e}", file=sys.stderr)
        return False

def main():
    """Main entry point"""
    if len(sys.argv) < 4:
        print("Usage: python3 augur-signal-webhook.py <symbol> <signal> <confidence> [additional_data_json]")
        print("Example: python3 augur-signal-webhook.py 'BTC/USD' 'buy' '0.85' '{\"price\": 52000}'")
        sys.exit(1)
    
    symbol = sys.argv[1]
    signal = sys.argv[2]  
    confidence = sys.argv[3]
    additional_data = sys.argv[4] if len(sys.argv) > 4 else None
    
    success = send_trading_signal(symbol, signal, confidence, additional_data)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()