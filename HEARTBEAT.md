# HEARTBEAT.md

**Default mode: BUILD.** Pull from `memory/task-queue.md`. Never idle >2 consecutive HEARTBEAT_OKs.

## Priority Order
1. Matthew messages → respond immediately
2. Something breaks → fix it
3. Everything green → BUILD (dispatch Nova tasks)

## Every Heartbeat
- Run `session_status` → if context > 75%, message Matthew: "⚠️ Context at X% — /new soon"
- Check `sessions_list` for failed sub-agents (<60s runs, no tool calls)
- Check synapse inbox: `~/bin/brain inbox --agent helios`
- Check GitHub CI: `~/bin/check-github-ci` → if failures, fix immediately
- If failures found: investigate and log

## Don't Poll
CPU temp, same emails repeatedly, earthquake feed, AUGUR health (self-monitoring). If checking same thing with no change → STOP and BUILD.
