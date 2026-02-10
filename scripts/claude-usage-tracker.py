#!/usr/bin/env python3
"""Claude API Usage Tracker — Reads OpenClaw session JSONL files to compute token usage and costs.

Usage:
    python3 claude-usage-tracker.py                    # Today's usage
    python3 claude-usage-tracker.py --days 7           # Last 7 days
    python3 claude-usage-tracker.py --all              # All time
    python3 claude-usage-tracker.py --json             # JSON output
    python3 claude-usage-tracker.py --by-session       # Breakdown by session
    python3 claude-usage-tracker.py --by-day           # Breakdown by day
"""

import json
import os
import sys
import glob
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# Anthropic pricing (per token) — Claude Opus 4
PRICING = {
    "input": 15.0 / 1_000_000,      # $15/M input tokens
    "output": 75.0 / 1_000_000,     # $75/M output tokens  
    "cache_read": 1.875 / 1_000_000, # $1.875/M cache read
    "cache_write": 18.75 / 1_000_000, # $18.75/M cache write
}


def parse_session_file(filepath: Path) -> list:
    """Parse a session JSONL file and extract usage entries."""
    entries = []
    try:
        with open(filepath) as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    msg = data.get("message", {})
                    if isinstance(msg, dict):
                        usage = msg.get("usage")
                        if usage and isinstance(usage, dict):
                            ts = data.get("timestamp")
                            dt = None
                            if ts:
                                if isinstance(ts, str):
                                    try:
                                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
                                    except ValueError:
                                        pass
                                elif isinstance(ts, (int, float)):
                                    ts = float(ts)
                                    dt = datetime.fromtimestamp(ts / 1000 if ts > 1e10 else ts)
                            if not dt:
                                dt = datetime.now()
                            cost = usage.get("cost", {})
                            entries.append({
                                "timestamp": dt,
                                "date": dt.strftime("%Y-%m-%d"),
                                "session_file": filepath.stem,
                                "input_tokens": usage.get("input", 0),
                                "output_tokens": usage.get("output", 0),
                                "cache_read": usage.get("cacheRead", 0),
                                "cache_write": usage.get("cacheWrite", 0),
                                "total_tokens": usage.get("totalTokens", 0),
                                "cost_total": cost.get("total", 0),
                                "cost_input": cost.get("input", 0),
                                "cost_output": cost.get("output", 0),
                                "cost_cache_read": cost.get("cacheRead", 0),
                                "cost_cache_write": cost.get("cacheWrite", 0),
                            })
                except (json.JSONDecodeError, KeyError):
                    continue
    except (IOError, PermissionError):
        pass
    return entries


def aggregate(entries: list) -> dict:
    """Aggregate usage entries into totals."""
    totals = {
        "input_tokens": 0, "output_tokens": 0,
        "cache_read": 0, "cache_write": 0, "total_tokens": 0,
        "cost_total": 0, "cost_input": 0, "cost_output": 0,
        "cost_cache_read": 0, "cost_cache_write": 0,
        "num_calls": len(entries),
    }
    for e in entries:
        for k in totals:
            if k != "num_calls":
                totals[k] += e.get(k, 0)
    return totals


def format_cost(amount: float) -> str:
    if amount < 0.01:
        return f"${amount:.4f}"
    return f"${amount:.2f}"


def format_tokens(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def print_summary(totals: dict, label: str = "Summary"):
    print(f"\n{'═' * 50}")
    print(f"  Claude API Usage — {label}")
    print(f"{'═' * 50}")
    print(f"  API Calls:      {totals['num_calls']}")
    print(f"  Input Tokens:   {format_tokens(totals['input_tokens'])}")
    print(f"  Output Tokens:  {format_tokens(totals['output_tokens'])}")
    print(f"  Cache Read:     {format_tokens(totals['cache_read'])}")
    print(f"  Cache Write:    {format_tokens(totals['cache_write'])}")
    print(f"  Total Tokens:   {format_tokens(totals['total_tokens'])}")
    print(f"{'─' * 50}")
    print(f"  Cost (Input):       {format_cost(totals['cost_input'])}")
    print(f"  Cost (Output):      {format_cost(totals['cost_output'])}")
    print(f"  Cost (Cache Read):  {format_cost(totals['cost_cache_read'])}")
    print(f"  Cost (Cache Write): {format_cost(totals['cost_cache_write'])}")
    print(f"  TOTAL COST:         {format_cost(totals['cost_total'])}")
    print(f"{'═' * 50}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Claude API Usage Tracker")
    parser.add_argument("--days", type=int, default=1, help="Number of days to look back (default: 1 = today)")
    parser.add_argument("--all", action="store_true", help="All time usage")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--by-session", action="store_true", help="Breakdown by session")
    parser.add_argument("--by-day", action="store_true", help="Breakdown by day")
    args = parser.parse_args()

    # Collect all session files (active + deleted)
    jsonl_files = list(SESSIONS_DIR.glob("*.jsonl")) + list(SESSIONS_DIR.glob("*.jsonl.deleted.*"))
    
    if not jsonl_files:
        print("No session files found.")
        sys.exit(1)

    # Parse all
    all_entries = []
    for f in jsonl_files:
        all_entries.extend(parse_session_file(f))

    # Filter by time
    if not args.all:
        cutoff = datetime.now() - timedelta(days=args.days)
        all_entries = [e for e in all_entries if e["timestamp"] >= cutoff]

    if not all_entries:
        print("No usage data found for the specified period.")
        sys.exit(0)

    # Sort by timestamp
    all_entries.sort(key=lambda e: e["timestamp"])

    totals = aggregate(all_entries)
    period = "All Time" if args.all else f"Last {args.days} day(s)"

    if args.json:
        output = {
            "period": period,
            "from": all_entries[0]["date"] if all_entries else None,
            "to": all_entries[-1]["date"] if all_entries else None,
            **totals,
        }
        if args.by_day:
            by_day = defaultdict(list)
            for e in all_entries:
                by_day[e["date"]].append(e)
            output["by_day"] = {d: aggregate(es) for d, es in sorted(by_day.items())}
        print(json.dumps(output, indent=2, default=str))
    else:
        print_summary(totals, period)

        if args.by_day:
            by_day = defaultdict(list)
            for e in all_entries:
                by_day[e["date"]].append(e)
            print(f"{'Date':<12} {'Calls':>6} {'Tokens':>10} {'Cost':>10}")
            print(f"{'─' * 42}")
            for date, es in sorted(by_day.items()):
                day_totals = aggregate(es)
                print(f"{date:<12} {day_totals['num_calls']:>6} {format_tokens(day_totals['total_tokens']):>10} {format_cost(day_totals['cost_total']):>10}")

        if args.by_session:
            by_session = defaultdict(list)
            for e in all_entries:
                by_session[e["session_file"]].append(e)
            print(f"\n{'Session':<40} {'Calls':>6} {'Cost':>10}")
            print(f"{'─' * 58}")
            sorted_sessions = sorted(by_session.items(), key=lambda x: aggregate(x[1])["cost_total"], reverse=True)
            for session, es in sorted_sessions[:15]:
                s_totals = aggregate(es)
                print(f"{session[:38]:<40} {s_totals['num_calls']:>6} {format_cost(s_totals['cost_total']):>10}")


if __name__ == "__main__":
    main()
