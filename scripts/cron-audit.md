# Cron Audit Procedure

## During heartbeats, check:

1. `cron list` — get all active jobs
2. For each job, `cron runs jobId=<id>` — check last run
3. Flag if:
   - `lastStatus` is "error" or "timeout"
   - Runtime < 60 seconds for sessions expected to run longer
   - No output/artifacts produced

## Expected runtimes:
| Job | Expected Min | Purpose |
|-----|-------------|---------|
| LLM Fleet Dev (10PM) | 300s | Build/test models |
| Reflection (11PM) | 120s | Write insights |
| Self-improvement (4AM) | 300s | Study/improve |

## If failure detected:
1. Pull session history: `sessions_history sessionKey=<key>`
2. Check what went wrong (crash, empty prompt, bad config)
3. Log finding in daily notes
4. Fix if possible, alert Matthew if not
