#!/usr/bin/env python3
"""
End of day routine - commit changes, reflect, update memory.
Run daily at 11:00 PM via cron.
"""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'

def get_today_commits():
    """Get today's commits from workspace repo"""
    os.chdir(WORKSPACE)
    today = datetime.now().strftime('%Y-%m-%d')
    
    result = subprocess.run(
        ['git', 'log', '--since', today, '--oneline', '--no-merges'],
        capture_output=True, text=True
    )
    
    commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
    return commits

def read_reflections():
    """Read today's reflections if they exist"""
    reflections_file = WORKSPACE / 'memory' / 'reflections.md'
    if reflections_file.exists():
        return reflections_file.read_text()
    return None

def commit_workspace():
    """Commit any uncommitted changes"""
    os.chdir(WORKSPACE)
    
    # Check if there are changes
    result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
    if not result.stdout.strip():
        return "No uncommitted changes"
    
    # Add and commit
    subprocess.run(['git', 'add', '-A'])
    subprocess.run(['git', 'commit', '-m', f'chore: end of day auto-commit {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
    
    return f"Committed: {len(result.stdout.strip().split(chr(10)))} files changed"

def generate_reflection_summary():
    """Generate end-of-day reflection summary"""
    commits = get_today_commits()
    reflections = read_reflections()
    
    summary = []
    summary.append(f"END OF DAY REFLECTION - {datetime.now().strftime('%B %d, %Y')}")
    summary.append("=" * 60)
    summary.append("")
    
    # What I built today
    summary.append("📦 WHAT I BUILT:")
    if commits:
        for commit in commits[:15]:  # Limit to 15
            summary.append(f"  • {commit}")
    else:
        summary.append("  (no commits today)")
    summary.append("")
    
    # Reflections (if any)
    if reflections:
        summary.append("🧠 REFLECTIONS & INSIGHTS:")
        # Extract key sections from reflections.md
        lines = reflections.split('\n')
        in_today_section = False
        for line in lines:
            if datetime.now().strftime('%B %d') in line or datetime.now().strftime('%Y-%m-%d') in line:
                in_today_section = True
            if in_today_section:
                if line.startswith('#'):
                    summary.append(f"\n{line}")
                elif line.strip() and not line.startswith('---'):
                    summary.append(f"  {line}")
                if line.startswith('---') and in_today_section and summary[-1] != "🧠 REFLECTIONS & INSIGHTS:":
                    break
    else:
        summary.append("🧠 REFLECTIONS:")
        summary.append("  (no reflections captured today)")
    
    summary.append("")
    summary.append("=" * 60)
    
    return '\n'.join(summary)

def save_daily_log():
    """Save today's activity to daily log"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = WORKSPACE / 'memory' / f'{today}.md'
    
    if not log_file.exists():
        # Create basic daily log
        commits = get_today_commits()
        content = [
            f"# Daily Log - {datetime.now().strftime('%B %d, %Y')}",
            "",
            "## Commits",
        ]
        for commit in commits:
            content.append(f"- {commit}")
        
        log_file.write_text('\n'.join(content))
        return f"Created {log_file.name}"
    
    return f"Daily log already exists: {log_file.name}"

def main():
    print(f"🌙 End of Day Routine - {datetime.now().strftime('%I:%M %p')}")
    print()
    
    # 1. Commit workspace changes
    print("1. Committing workspace changes...")
    commit_result = commit_workspace()
    print(f"   {commit_result}")
    print()
    
    # 2. Save daily log
    print("2. Updating daily log...")
    log_result = save_daily_log()
    print(f"   {log_result}")
    print()
    
    # 3. Generate reflection summary
    print("3. Generating reflection summary...")
    reflection = generate_reflection_summary()
    print(reflection)
    print()
    
    # 4. Store summary in Cortex
    print("4. Storing in Cortex...")
    try:
        os.chdir(WORKSPACE / 'memory')
        summary_text = f"End of day {datetime.now().strftime('%Y-%m-%d')}: {len(get_today_commits())} commits. Captured daily reflections and insights."
        subprocess.run(['python3', 'cortex_cli.py', 'remember', summary_text, '2.0'])
        print("   ✅ Stored in Cortex")
    except Exception as e:
        print(f"   ⚠️ Cortex storage failed: {e}")
    
    print()
    print("✅ End of day routine complete")

if __name__ == '__main__':
    main()
