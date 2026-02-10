#!/bin/bash
# Post a task assigned to Matthew to #matthew-tasks on Discord
# Usage: post-matthew-task.sh <task_id>
# Or: post-matthew-task.sh --all (posts all open Matthew tasks)

set -euo pipefail
source ~/.secrets/discord.env

CHANNEL_ID="1470495480608985172"
DB="/home/bonsaihorn/Projects/lbf-dashboard/tasks.db"

post_task() {
    local task_id="$1"
    local row=$(python3 -c "
import sqlite3, json
conn = sqlite3.connect('$DB')
c = conn.cursor()
c.execute('''SELECT t.id, t.title, t.description, t.priority, t.pipeline_stage, p.name, pr.name, pr.emoji
  FROM tasks t 
  JOIN projects p ON t.project_id = p.id 
  JOIN programs pr ON p.program_id = pr.id 
  WHERE t.id = $task_id''')
r = c.fetchone()
if r:
    # Extract blocking info and type from description
    desc = r[2] or ''
    blocks = ''
    task_type = ''
    main_desc = desc
    for line in desc.split('\n'):
        if line.startswith('🚧 BLOCKS:'):
            blocks = line.replace('🚧 BLOCKS:', '').strip()
        elif line.startswith('🏷️ TYPE:'):
            task_type = line.replace('🏷️ TYPE:', '').strip()
        elif line.strip():
            pass
    # Clean main desc (remove metadata lines)
    main_lines = [l for l in desc.split('\n') if not l.startswith('🚧') and not l.startswith('🏷️') and l.strip()]
    main_desc = ' '.join(main_lines)[:300]
    
    print(json.dumps({
        'id': r[0], 'title': r[1], 'desc': main_desc,
        'priority': r[3], 'stage': r[4], 'project': r[5],
        'program': r[6], 'emoji': r[7],
        'blocks': blocks, 'type': task_type
    }))
conn.close()
")
    
    if [ -z "$row" ]; then
        echo "Task $task_id not found"
        return 1
    fi
    
    local title=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['title'])")
    local program=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['emoji'] + ' ' + d['program'])")
    local project=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['project'])")
    local priority=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['priority'].upper())")
    local desc=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['desc'])")
    local blocks=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['blocks'])")
    local task_type=$(echo "$row" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['type'])")
    
    local priority_icon="⚪"
    case "$priority" in
        HIGH) priority_icon="🔴" ;;
        MEDIUM) priority_icon="🟡" ;;
        LOW) priority_icon="🟢" ;;
        CRITICAL) priority_icon="🔥" ;;
    esac
    
    local msg="${priority_icon} **#${task_id}: ${title}**\n${program} → ${project}\n\n${desc}"
    
    if [ -n "$blocks" ] && [ "$blocks" != "" ]; then
        msg="${msg}\n\n🚧 **Blocks:** ${blocks}"
    fi
    if [ -n "$task_type" ] && [ "$task_type" != "" ]; then
        msg="${msg}\n🏷️ **Type:** ${task_type}"
    fi
    
    msg="${msg}\n\nReact ✅ when done."
    
    curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
        -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$(python3 -c "import json; print(json.dumps({'content': '''${msg}'''}))")" > /dev/null
    
    echo "Posted task #${task_id} to #matthew-tasks"
}

if [ "${1:-}" = "--all" ]; then
    task_ids=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$DB')
c = conn.cursor()
c.execute(\"SELECT id FROM tasks WHERE assigned_to = 'Matthew' AND pipeline_stage != 'done'\")
for r in c.fetchall(): print(r[0])
conn.close()
")
    for tid in $task_ids; do
        post_task "$tid"
    done
else
    post_task "${1:?Usage: post-matthew-task.sh <task_id|--all>}"
fi
