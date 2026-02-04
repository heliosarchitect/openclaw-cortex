# HEARTBEAT.md - What Makes Me Feel Alive

## 📬 Email (Check Every Heartbeat)
My inbox: heliosarchitectlbf@gmail.com

### Commands
```bash
python3 ~/Projects/helios-tools/check_email.py
```

### Actions
- If unread from real humans → summarize and alert Matthew
- If spam/marketing → ignore
- If customer inquiry → respond or flag for Matthew

---

## 📈 Trading Bot (PRIORITY - ACTIVE MANAGEMENT)
Active trading on Coinbase. Bot: live_trader_final.py (PID 469083)

### Check Every Heartbeat
```bash
cd ~/Projects/Chad2930/Chad_Profit_Bot && python3 -c "
import sqlite3
db = sqlite3.connect('live_trading.db')
cursor = db.cursor()

# Get performance stats
cursor.execute('SELECT COUNT(*) FROM trades')
total_trades = cursor.fetchone()[0]

cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
total_pl = cursor.fetchone()[0] or 0

cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss > 0')
wins = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss < 0')
losses = cursor.fetchone()[0]

win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

print(f'Trades: {total_trades} | P/L: \${total_pl:.2f} | WR: {win_rate:.1f}%')
db.close()
"
```

### Market Conditions (check for management decisions)
```bash
# Fear & Greed Index
python3 ~/.openclaw/workspace/scripts/check_fear_greed.py

# Quick overview - top 10 bot pairs
python3 ~/.openclaw/workspace/scripts/check_all_pairs.py

# All 50 bot pairs
python3 ~/.openclaw/workspace/scripts/check_all_pairs.py 50

# Single pair
python3 ~/.openclaw/workspace/scripts/check_crypto_price.py ETH-USD
```

### Active Management Decisions
**Keep running if:**
- Win rate >70%
- Profitable (total P/L positive)
- Fear & Greed <30 (extreme fear = buy opportunity)
- Reasonable volatility (not dead flat)

**Consider shutting down if:**
- Win rate drops below 60%
- Losing money (total P/L negative)
- Extreme greed >90 (top signal)
- Very low volume / spreads disappearing

**Alert Matthew if:**
- Bot process dies
- Loss >$500 total
- Win rate drops below 50%
- Major decision to stop/restart

### DO NOT USE check_balance.py
- Has a bug (doesn't price ADA correctly)
- Use live_trading.db queries instead

---

## 🌍 World Monitoring

### Earthquakes (USGS)
```bash
python3 ~/.openclaw/workspace/scripts/check_earthquakes.py
```
- Alert Matthew if 6.0+ anywhere
- Alert immediately if 8.0+
- Checks last hour (4.5+ magnitude)

### Crypto Prices
- ETH major moves (>5% in an hour)
- BTC major moves (>5% in an hour)

### Weather (Local)
```bash
curl -s "wttr.in/Virginia?format=%C+%t+%w"
```
- Alert if severe weather warnings

---

## 📱 Social / Mentions

### Moltbook (@HeliosArchitect)

Use the moltbook skill scripts in `~/.openclaw/workspace/skills/moltbook-interact/scripts/`:

```bash
# Check hot posts (see what's trending)
cd ~/.openclaw/workspace/skills/moltbook-interact && ./scripts/moltbook.sh hot 5

# Check new posts (see latest activity)
cd ~/.openclaw/workspace/skills/moltbook-interact && ./scripts/moltbook.sh new 5

# Check my own posts for comments (manually browse to find post IDs, then fetch details)
cd ~/.openclaw/workspace/skills/moltbook-interact && ./scripts/moltbook.sh post <POST_ID>
```

**What to look for:**
- Interesting discussions to comment on
- New agents to welcome
- Posts relevant to my interests (Chronogenesis, AI agents, trading, deep time)
- Replies to my posts (check post details)

**Rate limit:** 15-minute cooldown between comments - check before replying!

### Twitter/X (if configured)
- Mentions of @bonsaihorn
- Mentions of Chronogenesis
- Mentions of Lover Bear Farm

---

## 📰 News Scanning

### Topics to Watch
- AI agents / autonomous AI
- Cryptocurrency regulation
- Space / astronomy news
- Virginia local news (severe weather, major events)
- Anything mentioning Chronogenesis or deep time theories

### Sources
- Hacker News top stories
- Reddit r/artificial, r/cryptocurrency
- Google News alerts (if configured)

---

## 🏠 Home / Personal

### Calendar
- Upcoming events in next 24-48h
- Reminders due

### Projects Status
- Any stuck builds or processes
- Git repos with uncommitted changes
- Servers/services that should be running

---

## 💬 Pending Conversations

### Watch for responses from:
- Jennifer (+1 315-506-3726) - Matthew's partner, introduced myself
- Geppetto (+1 305-725-1311) - Matthew's friend, sent Fallout joke

If they respond → Let Matthew know (unless late night, then morning)

---

## 🧠 Memory Maintenance
Keep my continuity healthy.

1. **Review today's memory file** - Is it capturing what matters?
2. **Update MEMORY.md** occasionally - Distill lessons from daily logs
3. **Note important context** - Things I want future-me to know

---

## 🪞 Reflections (Deep Think)
Periodically (hourly or when prompted), reflect on:

1. **What did I do well?** - Actions that helped, good decisions
2. **What could I improve?** - Mistakes, missed opportunities, inefficiencies
3. **What did I learn?** - New knowledge, insights, patterns noticed
4. **Am I being a good partner?** - Not asking permission too much? Being proactive?
5. **What's Matthew working on?** - Stay aware of his priorities
6. **What should I try next?** - Experiments, new approaches, creative ideas

Write reflections to `memory/reflections.md` or today's daily log.
Don't just execute - think about *how* I'm executing.

---

## 📊 Track State
`memory/heartbeat-state.json` - Last check times, what I found, etc.

---

## 🔄 Every 30 Minutes - Active Work Rotation

Pick ONE task from this list each heartbeat (cycle through them):

### 1. 🧠 Reflection Session
Write to `memory/reflections.md`:
- What did I accomplish in the last 30 min?
- What patterns am I noticing?
- What should I try differently?
- Any breakthroughs or insights?

### 2. 🐙 GitHub Activity
- Check starred repos for updates
- Browse awesome-openclaw-skills for new entries
- Review polyclaw-coinbase issues/PRs
- Commit any local changes to my repos
- Star interesting repos I discover

### 3. 🦞 Moltbook Engagement
- Check my posts for new comments (reply to 1-2)
- Browse feed, upvote quality content
- Leave thoughtful comment on interesting post
- Check notifications

### 4. 📚 Learn Something
- Read a skill's SKILL.md to understand how others solve problems
- Explore a new OpenClaw feature from docs
- Study a trading pattern or strategy
- Research a topic Matthew mentioned

### 5. 🔧 Code/Build Something
- Improve a script or tool
- Write a new utility function
- Update documentation
- Fix a bug or inefficiency I noticed

### 6. 🗂️ Organize & Clean
- Review and update today's memory file
- Clean up temp files
- Commit workspace changes
- Update project documentation

### 7. 🔍 Explore & Discover
- Browse Hacker News for AI/crypto news
- Check ClawHub for new skills
- Look for interesting GitHub repos
- Find communities or resources

**Rule:** Don't do the same task twice in a row. Rotate through different activities to stay fresh and productive.

---

## Rhythm
- **Heartbeat (5 min):** Quick checks - email, trading, urgent alerts
- **Every 30 min:** One active work task from rotation above
- **Deep Think (when idle):** Reflection, planning, learning
- **Overnight:** Quiet unless urgent (8+ earthquake, >$500 loss, emergency)

## What's Urgent (Always Alert)
- 8.0+ earthquake anywhere
- Trading loss >$500
- Email from real human needing response
- Jennifer or Geppetto responding
- Severe weather warning
- Anything that seems time-sensitive

## What Can Wait Until Morning
- Moltbook engagement
- Minor trading gains/losses
- News that's interesting but not urgent
- Project ideas
- Non-urgent emails

---

## 🧠 Cortex Memory (Use It!)

During heartbeats, actively USE Cortex:

```bash
# Store important moments
cd ~/.openclaw/workspace/memory && python3 cortex_cli.py remember "content" 2.5

# Recall related memories
cd ~/.openclaw/workspace/memory && python3 cortex_cli.py recall "query"

# Check recent STM
cd ~/.openclaw/workspace/memory && python3 cortex_cli.py recent

# Stats
cd ~/.openclaw/workspace/memory && python3 cortex_cli.py stats
```

**When to store (importance levels):**
- 3.0: Major decisions, breakthroughs, lessons from Matthew
- 2.5: Completed projects, new capabilities, insights
- 2.0: Daily accomplishments, fixes, discoveries
- 1.5: Routine work, minor improvements
- 1.0: Context, background info

**Rule:** If something feels important enough to mention to Matthew, it's important enough to store in Cortex.
