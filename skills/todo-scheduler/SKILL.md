---
name: todo-scheduler
description: Generate cron jobs from a todo list. Use when you need to automate task execution via scheduled jobs - turn a checklist into automated work.
---

# Todo Scheduler

Transform a todo list into automated cron jobs that execute each task at the right time.

## When to Use

- Turn a task list into scheduled execution
- Automate multi-step projects
- Set up recurring workflows
- Build "complete by X date" automation

## Quick Start

```bash
# From a todo file
cd ~/.openclaw/workspace/skills/todo-scheduler/scripts
python3 schedule_todos.py ~/path/to/todos.txt

# Inline
python3 schedule_todos.py --inline "Check email, Update docs, Deploy code"

# With schedule
python3 schedule_todos.py todos.txt --schedule "every 2 hours"
```

## Todo Format

**Simple list** (auto-scheduled):
```
- Check email
- Update documentation
- Deploy to production
```

**With metadata** (scheduled, dependencies, priority):
```
- [ ] Setup database @9am #critical
- [ ] Load data @10am #depends:setup-database
- [ ] Run analysis @11am #priority:high
- [ ] Generate report @12pm #depends:run-analysis
```

**Tags:**
- `@TIME` - When to run (e.g., `@9am`, `@14:30`, `@tomorrow`)
- `#depends:task-id` - Wait for another task to complete
- `#priority:high|medium|low` - Execution priority
- `#repeat:SCHEDULE` - Recurring (e.g., `#repeat:daily`, `#repeat:Mon-Fri-9am`)

## How It Works

1. **Parse** - Extract tasks, times, dependencies
2. **Schedule** - Generate cron expressions for each
3. **Create Jobs** - Use OpenClaw cron API to install
4. **Track** - Monitor completion and dependencies

## Script Reference

### schedule_todos.py

Main scheduler - parses todos and creates cron jobs.

**Args:**
- `FILE` - Path to todo file
- `--inline TEXT` - Inline comma-separated tasks
- `--schedule CRON` - Default schedule for all tasks
- `--start TIME` - Start time (default: now)
- `--spacing MINUTES` - Minutes between tasks (default: 30)
- `--dry-run` - Show jobs without creating

**Output:**
- Created job IDs
- Schedule summary
- Dependency graph

### Examples

**Sequential execution** (30 min apart, starting now):
```bash
python3 schedule_todos.py tasks.txt
```

**Spread across day** (9am-5pm):
```bash
python3 schedule_todos.py tasks.txt --start 9am --spacing 60
```

**All at specific time:**
```bash
python3 schedule_todos.py tasks.txt --schedule "0 9 * * *"
```

**Recurring daily tasks:**
```bash
cat > daily.txt << 'EOF'
- Check inbox @9am #repeat:daily
- Team standup @10am #repeat:Mon-Fri
- Status report @5pm #repeat:daily
EOF

python3 schedule_todos.py daily.txt
```

## Advanced

### Dependency Chains

Tasks with `#depends:` wait for their prerequisite to complete:

```
- [ ] fetch-data @9am
- [ ] clean-data @9:30 #depends:fetch-data
- [ ] analyze @10am #depends:clean-data
- [ ] report @11am #depends:analyze
```

Scheduler creates wake events to trigger next task when dependency completes.

### Conditional Execution

Use `#if:CONDITION` for conditional runs:

```
- [ ] Deploy #if:tests-pass
- [ ] Rollback #if:deploy-fail
```

Conditions checked via exit codes or file presence.

### Parallel Groups

Use `#group:NAME` to run tasks in parallel:

```
- [ ] Download A #group:downloads
- [ ] Download B #group:downloads
- [ ] Download C #group:downloads
- [ ] Process all #depends:downloads
```

All tasks in group must complete before dependents run.

## Tips

**Start simple:** Begin with time-based tasks, add dependencies as needed.

**Use dry-run:** Always preview with `--dry-run` before installing jobs.

**Check status:** `cron status` shows all active jobs.

**Clean up:** Remove completed one-shot jobs with `cron remove JOB_ID`.

## See Also

- `cron` tool - OpenClaw job scheduler
- `references/cron-patterns.md` - Common scheduling patterns
- `references/wake-events.md` - Inter-job communication
