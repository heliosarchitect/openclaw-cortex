# LBF Discord Server Setup Guide for OpenClaw Integration

## Overview
This guide covers the complete setup of a Discord server for LBF's OpenClaw integration, including server structure, bot configuration, permissions, and automated alerts.

## 1. Server Structure

### Required Channels

#### **#general**
- **Purpose**: General team discussion and announcements
- **Permissions**: All members can read/write
- **Type**: Text channel

#### **#augur-signals** 
- **Purpose**: Real-time AUGUR trading signals and alerts
- **Permissions**: OpenClaw bot write-only, team read-only
- **Type**: Text channel
- **Webhook**: Required for automated signal posting

#### **#augur-reports**
- **Purpose**: Daily/weekly AUGUR performance reports and analytics  
- **Permissions**: OpenClaw bot write-only, team read-only
- **Type**: Text channel
- **Webhook**: Required for automated report delivery

#### **#helios-logs**
- **Purpose**: System logs and debug information from Helios AI
- **Permissions**: OpenClaw bot write-only, admin/dev read-only
- **Type**: Text channel
- **Webhook**: Required for log streaming

#### **#infrastructure**
- **Purpose**: Server status, deployment notifications, system alerts
- **Permissions**: OpenClaw bot write-only, admin read-only
- **Type**: Text channel  
- **Webhook**: Required for automated infrastructure alerts

#### **#dev**
- **Purpose**: Development discussion, code reviews, technical coordination
- **Permissions**: Developers read/write, others read-only
- **Type**: Text channel

### Channel Categories (Optional)
```
📊 TRADING
├── #augur-signals
├── #augur-reports
└── #trading-discussion

🤖 AUTOMATION  
├── #helios-logs
├── #infrastructure
└── #bot-commands

💬 GENERAL
├── #general
└── #dev
```

## 2. Bot Permissions Requirements

### OpenClaw Bot Required Permissions

#### Server Permissions
- **View Channels**: Essential for channel access
- **Send Messages**: Required for posting alerts/reports
- **Embed Links**: For rich content in reports  
- **Attach Files**: For log files and report attachments
- **Read Message History**: For context awareness
- **Use External Emojis**: For enhanced visual feedback
- **Manage Webhooks**: For webhook creation/management

#### Per-Channel Permissions Override
```
#augur-signals:
  - Send Messages: ✓
  - Embed Links: ✓  
  - Attach Files: ✓
  - Manage Webhooks: ✓

#augur-reports:
  - Send Messages: ✓
  - Embed Links: ✓
  - Attach Files: ✓
  - Manage Webhooks: ✓

#helios-logs:
  - Send Messages: ✓
  - Attach Files: ✓
  - Manage Webhooks: ✓

#infrastructure:
  - Send Messages: ✓
  - Embed Links: ✓
  - Manage Webhooks: ✓
```

### Bot Setup Steps
1. Create bot application at https://discord.com/developers/applications
2. Generate bot token (keep secure)
3. Enable required privileged intents:
   - Message Content Intent (if reading messages)
   - Server Members Intent (if needed)
4. Invite bot with permission integer: `537259072` (calculated from above permissions)
5. Assign role with appropriate permissions hierarchy

## 3. OpenClaw Discord Channel Configuration

### YAML Configuration Snippet

```yaml
# discord-config.yml
discord:
  enabled: true
  bot_token: "${DISCORD_BOT_TOKEN}"  # Environment variable
  guild_id: "YOUR_SERVER_ID_HERE"
  
  channels:
    general:
      id: "GENERAL_CHANNEL_ID"
      name: "general"
      description: "General team discussion"
      
    augur_signals:
      id: "AUGUR_SIGNALS_CHANNEL_ID" 
      name: "augur-signals"
      description: "Real-time AUGUR trading signals"
      webhook_url: "${AUGUR_SIGNALS_WEBHOOK_URL}"
      rate_limit: 10  # messages per minute
      
    augur_reports:
      id: "AUGUR_REPORTS_CHANNEL_ID"
      name: "augur-reports" 
      description: "Daily AUGUR performance reports"
      webhook_url: "${AUGUR_REPORTS_WEBHOOK_URL}"
      schedule: "0 23 * * *"  # Daily at 11 PM
      
    helios_logs:
      id: "HELIOS_LOGS_CHANNEL_ID"
      name: "helios-logs"
      description: "Helios AI system logs"
      webhook_url: "${HELIOS_LOGS_WEBHOOK_URL}"
      log_level: "INFO"  # DEBUG, INFO, WARN, ERROR
      buffer_size: 100   # Log entries before flush
      
    infrastructure:
      id: "INFRASTRUCTURE_CHANNEL_ID"
      name: "infrastructure"  
      description: "System status and alerts"
      webhook_url: "${INFRASTRUCTURE_WEBHOOK_URL}"
      alert_types: ["deployment", "error", "performance"]
      
    dev:
      id: "DEV_CHANNEL_ID"
      name: "dev"
      description: "Development coordination"

  # Message formatting
  formatting:
    embed_color: 0x7289DA  # Discord blurple
    timestamp_format: "YYYY-MM-DD HH:mm:ss UTC"
    max_message_length: 2000
    
  # Rate limiting and safety
  rate_limits:
    global: 50          # messages per minute across all channels
    per_channel: 10     # messages per minute per channel  
    burst_limit: 5      # burst allowance
    
  # Error handling
  retry_config:
    max_retries: 3
    backoff_factor: 2
    timeout: 30
```

### Environment Variables Required
```bash
# .env file
DISCORD_BOT_TOKEN=your_bot_token_here
AUGUR_SIGNALS_WEBHOOK_URL=https://discord.com/api/webhooks/...
AUGUR_REPORTS_WEBHOOK_URL=https://discord.com/api/webhooks/...
HELIOS_LOGS_WEBHOOK_URL=https://discord.com/api/webhooks/...
INFRASTRUCTURE_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## 4. Webhook Setup for AUGUR Trade Alerts

### Creating Webhooks

#### Step-by-Step Webhook Creation
1. **Navigate to Channel Settings**
   - Right-click target channel → Edit Channel
   - Go to Integrations → Webhooks
   - Click "Create Webhook"

2. **Configure Webhook**
   ```
   Name: AUGUR Signals Bot
   Avatar: Upload LBF/AUGUR logo
   Channel: #augur-signals
   ```

3. **Copy Webhook URL**
   - Format: `https://discord.com/api/webhooks/{webhook.id}/{webhook.token}`
   - Store securely in environment variables

#### Required Webhooks
- **#augur-signals**: Real-time trade alerts
- **#augur-reports**: Daily/weekly reports  
- **#helios-logs**: System logs
- **#infrastructure**: Status notifications

### AUGUR Alert Integration

#### Signal Message Format
```json
{
  "embeds": [{
    "title": "🚨 AUGUR Trading Signal",
    "description": "New high-confidence trading opportunity detected",
    "color": 3447003,
    "timestamp": "2026-02-16T19:30:00.000Z",
    "fields": [
      {
        "name": "Symbol",
        "value": "BTC-USD", 
        "inline": true
      },
      {
        "name": "Action",
        "value": "BUY",
        "inline": true  
      },
      {
        "name": "Confidence",
        "value": "87.3%",
        "inline": true
      },
      {
        "name": "Price Target",
        "value": "$43,250.00",
        "inline": true
      },
      {
        "name": "Stop Loss", 
        "value": "$42,100.00",
        "inline": true
      },
      {
        "name": "Strategy",
        "value": "momentum_breakout_v4",
        "inline": true
      }
    ],
    "footer": {
      "text": "AUGUR V5 • LBF Trading System"
    }
  }]
}
```

#### Report Message Format  
```json
{
  "embeds": [{
    "title": "📊 AUGUR Daily Report - February 16, 2026",
    "description": "Performance summary and key metrics",
    "color": 65280,
    "timestamp": "2026-02-16T23:00:00.000Z",
    "fields": [
      {
        "name": "Total Trades",
        "value": "27,201",
        "inline": true
      },
      {
        "name": "Win Rate", 
        "value": "23.1%",
        "inline": true
      },
      {
        "name": "Daily PnL",
        "value": "+$137.82",
        "inline": true
      },
      {
        "name": "Top Strategy",
        "value": "OGN-USD (+$26.54)",
        "inline": false
      }
    ],
    "footer": {
      "text": "Paper Trading Mode • Full report attached"
    }
  }]
}
```

### Webhook Testing Commands
```bash
# Test webhook connectivity
curl -X POST "${AUGUR_SIGNALS_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"content": "✅ AUGUR webhook test successful"}'

# Test with embed
curl -X POST "${AUGUR_SIGNALS_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "🔧 System Test",
      "description": "Discord webhook integration active",
      "color": 16776960
    }]
  }'
```

## 5. Security & Best Practices

### Token Security
- Store all tokens in environment variables
- Use `.env` files locally (add to `.gitignore`)
- Use proper secrets management in production
- Rotate tokens quarterly

### Permission Principle
- Grant minimum required permissions
- Use role-based access control
- Regular permission audits
- Separate bot accounts per environment

### Monitoring
- Log all webhook requests
- Monitor rate limits
- Alert on webhook failures  
- Track message delivery success rates

### Backup Strategy
- Export channel history regularly
- Backup webhook configurations
- Document all channel purposes
- Maintain channel ID registry

## 6. Troubleshooting Guide

### Common Issues

#### **Webhook 404 Errors**
- Verify webhook URL is correct
- Check webhook hasn't been deleted
- Confirm channel still exists
- Validate bot permissions

#### **Rate Limiting (429 Errors)**  
- Implement exponential backoff
- Queue messages during high traffic
- Monitor rate limit headers
- Distribute load across webhooks

#### **Permission Denied (403 Errors)**
- Verify bot has required permissions
- Check channel-specific overrides  
- Confirm bot role hierarchy
- Validate webhook permissions

#### **Message Formatting Issues**
- Validate JSON payload structure
- Check embed field limits (25 fields max)
- Verify character limits (2000 chars)
- Test special character encoding

### Debug Commands
```bash
# Check bot permissions
GET /guilds/{guild.id}/members/{bot.id}

# List webhooks
GET /channels/{channel.id}/webhooks

# Validate embed
POST /webhooks/{webhook.id}/{webhook.token}/slack
```

## 7. Implementation Checklist

### Pre-Deployment
- [ ] Discord server created
- [ ] All channels created with proper names
- [ ] Bot application created and configured
- [ ] Bot invited with correct permissions
- [ ] All webhooks created and URLs stored
- [ ] Environment variables configured
- [ ] YAML configuration file created
- [ ] Test webhooks functional

### Post-Deployment  
- [ ] Real trading signals flowing
- [ ] Daily reports scheduling correctly
- [ ] Log levels appropriate
- [ ] Rate limits not exceeded
- [ ] Error handling working
- [ ] Team members have proper access
- [ ] Backup procedures tested

### Monitoring Setup
- [ ] Webhook failure alerts configured
- [ ] Rate limit monitoring active
- [ ] Message delivery tracking enabled
- [ ] Error log aggregation working

---

## Appendix

### Channel ID Reference Template
```yaml
# Store actual IDs here after channel creation
GENERAL_CHANNEL_ID: "123456789012345678"
AUGUR_SIGNALS_CHANNEL_ID: "123456789012345679"  
AUGUR_REPORTS_CHANNEL_ID: "123456789012345680"
HELIOS_LOGS_CHANNEL_ID: "123456789012345681"
INFRASTRUCTURE_CHANNEL_ID: "123456789012345682"
DEV_CHANNEL_ID: "123456789012345683"
```

### Permission Integer Calculator
Base permissions for OpenClaw bot:
- View Channels: 1024
- Send Messages: 2048  
- Embed Links: 16384
- Attach Files: 32768
- Read Message History: 65536
- Use External Emojis: 262144
- Manage Webhooks: 536870912

**Total: 537259072** (use for bot invite URL)

---

*Generated: February 16, 2026*  
*Document Version: 1.0*  
*LBF OpenClaw Integration Team*