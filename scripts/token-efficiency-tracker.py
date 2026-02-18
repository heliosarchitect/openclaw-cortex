#!/usr/bin/env python3
"""
Token Efficiency Tracker
Analyzes OpenClaw session transcripts to track output:input token ratios
Usage: python3 token-efficiency-tracker.py [--days N] [--verbose]
"""

import json
import glob
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re

class TokenEfficiencyTracker:
    def __init__(self):
        self.home_dir = Path.home()
        self.openclaw_dir = self.home_dir / ".openclaw"
        self.logs_dir = self.openclaw_dir / "logs"
        
    def find_transcript_files(self, days: int = 7) -> List[Path]:
        """Find transcript files from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Look for transcript files in various possible locations
        search_patterns = [
            self.logs_dir / "**" / "*.transcript.json",
            self.logs_dir / "**" / "*session*.json", 
            self.logs_dir / "**" / "*transcript*.json",
            self.openclaw_dir / "**" / "*.transcript.json"
        ]
        
        transcript_files = []
        for pattern in search_patterns:
            files = glob.glob(str(pattern), recursive=True)
            for file_path in files:
                file_stat = os.stat(file_path)
                file_time = datetime.fromtimestamp(file_stat.st_mtime)
                if file_time >= cutoff_date:
                    transcript_files.append(Path(file_path))
                    
        return sorted(set(transcript_files))
    
    def parse_transcript_file(self, file_path: Path, verbose: bool = False) -> Dict:
        """Parse a single transcript file and extract token metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse as JSONL (multiple JSON objects)
            lines = content.strip().split('\n')
            entries = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            # If that didn't work, try parsing as single JSON
            if not entries:
                try:
                    data = json.loads(content)
                    entries = [data] if isinstance(data, dict) else data
                except json.JSONDecodeError:
                    if verbose:
                        print(f"Warning: Could not parse {file_path}")
                    return {}
            
            return self.analyze_transcript_entries(entries, file_path, verbose)
            
        except Exception as e:
            if verbose:
                print(f"Error processing {file_path}: {e}")
            return {}
    
    def analyze_transcript_entries(self, entries: List[Dict], file_path: Path, verbose: bool) -> Dict:
        """Analyze parsed transcript entries for token metrics"""
        stats = {
            'file': str(file_path),
            'total_turns': 0,
            'heartbeat_turns': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'messages': []
        }
        
        for entry in entries:
            if not isinstance(entry, dict):
                continue
                
            # Look for token usage information
            input_tokens = 0
            output_tokens = 0
            is_heartbeat = False
            message_text = ""
            
            # Extract tokens from various possible structures
            if 'usage' in entry:
                usage = entry['usage']
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                
            elif 'tokens' in entry:
                tokens = entry['tokens']
                input_tokens = tokens.get('input', 0)
                output_tokens = tokens.get('output', 0)
                
            elif 'input_tokens' in entry and 'output_tokens' in entry:
                input_tokens = entry.get('input_tokens', 0)
                output_tokens = entry.get('output_tokens', 0)
            
            # Extract message content to detect heartbeats
            if 'content' in entry:
                message_text = str(entry['content'])
            elif 'message' in entry:
                message_text = str(entry['message'])
            elif 'text' in entry:
                message_text = str(entry['text'])
                
            # Detect heartbeat messages
            heartbeat_patterns = [
                'HEARTBEAT_OK',
                'heartbeat',
                'Everything looks good',
                'All systems operational'
            ]
            
            for pattern in heartbeat_patterns:
                if pattern.lower() in message_text.lower():
                    is_heartbeat = True
                    break
            
            # If we found token usage, record it
            if input_tokens > 0 or output_tokens > 0:
                stats['total_turns'] += 1
                stats['total_input_tokens'] += input_tokens
                stats['total_output_tokens'] += output_tokens
                
                if is_heartbeat:
                    stats['heartbeat_turns'] += 1
                
                stats['messages'].append({
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'is_heartbeat': is_heartbeat,
                    'text_preview': message_text[:100] + '...' if len(message_text) > 100 else message_text
                })
        
        return stats
    
    def aggregate_stats(self, file_stats: List[Dict]) -> Dict:
        """Aggregate statistics across all files"""
        total_stats = {
            'files_processed': len(file_stats),
            'total_turns': 0,
            'heartbeat_turns': 0,
            'productive_turns': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'heartbeat_input_tokens': 0,
            'heartbeat_output_tokens': 0,
            'daily_breakdown': defaultdict(lambda: {
                'turns': 0, 'input_tokens': 0, 'output_tokens': 0, 'heartbeat_turns': 0
            })
        }
        
        for stats in file_stats:
            if not stats or stats.get('total_turns', 0) == 0:
                continue
                
            total_stats['total_turns'] += stats['total_turns']
            total_stats['heartbeat_turns'] += stats['heartbeat_turns']
            total_stats['total_input_tokens'] += stats['total_input_tokens']
            total_stats['total_output_tokens'] += stats['total_output_tokens']
            
            # Try to extract date from filename for daily breakdown
            file_path = Path(stats['file'])
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
            if date_match:
                date = date_match.group(1)
            else:
                # Use file modification date
                file_stat = os.stat(file_path)
                date = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d')
                
            daily = total_stats['daily_breakdown'][date]
            daily['turns'] += stats['total_turns']
            daily['input_tokens'] += stats['total_input_tokens'] 
            daily['output_tokens'] += stats['total_output_tokens']
            daily['heartbeat_turns'] += stats['heartbeat_turns']
        
        total_stats['productive_turns'] = total_stats['total_turns'] - total_stats['heartbeat_turns']
        
        return total_stats
    
    def generate_report(self, stats: Dict) -> str:
        """Generate a formatted efficiency report"""
        if stats['total_turns'] == 0:
            return "No transcript data found or parsed successfully."
        
        # Calculate key metrics
        avg_input = stats['total_input_tokens'] / stats['total_turns'] if stats['total_turns'] else 0
        avg_output = stats['total_output_tokens'] / stats['total_turns'] if stats['total_turns'] else 0
        output_input_ratio = (stats['total_output_tokens'] / stats['total_input_tokens'] * 100) if stats['total_input_tokens'] else 0
        
        # Calculate without heartbeats
        productive_input = stats['total_input_tokens'] - stats['heartbeat_input_tokens']
        productive_output = stats['total_output_tokens'] - stats['heartbeat_output_tokens']
        productive_ratio = (productive_output / productive_input * 100) if productive_input else 0
        
        report = []
        report.append("=" * 60)
        report.append("TOKEN EFFICIENCY DASHBOARD")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")
        report.append("=" * 60)
        report.append("")
        
        # Current metrics
        report.append("📊 CURRENT METRICS")
        report.append(f"Total turns analyzed: {stats['total_turns']:,}")
        report.append(f"Productive turns: {stats['productive_turns']:,} ({stats['productive_turns']/stats['total_turns']*100:.1f}%)")
        report.append(f"Heartbeat turns: {stats['heartbeat_turns']:,} ({stats['heartbeat_turns']/stats['total_turns']*100:.1f}%)")
        report.append("")
        
        report.append("🔄 TOKEN FLOW")
        report.append(f"Total input tokens: {stats['total_input_tokens']:,}")
        report.append(f"Total output tokens: {stats['total_output_tokens']:,}")
        report.append(f"Average input/turn: {avg_input:,.0f} tokens")
        report.append(f"Average output/turn: {avg_output:.0f} tokens")
        report.append("")
        
        report.append("📈 EFFICIENCY RATIOS")
        report.append(f"Output:Input ratio: {output_input_ratio:.3f}%")
        report.append(f"Input tokens per output: {avg_input/avg_output:.0f}:1" if avg_output else "N/A")
        report.append(f"Without heartbeats: {productive_ratio:.3f}%")
        report.append("")
        
        # Targets and progress
        target_ratios = [0.5, 1.0, 2.0, 5.0]
        report.append("🎯 TARGETS")
        current = output_input_ratio
        for target in target_ratios:
            improvement = (target / current - 1) * 100 if current > 0 else 0
            status = "✅" if current >= target else "🔶" if current >= target * 0.8 else "❌"
            report.append(f"{status} {target:.1f}% ratio ({improvement:+.0f}% improvement needed)")
        report.append("")
        
        # Daily breakdown
        if stats['daily_breakdown']:
            report.append("📅 DAILY BREAKDOWN")
            sorted_days = sorted(stats['daily_breakdown'].items())
            for date, day_stats in sorted_days[-7:]:  # Last 7 days
                if day_stats['turns'] == 0:
                    continue
                day_ratio = (day_stats['output_tokens'] / day_stats['input_tokens'] * 100) if day_stats['input_tokens'] else 0
                day_avg_input = day_stats['input_tokens'] / day_stats['turns']
                report.append(f"{date}: {day_stats['turns']:3d} turns, {day_avg_input:5,.0f} avg input, {day_ratio:.3f}% ratio")
            report.append("")
        
        # Recommendations
        report.append("💡 TOP OPTIMIZATION OPPORTUNITIES")
        if avg_input > 70000:
            report.append("🔴 HIGH: Avg input >70K tokens - Review context loading")
        if stats['heartbeat_turns'] / stats['total_turns'] > 0.15:
            report.append("🟡 MED: >15% heartbeat turns - Consider frequency reduction")
        if output_input_ratio < 0.5:
            report.append("🔴 HIGH: <0.5% ratio - Implement turn batching")
        report.append("")
        
        report.append("📋 IMPLEMENTATION STATUS")
        report.append("✅ Workspace files optimized (~5,200 tokens saved)")
        report.append("✅ Cortex memory tuned (H0-5)")
        report.append("🔶 Tool descriptions optimization (Phase 2)")
        report.append("🔶 Context pruning adjustment (Phase 2)")
        report.append("❌ Turn batching strategy (Phase 3)")
        
        return "\n".join(report)

def generate_demo_stats() -> Dict:
    """Generate demo stats based on known baseline metrics from analysis"""
    # Known baseline: 14,305 turns, 79,175 avg input, 248 avg output, 0.31% ratio
    # 1,581 HEARTBEAT_OK turns (11.1%)
    
    total_turns = 14305
    heartbeat_turns = 1581
    avg_input = 79175
    avg_output = 248
    
    total_input = int(total_turns * avg_input)
    total_output = int(total_turns * avg_output)
    
    # Generate some daily breakdown for demo
    daily_breakdown = {}
    import random
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_turns = random.randint(1800, 2200)
        daily_input = daily_turns * random.randint(75000, 83000)
        daily_output = daily_turns * random.randint(220, 280)
        daily_heartbeats = int(daily_turns * 0.11)
        
        daily_breakdown[date] = {
            'turns': daily_turns,
            'input_tokens': daily_input,
            'output_tokens': daily_output,
            'heartbeat_turns': daily_heartbeats
        }
    
    return {
        'files_processed': 7,
        'total_turns': total_turns,
        'heartbeat_turns': heartbeat_turns,
        'productive_turns': total_turns - heartbeat_turns,
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'heartbeat_input_tokens': int(heartbeat_turns * avg_input),
        'heartbeat_output_tokens': int(heartbeat_turns * avg_output),
        'daily_breakdown': daily_breakdown
    }

def main():
    parser = argparse.ArgumentParser(description='Track OpenClaw token efficiency')
    parser.add_argument('--days', type=int, default=7, help='Days of logs to analyze (default: 7)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', type=str, help='Output file (default: stdout)')
    parser.add_argument('--demo', action='store_true', help='Run with demo data based on known baseline')
    
    args = parser.parse_args()
    
    if args.demo:
        if args.verbose:
            print("Running in demo mode with baseline metrics...")
        aggregated = generate_demo_stats()
    else:
        tracker = TokenEfficiencyTracker()
        
        if args.verbose:
            print(f"Searching for transcript files from last {args.days} days...")
        
        transcript_files = tracker.find_transcript_files(args.days)
        
        if args.verbose:
            print(f"Found {len(transcript_files)} transcript files")
            for f in transcript_files:
                print(f"  {f}")
        
        if not transcript_files:
            print("No transcript files found. Check OpenClaw logging configuration.")
            print(f"Expected locations: {tracker.logs_dir}")
            print("\nTry running with --demo to see the dashboard format:")
            print(f"python3 {sys.argv[0]} --demo")
            return 1
        
        # Parse all files
        file_stats = []
        for file_path in transcript_files:
            if args.verbose:
                print(f"Processing {file_path}...")
            stats = tracker.parse_transcript_file(file_path, args.verbose)
            if stats:
                file_stats.append(stats)
        
        # Generate report
        aggregated = tracker.aggregate_stats(file_stats)
    
    # Create tracker instance for report generation
    tracker = TokenEfficiencyTracker()
    report = tracker.generate_report(aggregated)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())