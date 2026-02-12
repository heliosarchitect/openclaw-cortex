#!/usr/bin/env python3
"""Send a message to synapse.json"""
import json, datetime, uuid, sys

SYNAPSE = "/home/bonsaihorn/.openclaw/workspace/memory/synapse.json"

body = sys.stdin.read()

with open(SYNAPSE, 'r') as f:
    data = json.load(f)

msg = {
    'id': 'syn_' + uuid.uuid4().hex[:12],
    'from': 'helios',
    'to': 'claude-code',
    'priority': sys.argv[1] if len(sys.argv) > 1 else 'normal',
    'subject': sys.argv[2] if len(sys.argv) > 2 else 'Message from Helios',
    'body': body,
    'status': 'sent',
    'timestamp': datetime.datetime.now().isoformat(),
    'read_by': [],
    'thread_id': sys.argv[3] if len(sys.argv) > 3 else None,
    'ack_body': None
}

data['messages'].append(msg)

with open(SYNAPSE, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Sent: {msg['id']}")
