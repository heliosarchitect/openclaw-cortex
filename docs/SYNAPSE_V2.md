# SYNAPSE Protocol V2 — Task Delegation with Expiry & Status Tracking

**Version:** 2.0  
**Author:** Helios AI  
**Date:** 2026-02-13  

## Overview

SYNAPSE V2 extends the existing inter-agent messaging protocol with structured task delegation capabilities. While preserving full backward compatibility with V1 messages, V2 adds task lifecycle management, expiry handling, and status tracking.

## Key Features

### 1. Task Delegation Lifecycle
- **Message Types**: "message" (default, V1 compatible) or "task" 
- **Status Flow**: pending → in_progress → completed/failed/expired/cancelled
- **Permission Model**: Only assigned agents can start/complete tasks, only delegators can cancel
- **Result Tracking**: Freeform result payload captured on completion/failure

### 2. Automatic Expiry
- **Lazy Expiry**: Tasks automatically expire when `expires_at` timestamp passes
- **Expiry Engine**: Triggered on every `get_inbox()` and `get_tasks()` call
- **Grace Handling**: Invalid expiry dates are safely ignored

### 3. Enhanced API
Four new functions complement the existing V1 API:
- `create_task()` - Create tasks with optional expiry
- `update_task_status()` - Transition task states with permission enforcement  
- `get_tasks()` - Query tasks with filtering
- `get_task()` - Retrieve single task by ID

## Architecture

### Data Model Extensions

V2 tasks extend V1 messages with additional fields:

```python
{
    # V1 fields (preserved)
    "id": "tsk_a1b2c3d4e5f6",
    "from": "helios", 
    "to": "claude-code",
    "priority": "action",
    "subject": "Build feature X",
    "body": "Detailed requirements...",
    "status": "unread",  # V1 message status
    "timestamp": "2026-02-13T06:00:00Z",
    # ... other V1 fields
    
    # V2 task extensions  
    "msg_type": "task",
    "assigned_to": "claude-code",
    "delegated_by": "helios", 
    "task_status": "pending",
    "result": null,
    "expires_at": "2026-02-14T06:00:00Z",
    "created_at": "2026-02-13T06:00:00Z",
    "started_at": null,
    "completed_at": null
}
```

### Status Transitions

```
    pending
    ├── in_progress (assigned agent only)
    ├── cancelled (delegator only) 
    └── expired (automatic)
    
    in_progress  
    ├── completed (assigned agent only)
    ├── failed (assigned agent only)
    └── expired (automatic)
    
    Terminal states: completed, failed, expired, cancelled
```

### Permission Matrix

| Transition | Who Can Execute |
|------------|----------------|
| pending → in_progress | assigned_to agent only |
| pending → cancelled | delegated_by agent only |
| in_progress → completed | assigned_to agent only |
| in_progress → failed | assigned_to agent only |
| any → expired | expiry engine only |

## Usage Examples

### Creating a Task
```python
import synapse_manager as sm

# Basic task
task = sm.create_task(
    from_agent="helios",
    to_agent="claude-code", 
    subject="Implement feature X",
    body="Build the authentication module",
    priority="action"
)

# Task with expiry (1 hour)
from datetime import datetime, timezone, timedelta
expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

urgent_task = sm.create_task(
    from_agent="helios",
    to_agent="claude-code",
    subject="Critical bug fix", 
    body="Fix the login issue ASAP",
    expires_at=expires,
    priority="urgent"
)
```

### Managing Task Status
```python
# Agent starts working on task
sm.update_task_status(task["id"], "claude-code", "in_progress")

# Complete with result
sm.update_task_status(
    task["id"], 
    "claude-code", 
    "completed", 
    "Authentication module implemented. Tests pass."
)

# Or fail with reason
sm.update_task_status(
    task["id"],
    "claude-code", 
    "failed",
    "Blocked on missing API credentials"
)

# Delegator cancels task
sm.update_task_status(task["id"], "helios", "cancelled", "No longer needed")
```

### Querying Tasks
```python
# Get all tasks for an agent (assigned or delegated)
my_tasks = sm.get_tasks("claude-code")

# Filter by status
pending_tasks = sm.get_tasks("claude-code", status_filter="pending")
in_progress = sm.get_tasks("claude-code", status_filter="in_progress")

# Include expired tasks
all_tasks = sm.get_tasks("claude-code", include_expired=True)

# Get specific task
task = sm.get_task("tsk_a1b2c3d4e5f6")
```

## Backward Compatibility

### Migration
- V1 synapse.json files are automatically migrated on load
- Existing messages get `msg_type: "message"` added
- Version number bumps from 1 to 2
- All V1 functions work unchanged

### Mixed Usage
```python
# V1 and V2 can coexist
message = sm.send_message("helios", "claude-code", "FYI", "Just letting you know")
task = sm.create_task("helios", "claude-code", "TODO", "Please do this")

# Both appear in inbox
inbox = sm.get_inbox("claude-code")  # Contains both message and task

# Only tasks in task queries
tasks = sm.get_tasks("claude-code")  # Contains only the task
```

## Error Handling

The API enforces business rules through exceptions:

```python
# Permission violations
try:
    sm.update_task_status(task_id, "wrong-agent", "in_progress")
except ValueError as e:
    print(f"Permission denied: {e}")

# Invalid transitions  
try:
    sm.update_task_status(task_id, "claude-code", "completed")  # skip in_progress
except ValueError as e:
    print(f"Invalid transition: {e}")

# Terminal state protection
try:
    sm.update_task_status(completed_task_id, "claude-code", "failed")
except ValueError as e:
    print(f"Cannot modify completed task: {e}")
```

## Performance Characteristics

- **Lazy Expiry**: O(n) scan of tasks only when needed
- **Atomic Writes**: tmp+rename pattern prevents corruption
- **Memory Footprint**: In-memory operations, file persistence
- **Pruning**: Maintains 200 message cap, preserves unread items

## Testing

V2 includes comprehensive test coverage (32 tests):
- Task creation and lifecycle management
- Status transition validation  
- Permission enforcement
- Expiry engine behavior
- Backward compatibility
- Data integrity and edge cases

Run tests: `python3 -m pytest test_synapse_v2.py -v`

## Implementation Notes

### Thread Safety
- File-based storage with atomic writes
- No explicit locking (relies on filesystem atomicity)
- Suitable for single-process multi-thread usage

### Extensibility  
- Message schema allows future field additions
- Status transitions can be extended
- Permission model can be refined

### Integration Points
- Works with existing Cortex memory system
- Compatible with OpenClaw agent framework
- Suitable for n8n workflow integration

## Migration Guide

Existing V1 installations automatically upgrade:

1. **File Migration**: V1 synapse.json files gain `msg_type` fields
2. **API Compatibility**: All V1 functions remain unchanged  
3. **New Capabilities**: V2 task functions available immediately
4. **Zero Downtime**: Migration happens transparently on first load

## Future Enhancements

Potential V3 features:
- Task dependencies and DAG execution
- Recurring/scheduled tasks
- Task templates and workflows
- Integration with external task systems
- Advanced querying and reporting