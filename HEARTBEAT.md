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

## 📈 Trading Bot (PRIORITY)
Active trading on Coinbase. Bot is running: scalper_final.py

### Status
- Bot tracks P&L automatically via ETHBot portfolio API
- Monitors every 30 seconds
- Target: $2,492 → $2,550 → $100k

### DO NOT USE check_balance.py
- It has a bug (doesn't price ADA correctly)
- Use scalper_final.py logs instead or check via portfolio API

### Only alert if:
- Bot process dies
- Loss >$500 total
- Matthew asks for status

---

## 🌍 World Monitoring

### Earthquakes (USGS)
```bash
curl -s "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"features\"])} quakes 4.5+ in last hour') if d['features'] else print('All quiet')"
```
- Alert Matthew if 6.0+ anywhere
- Alert immediately if 8.0+

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
