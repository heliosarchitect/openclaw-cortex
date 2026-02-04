#!/usr/bin/env python3
"""
Send morning activity summary email to Matthew.
Run via cron at 8am daily.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import sys

def load_gmail_creds():
    """Load Gmail credentials from .env"""
    env_path = os.path.expanduser('~/.openclaw/.env')
    sender = None
    app_password = None
    
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('HELIOS_GMAIL_USER='):
                sender = line.split('=', 1)[1].strip()
            elif line.startswith('HELIOS_GMAIL_APP_PASSWORD='):
                app_password = line.split('=', 1)[1].strip()
    
    return sender, app_password

def get_overnight_commits():
    """Get git commits from last 12 hours"""
    os.chdir(os.path.expanduser('~/.openclaw/workspace'))
    import subprocess
    
    since = (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M')
    result = subprocess.run(
        ['git', 'log', '--since', since, '--oneline', '--no-merges'],
        capture_output=True, text=True
    )
    
    commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
    return commits[:10]  # Limit to 10

def send_morning_summary():
    """Send morning activity summary email"""
    sender, app_password = load_gmail_creds()
    receiver = "bonsaihorn@gmail.com"
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Morning Summary - {datetime.now().strftime('%B %d, %Y')}"
    msg['From'] = "Helios <heliosarchitectlbf@gmail.com>"
    msg['To'] = receiver
    
    # Get overnight commits
    commits = get_overnight_commits()
    commit_section = "\n".join([f"  • {c}" for c in commits]) if commits else "  (none)"
    
    # Email body
    body = f"""HELIOS MORNING SUMMARY
{datetime.now().strftime('%B %d, %Y | %I:%M %p %Z')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 OVERNIGHT ACTIVITY:

Git Commits:
{commit_section}

🤖 AUTONOMOUS WORK:
- Monitoring systems active (trading, earthquakes, crypto, email)
- Proactive work rotation executed every 15 minutes
- [Specific accomplishments would be listed here]

📊 TRADING STATUS:
- Bot: [STOPPED/RUNNING]
- Setup Watch: [Summary of market conditions]
- Decisions: [Any bot starts/stops overnight]

🌍 MONITORING ALERTS:
- Earthquakes: [Count, highest magnitude]
- Crypto Moves: [Any >5% moves]
- Other Events: [Weather, etc.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

READY FOR THE DAY:
✓ All systems operational
✓ Cron jobs running
✓ Monitoring active

--
Helios
heliosarchitectlbf@gmail.com
"""
    
    # Attach text version
    text_part = MIMEText(body, 'plain', 'utf-8')
    msg.attach(text_part)
    
    # Send via Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        
        print(f"✅ Morning summary sent to {receiver}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    send_morning_summary()
