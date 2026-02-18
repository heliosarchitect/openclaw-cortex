---
name: security-monitor
description: Comprehensive security monitoring and SIEM integration for OpenClaw. Integrates with Wazuh, monitors system security events, analyzes logs, and provides proactive threat detection.
---

# Security Monitor Skill

This skill provides comprehensive security monitoring capabilities for OpenClaw deployments, with native Wazuh integration and system-level security analysis.

## Features

### 🛡️ Wazuh Integration
- **Agent Status**: Monitor Wazuh agent health across fleet
- **Alert Analysis**: Parse and categorize security alerts
- **Rule Management**: Deploy custom detection rules
- **Dashboard Access**: Direct API integration with Wazuh manager

### 📊 System Monitoring
- **Process Monitoring**: Detect suspicious processes
- **Network Analysis**: Monitor open ports and connections
- **File Integrity**: Track critical file changes
- **User Activity**: Audit authentication and privilege escalation

### 🔍 Threat Detection
- **Anomaly Detection**: Statistical analysis of security events
- **IOC Scanning**: Check for indicators of compromise
- **Behavioral Analysis**: Baseline normal activity patterns
- **Alert Correlation**: Cross-reference multiple data sources

### 📈 Reporting
- **Security Dashboards**: Real-time security posture
- **Incident Reports**: Automated incident documentation
- **Compliance Checks**: CIS benchmarks and security standards
- **Trend Analysis**: Historical security metrics

## Quick Start

```bash
# Check Wazuh agent status
security-monitor status

# Get recent security alerts
security-monitor alerts --last 24h --severity high

# Run security scan
security-monitor scan --full

# Generate security report
security-monitor report --daily
```

## Commands

### Core Commands
- `status` - Check security system health
- `alerts [--last TIME] [--severity LEVEL]` - Get security alerts
- `scan [--quick|--full]` - Run security scans
- `report [--daily|--weekly|--custom RANGE]` - Generate reports

### Wazuh Integration
- `wazuh-status` - Wazuh manager and agent status
- `wazuh-rules` - List and manage detection rules
- `wazuh-agents` - Fleet agent management
- `wazuh-dashboard` - Launch Wazuh web interface

### Advanced Analysis
- `threat-hunt QUERY` - Custom threat hunting queries
- `ioc-scan [--file FILE|--hash HASH]` - IOC analysis
- `baseline-update` - Update behavioral baselines
- `correlate-events` - Cross-event correlation analysis

## Configuration

### Wazuh Settings
```yaml
wazuh:
  manager_url: "http://192.168.10.143:55000"
  username: "wazuh"
  password: "wazuh"  # Use environment variable in production
  verify_ssl: false
  timeout: 30

monitoring:
  alert_threshold: "medium"
  scan_frequency: "1h"
  report_schedule: "daily"
  retention_days: 90
```

### Alert Categories
- **Critical**: Active intrusion attempts, malware detection
- **High**: Privilege escalation, suspicious processes
- **Medium**: Failed authentication, policy violations  
- **Low**: Information gathering, reconnaissance

## Integration

### OpenClaw Integration
Add to your workflow automation:
```yaml
- name: Security Check
  skill: security-monitor
  action: scan
  schedule: "0 */4 * * *"  # Every 4 hours
  alert_on: ["critical", "high"]
```

### Webhook Alerts
Configure external alert destinations:
```yaml
webhooks:
  slack: "https://hooks.slack.com/services/..."
  discord: "https://discord.com/api/webhooks/..."
  email: "security@yourdomain.com"
```

### Custom Rules
Deploy organization-specific detection rules:
```yaml
custom_rules:
  - name: "Crypto Mining Detection"
    pattern: "xmrig|stratum|mining"
    severity: "high"
    action: "alert"
  
  - name: "Suspicious Network Activity"
    pattern: "port scan|nmap"
    severity: "medium"
    action: "log"
```

## Files

- **Scripts**: `scripts/security-monitor.py`
- **Config**: `config/security-monitor.yaml`
- **Rules**: `rules/custom-rules.xml`
- **Reports**: `reports/` (generated outputs)
- **Logs**: `logs/security-monitor.log`

## Use Cases

### 🏢 Enterprise Security
- Continuous security monitoring
- Compliance reporting (SOC2, ISO27001)
- Incident response automation
- Security metrics for management

### 🔒 Personal Security
- Home lab monitoring
- Development environment protection
- Cryptocurrency security
- Privacy monitoring

### 📡 Fleet Management
- Multi-system security oversight
- Centralized alert correlation
- Automated remediation
- Security baseline enforcement

## Security Best Practices

- **Credential Management**: Store Wazuh credentials in `~/.secrets/wazuh.env`
- **Network Security**: Use VPN or private networks for Wazuh communication
- **Alert Tuning**: Configure appropriate thresholds to reduce false positives
- **Regular Updates**: Keep Wazuh agents and rules updated
- **Backup Configuration**: Regular backup of security configurations

## Troubleshooting

### Common Issues
- **Agent Disconnected**: Check network connectivity and agent status
- **High Alert Volume**: Tune detection rules and thresholds
- **Performance Impact**: Adjust scan frequency and scope
- **False Positives**: Refine custom rules and baselines

### Debug Mode
Enable detailed logging:
```bash
export SECURITY_MONITOR_DEBUG=1
security-monitor scan --debug
```

### Health Checks
Verify system health:
```bash
security-monitor diagnose
```

---

Built for comprehensive security monitoring in modern infrastructure environments. Integrates seamlessly with existing OpenClaw automation workflows.