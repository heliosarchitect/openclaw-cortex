#!/usr/bin/env python3
"""
GitHub Release Monitor
Monitors GitHub repositories for new releases and tracks state.
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Default repositories to monitor
DEFAULT_REPOS = [
    "openclaw/openclaw",
    "n8n-io/n8n",
    "ansible/ansible",
    "hashicorp/terraform",
    "hashicorp/vault",
    "grafana/grafana",
    "prometheus/prometheus",
    "heliosarchitect/openclaw-cortex",
    "heliosarchitect/wems-mcp-server"
]

# Configuration
SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "releases_state.json"
CONFIG_FILE = SCRIPT_DIR / "config.json"
WATCH_INTERVAL = 3600  # 1 hour default


def load_config() -> Dict:
    """Load configuration from config file or create default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "repositories": DEFAULT_REPOS,
            "watch_interval": WATCH_INTERVAL
        }
        save_config(config)
    return config


def save_config(config: Dict) -> None:
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_state() -> Dict:
    """Load the last known state of releases."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state: Dict) -> None:
    """Save the current state of releases."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def run_gh_command(args: List[str]) -> Tuple[bool, str]:
    """Run a gh CLI command and return success status and output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def check_rate_limit() -> Tuple[int, int]:
    """Check GitHub API rate limit status."""
    success, output = run_gh_command(["api", "rate_limit"])
    if not success:
        print(f"Warning: Could not check rate limit: {output}", file=sys.stderr)
        return 0, 0
    
    try:
        rate_limit = json.loads(output)
        core = rate_limit.get("rate", {})
        remaining = core.get("remaining", 0)
        reset_time = core.get("reset", 0)
        return remaining, reset_time
    except json.JSONDecodeError:
        return 0, 0


def get_latest_release(repo: str) -> Optional[Dict]:
    """Get the latest release for a repository."""
    success, output = run_gh_command([
        "api", f"repos/{repo}/releases/latest",
        "--jq", '{"tag_name": .tag_name, "name": .name, "published_at": .published_at, "html_url": .html_url, "prerelease": .prerelease, "draft": .draft}'
    ])
    
    if not success:
        if "Not Found" in output:
            print(f"No releases found for {repo}")
            return None
        print(f"Error fetching release for {repo}: {output}", file=sys.stderr)
        return None
    
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error parsing release data for {repo}: {e}", file=sys.stderr)
        return None


def format_release_notification(repo: str, release: Dict) -> str:
    """Format a release for notification."""
    tag = release.get("tag_name", "Unknown")
    name = release.get("name", tag)
    published_at = release.get("published_at", "Unknown")
    url = release.get("html_url", "")
    prerelease = release.get("prerelease", False)
    draft = release.get("draft", False)
    
    # Parse and format the date
    try:
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        formatted_date = published_at
    
    release_type = ""
    if draft:
        release_type = " [DRAFT]"
    elif prerelease:
        release_type = " [PRERELEASE]"
    
    return f"🚀 New release: {repo} {tag}{release_type}\n📝 {name}\n📅 {formatted_date}\n🔗 {url}"


def check_for_new_releases(repos: List[str], verbose: bool = False) -> List[Tuple[str, Dict]]:
    """Check for new releases in the specified repositories."""
    state = load_state()
    new_releases = []
    
    # Check rate limit before starting
    remaining, reset_time = check_rate_limit()
    if remaining < len(repos) and remaining > 0:
        print(f"Warning: Low API rate limit ({remaining} remaining). Consider waiting.", file=sys.stderr)
    elif remaining == 0:
        reset_dt = datetime.fromtimestamp(reset_time)
        print(f"Error: API rate limit exceeded. Resets at {reset_dt}", file=sys.stderr)
        return new_releases
    
    for repo in repos:
        if verbose:
            print(f"Checking {repo}...")
        
        latest_release = get_latest_release(repo)
        if not latest_release:
            continue
        
        # Skip drafts for notifications (but track them in state)
        if latest_release.get("draft", False):
            if verbose:
                print(f"  Found draft release {latest_release.get('tag_name')} (skipping notification)")
            continue
        
        tag_name = latest_release.get("tag_name")
        last_seen = state.get(repo, {}).get("tag_name")
        
        if tag_name != last_seen:
            if verbose:
                print(f"  New release found: {tag_name} (was: {last_seen})")
            new_releases.append((repo, latest_release))
            
            # Update state
            state[repo] = {
                "tag_name": tag_name,
                "checked_at": datetime.now().isoformat()
            }
        elif verbose:
            print(f"  No new releases (latest: {tag_name})")
    
    # Save updated state
    save_state(state)
    
    return new_releases


def main():
    parser = argparse.ArgumentParser(description="Monitor GitHub repositories for new releases")
    parser.add_argument("--check", action="store_true", help="Run a one-time check for new releases")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor for new releases")
    parser.add_argument("--repos", nargs="+", help="Repositories to monitor (overrides config)")
    parser.add_argument("--interval", type=int, help="Watch interval in seconds (default from config)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--init", action="store_true", help="Initialize state with current releases (no notifications)")
    
    args = parser.parse_args()
    
    if not args.check and not args.watch and not args.init:
        parser.error("Must specify --check, --watch, or --init")
    
    # Load configuration
    config = load_config()
    repos = args.repos or config["repositories"]
    interval = args.interval or config["watch_interval"]
    
    if args.verbose:
        print(f"Monitoring {len(repos)} repositories:")
        for repo in repos:
            print(f"  - {repo}")
        print()
    
    if args.init:
        print("Initializing state with current releases...")
        state = {}
        for repo in repos:
            latest_release = get_latest_release(repo)
            if latest_release:
                state[repo] = {
                    "tag_name": latest_release.get("tag_name"),
                    "checked_at": datetime.now().isoformat()
                }
                print(f"  {repo}: {latest_release.get('tag_name')}")
        save_state(state)
        print("State initialized.")
        return
    
    if args.check:
        new_releases = check_for_new_releases(repos, args.verbose)
        
        if new_releases:
            print(f"Found {len(new_releases)} new release(s):")
            print()
            for repo, release in new_releases:
                print(format_release_notification(repo, release))
                print()
        else:
            if args.verbose:
                print("No new releases found.")
    
    elif args.watch:
        print(f"Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                if args.verbose:
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new releases...")
                
                new_releases = check_for_new_releases(repos, args.verbose)
                
                if new_releases:
                    print(f"\n🔔 Found {len(new_releases)} new release(s):")
                    print("=" * 50)
                    for repo, release in new_releases:
                        print(format_release_notification(repo, release))
                        print()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()