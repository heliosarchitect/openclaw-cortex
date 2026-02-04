# Common Cron Patterns

Quick reference for scheduling todos.

## Basic Patterns

| Pattern | Cron Expression | Description |
|---------|----------------|-------------|
| Every minute | `* * * * *` | Every 1 minute |
| Every 5 minutes | `*/5 * * * *` | Every 5 minutes |
| Every hour | `0 * * * *` | Top of every hour |
| Every 2 hours | `0 */2 * * *` | Every 2 hours |
| Daily at 9am | `0 9 * * *` | 9:00 AM every day |
| Weekdays at 9am | `0 9 * * 1-5` | Monday-Friday 9 AM |
| Weekly on Monday | `0 9 * * 1` | Monday 9 AM |
| Monthly on 1st | `0 9 1 * *` | 1st of month, 9 AM |

## Todo Tag Examples

### Time-based
```
- Check inbox @9am
- Team meeting @10:30am
- Deploy code @5pm
- Backup database @tomorrow
```

### Recurring
```
- Daily standup @9am #repeat:daily
- Weekly review @5pm #repeat:Mon-Fri
- Monthly report @1st #repeat:monthly
- Check logs @every-hour #repeat:hourly
```

### Dependencies
```
- Setup environment
- Install dependencies #depends:setup-environment
- Run tests #depends:install-dependencies
- Deploy #depends:run-tests
```

### Priority
```
- Critical fix #priority:high
- Documentation update #priority:low
- Code review #critical
```

## Schedule Presets

Use `--schedule` flag for common patterns:

```bash
# Every hour
python3 schedule_todos.py tasks.txt --schedule "0 * * * *"

# Weekday mornings
python3 schedule_todos.py tasks.txt --schedule "0 9 * * 1-5"

# Every 15 minutes
python3 schedule_todos.py tasks.txt --schedule "*/15 * * * *"
```

## Cron Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sun=0/7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

## Examples

**Morning routine** (sequential):
```
- Check email @9am
- Review PRs @9:30am
- Team standup @10am
```

**Data pipeline** (dependencies):
```
- Fetch data @9am
- Clean data #depends:fetch-data
- Run analysis #depends:clean-data
- Generate report #depends:run-analysis
```

**Recurring maintenance** (cron):
```
- Backup database @midnight #repeat:daily
- Clean logs @2am #repeat:daily
- Health check @every-hour #repeat:hourly
```
