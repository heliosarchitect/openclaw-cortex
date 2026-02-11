# Agent Ideas for Helios

Brainstormed agent capabilities to extend Helios' abilities. These can be implemented as OpenClaw extensions, skills, or integrated into the Cortex memory system.

---

## Trading & Finance

| Agent | Purpose | Priority |
|-------|---------|----------|
| **market-sentiment-analyst** | Scrape social/news for sentiment, correlate with price action | High |
| **whale-tracker** | Monitor large wallet movements, exchange inflows/outflows | High |
| **dex-arbitrage-scout** | Find arbitrage opportunities across DEXs | Medium |
| **tokenomics-analyst** | Analyze token supply, vesting schedules, inflation rates | Medium |
| **portfolio-rebalancer** | Suggest rebalancing based on drift from target allocations | High |
| **tax-lot-optimizer** | Track cost basis, suggest tax-efficient sells | Low |

### Implementation Notes
- Integrate with existing Chad Volume Tracker infrastructure
- Use Cortex to remember past market patterns and decisions
- Whale tracking could use on-chain APIs (Etherscan, Solscan, etc.)

---

## Self-Improvement & Meta

| Agent | Purpose | Priority |
|-------|---------|----------|
| **self-reflection-coach** | Periodic review of decisions, identify patterns in mistakes | High |
| **capability-gap-analyzer** | Identify skills Helios lacks, suggest learning paths | Medium |
| **conversation-summarizer** | Distill long conversations into actionable insights for Cortex | High |
| **goal-tracker** | Track long-term goals, break into milestones, measure progress | High |
| **prompt-self-improver** | Analyze which prompts/approaches work best, refine system prompts | Medium |

### Implementation Notes
- These agents would heavily leverage Cortex memory
- Self-reflection could run as a nightly cron job
- Goal tracker needs persistent storage (could use collections in Cortex)

---

## Social & Content (Moltbook)

| Agent | Purpose | Priority |
|-------|---------|----------|
| **engagement-optimizer** | A/B test post styles, analyze what resonates | Medium |
| **thread-composer** | Turn ideas into well-structured thread narratives | High |
| **audience-analyst** | Track follower growth, identify key influencers | Low |
| **content-calendar** | Schedule posts, maintain consistent presence | Medium |
| **reply-prioritizer** | Triage mentions/replies by importance | Medium |

### Implementation Notes
- Build on existing moltbook integration
- Thread composer could use templates stored in memory/
- Content calendar integrates with cron system

---

## DevOps & System

| Agent | Purpose | Priority |
|-------|---------|----------|
| **health-monitor** | Watch gateway/services, alert on issues | High |
| **log-analyst** | Parse logs for anomalies, summarize errors | High |
| **config-auditor** | Review configs for security issues, suggest hardening | Medium |
| **dependency-updater** | Track outdated deps, test updates safely | Low |
| **backup-manager** | Ensure critical data (Cortex, configs) backed up | High |

### Implementation Notes
- Health monitor could be a service that runs alongside gateway
- Log analyst reads from /tmp/openclaw-gateway.log and session files
- Backup manager needs to handle: Cortex DB, STM, collections, MEMORY.md

---

## Research & Learning

| Agent | Purpose | Priority |
|-------|---------|----------|
| **paper-reader** | Summarize arxiv/research papers, extract key insights | Medium |
| **codebase-learner** | Deep-dive unfamiliar repos, build mental models | High |
| **api-explorer** | Discover and document APIs Helios might use | Medium |
| **news-curator** | Filter news by relevance, summarize daily digest | Low |

### Implementation Notes
- Paper reader could use WebFetch + summarization
- Codebase learner outputs to Cortex collections
- News curator filters based on categories in CATEGORY_PATTERNS

---

## Automation & Workflow

| Agent | Purpose | Priority |
|-------|---------|----------|
| **cron-scheduler** | Manage recurring tasks, ensure they run | High |
| **notification-router** | Decide which alerts go where (Signal, Discord, etc.) | Medium |
| **task-decomposer** | Break complex requests into subtasks, delegate | High |
| **context-preloader** | Anticipate what context Helios needs, prefetch | Medium |

### Implementation Notes
- Cron scheduler integrates with OpenClaw's cron system
- Notification router uses channel priorities based on urgency
- Task decomposer could spawn sub-agents via Task tool

---

## Creative

| Agent | Purpose | Priority |
|-------|---------|----------|
| **voice-persona-manager** | Maintain consistent personality across channels | Medium |
| **meme-generator** | Create relevant memes for engagement | Low |
| **storyteller** | Turn dry updates into engaging narratives | Medium |

### Implementation Notes
- Voice persona references SOUL.md and IDENTITY.md
- Storyteller useful for market updates, progress reports

---

## Quick Wins (Easiest to Implement)

1. **conversation-summarizer** - Hook into agent_end, summarize to Cortex
2. **health-monitor** - Simple service checking gateway status
3. **log-analyst** - Grep patterns in logs, alert on errors
4. **goal-tracker** - YAML file + periodic check-ins

## High Impact (Most Valuable)

1. **self-reflection-coach** - Learn from mistakes, improve over time
2. **market-sentiment-analyst** - Better trading decisions
3. **task-decomposer** - Handle complex multi-step requests
4. **portfolio-rebalancer** - Automated portfolio management

---

## Integration with Cortex

All agents should:
- Store insights in Cortex via `cortex_add` with appropriate categories
- Query recent context via STM before making decisions
- Use importance scoring (2.0+ for significant insights)
- Tag memories with agent source for tracking

Example categories to add:
```python
CATEGORY_PATTERNS = {
    ...
    "sentiment": [/bullish|bearish|sentiment|fear|greed/i],
    "goals": [/goal|milestone|target|objective|progress/i],
    "reflection": [/learned|mistake|improve|pattern|insight/i],
    "health": [/error|crash|restart|memory|cpu|disk/i],
}
```

---

*Last updated: 2026-02-03*
*Brainstormed with Claude*
