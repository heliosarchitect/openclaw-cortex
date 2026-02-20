# n8n Integration Documentation

## Overview
OpenClaw→n8n integration enables event-driven automation workflows. Events from OpenClaw systems trigger n8n workflows for notifications, monitoring, and complex automation chains.

## Architecture

```
OpenClaw Systems → Event Dispatcher → n8n Webhooks → Workflows → Actions
     ↑                    ↑                ↑            ↑         ↓
   Events             openclaw-event   Webhook Nodes  Processing  Notifications
                                                                   Integrations
                                                                   Alerts
```

## Event Types

### 1. Agent Events
- **agent-complete**: Agent session completions
- **agent-failure**: Agent session failures  
- **agent-timeout**: Agent sessions exceeding time limits

**Schema:**
```json
{
  "event": "agent-complete",
  "timestamp": "2026-02-16T15:16:00Z",
  "source": "openclaw",
  "data": {
    "session_id": "agent:main:subagent:abc123",
    "agent_type": "subagent",
    "duration": 45,
    "status": "success|failure|timeout",
    "task": "Brief task description",
    "error": "Error details (if failure)"
  }
}
```

### 2. System Events
- **system-alert**: Critical system issues
- **service-restart**: Service restart notifications
- **cron-failure**: Cron job failures
- **resource-usage**: High resource usage warnings

**Schema:**
```json
{
  "event": "system-alert", 
  "timestamp": "2026-02-16T15:16:00Z",
  "source": "openclaw",
  "data": {
    "service": "nginx|postgres|n8n|openclaw",
    "status": "up|down|degraded|restarting",
    "severity": "info|warning|critical|emergency", 
    "message": "Human-readable description",
    "metrics": {
      "cpu_usage": 85.2,
      "memory_usage": 78.5,
      "disk_usage": 45.3
    }
  }
}
```

### 3. Trading Events  
- **trading-signal**: AUGUR trading signals
- **position-update**: Position changes
- **risk-alert**: Risk management alerts

**Schema:**
```json
{
  "event": "trading-signal",
  "timestamp": "2026-02-16T15:16:00Z", 
  "source": "openclaw",
  "data": {
    "symbol": "BTC/USD",
    "signal": "buy|sell|hold",
    "confidence": 0.85,
    "price": 52000.0,
    "strategy": "V4.5.0",
    "metadata": {
      "indicators": ["RSI", "MACD", "Volume"],
      "timeframe": "4h"
    }
  }
}
```

### 4. Memory Events
- **memory-event**: Significant memory additions
- **insight-generated**: New insights from analysis
- **pattern-detected**: Pattern recognition events

**Schema:**
```json
{
  "event": "memory-event",
  "timestamp": "2026-02-16T15:16:00Z",
  "source": "openclaw", 
  "data": {
    "type": "cortex_add|atom_create|insight_generated",
    "importance": 2.5,
    "category": "trading|technical|personal",
    "content_preview": "First 100 chars of content...",
    "agent": "helios|claude-code|nova"
  }
}
```

### 5. External Events
- **model-update**: New AI models detected
- **github-release**: GitHub release notifications  
- **backup-complete**: Backup completion status

## Webhook Endpoints

n8n workflows should create webhook nodes at these URLs:

- `http://localhost:5678/webhook/openclaw/agent-complete`
- `http://localhost:5678/webhook/openclaw/system-alert`
- `http://localhost:5678/webhook/openclaw/trading-signal`
- `http://localhost:5678/webhook/openclaw/memory-event`
- `http://localhost:5678/webhook/openclaw/model-update`
- `http://localhost:5678/webhook/openclaw/cron-failure`
- `http://localhost:5678/webhook/openclaw/backup-complete`

### Authentication
Optional bearer token authentication via `N8N_WEBHOOK_TOKEN` environment variable.

## Event Dispatcher

### Usage
```bash
# Send a simple event
~/bin/openclaw-event "agent-complete" '{"session":"abc123","status":"success"}'

# Send system alert
~/bin/openclaw-event "system-alert" '{
  "service": "postgres",
  "status": "down", 
  "severity": "critical",
  "message": "Database connection lost"
}'

# Send trading signal
~/bin/openclaw-event "trading-signal" '{
  "symbol": "BTC/USD",
  "signal": "buy", 
  "confidence": 0.85,
  "price": 52000
}'
```

### Environment Variables
- `N8N_URL`: Base URL for n8n (default: http://localhost:5678)
- `N8N_WEBHOOK_TOKEN`: Optional authentication token
- `OPENCLAW_EVENT_LOG`: Log file path (default: /tmp/openclaw-events.log)

## Integration Points

### 1. Agent Completions
Modify session spawning to send completion events:
```bash
# In sessions_spawn wrapper
~/bin/openclaw-event "agent-complete" "{
  \"session_id\": \"$SESSION_ID\",
  \"duration\": $DURATION,
  \"status\": \"success\",
  \"task\": \"$TASK_DESCRIPTION\"
}"
```

### 2. SYNAPSE Messages
Hook into brain CLI to forward high-priority messages:
```bash
# In brain-qa-cron and similar scripts
~/bin/openclaw-event "system-alert" "{
  \"service\": \"brain-qa\",
  \"severity\": \"warning\",
  \"message\": \"QA tests failed\"
}"
```

### 3. AUGUR Signals
Integrate with augur signal generation:
```bash
# In AUGUR signal generation
~/bin/openclaw-event "trading-signal" "{
  \"symbol\": \"$SYMBOL\",
  \"signal\": \"$SIGNAL\",
  \"confidence\": $CONFIDENCE
}"
```

### 4. Memory Events  
Hook into cortex_add for high-importance memories:
```bash
# When importance > 2.0
~/bin/openclaw-event "memory-event" "{
  \"type\": \"cortex_add\",
  \"importance\": $IMPORTANCE,
  \"category\": \"$CATEGORY\"
}"
```

## n8n Workflow Templates

### 1. Agent Completion Notifications
**Trigger**: Webhook `/webhook/openclaw/agent-complete`
**Actions**:
- Filter for failures or long-running tasks
- Send notifications via Signal/Discord  
- Log to database
- Update task tracking systems

### 2. System Monitoring
**Trigger**: Webhook `/webhook/openclaw/system-alert`
**Actions**:
- Severity-based routing (critical → immediate alert)
- Auto-restart attempts for known issues
- Escalation chains (service → team lead → on-call)
- Integration with monitoring dashboards

### 3. Trading Signal Processing
**Trigger**: Webhook `/webhook/openclaw/trading-signal` 
**Actions**:
- Signal validation and filtering
- Risk management checks
- Forward to trading channels
- Performance tracking
- Backtesting integration

### 4. Backup and Maintenance
**Trigger**: Webhook `/webhook/openclaw/backup-complete`
**Actions**: 
- Verify backup integrity
- Update backup status dashboards
- Schedule cleanup of old backups
- Notify administrators of failures

## Testing

### 1. Test Event Dispatcher
```bash
# Test basic connectivity
~/bin/openclaw-event "test" '{"message":"hello world"}'

# Test with authentication
N8N_WEBHOOK_TOKEN="your-token" ~/bin/openclaw-event "test" '{}'

# Test failure handling
N8N_URL="http://invalid:9999" ~/bin/openclaw-event "test" '{}'
```

### 2. Test n8n Webhooks
```bash
# Direct webhook test
curl -X POST http://localhost:5678/webhook/openclaw/test \
  -H "Content-Type: application/json" \
  -d '{
    "event": "test",
    "timestamp": "2026-02-16T15:16:00Z",
    "source": "openclaw",
    "data": {"message": "test"}
  }'
```

### 3. End-to-End Testing
Create test workflows that:
- Receive each event type
- Log to files for verification
- Send test notifications
- Validate schema compliance

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check n8n is running: `ps aux | grep n8n`
   - Check port availability: `netstat -ln | grep 5678`
   - Check n8n logs: `journalctl -u n8n` (if systemd service)

2. **Webhook Not Found (404)**
   - Verify workflow is active in n8n
   - Check webhook URL path matches exactly
   - Ensure webhook node is properly configured

3. **Authentication Errors (401)**
   - Verify `N8N_WEBHOOK_TOKEN` is set correctly
   - Check n8n webhook authentication settings
   - Test without token first to isolate issue

4. **Timeout Errors**
   - Check n8n server health and load
   - Verify network connectivity
   - Consider increasing timeout in openclaw-event

### Monitoring

1. **Event Dispatcher Logs**
   ```bash
   tail -f /tmp/openclaw-events.log
   ```

2. **n8n Workflow Execution Logs**
   - Check n8n web interface execution history
   - Review workflow output and error logs

3. **Alert Consolidation**
   ```bash
   # Check if webhook failures create fallback alerts
   ls -la /tmp/helios-alerts/webhook-failure-alert
   ```

## Configuration Management

### Environment Setup
```bash
# Add to ~/.bashrc or system environment
export N8N_URL="http://localhost:5678"
export N8N_WEBHOOK_TOKEN="secure-random-token"
export OPENCLAW_EVENT_LOG="/var/log/openclaw-events.log"
```

### n8n Workflow Export/Import
1. Export workflows from n8n web interface
2. Save to `~/Projects/n8n-openclaw/workflows/` 
3. Version control workflow definitions
4. Import on new installations

### Backup Integration
Include n8n workflows in backup procedures:
```bash
# Add to helios-full-backup
n8n export:workflow --all --output=/backup/n8n-workflows.json
```

## Performance Considerations

1. **Event Rate Limiting**
   - Monitor event frequency to prevent overwhelming n8n
   - Implement batching for high-frequency events
   - Add circuit breaker for failing webhooks

2. **Webhook Timeout**
   - Default 10s timeout in openclaw-event
   - Consider async processing for long-running workflows
   - Monitor n8n workflow execution times

3. **Log Rotation**
   - Implement log rotation for `/tmp/openclaw-events.log`
   - Set up cleanup of old webhook response files
   - Monitor disk usage for log files

## Security

1. **Authentication**
   - Use webhook tokens for sensitive events
   - Consider IP filtering if n8n exposed externally
   - Rotate tokens regularly

2. **Data Sanitization**
   - Validate JSON input before sending
   - Strip sensitive data from logs
   - Consider encryption for sensitive payloads

3. **Network Security**
   - Keep n8n on private network if possible
   - Use HTTPS for external n8n instances
   - Monitor webhook access logs for anomalies