# World Event Monitoring System (WEMS) - OpenClaw Skill

**Author**: OpenClaw AI  
**Version**: 1.0.0  
**Category**: Monitoring & Alerts  
**Tags**: `monitoring`, `disasters`, `weather`, `earthquakes`, `space-weather`, `drought`

## Overview

The World Event Monitoring System (WEMS) is an MCP server that provides real-time monitoring and alerting for global events including earthquakes, severe weather, space weather phenomena, and drought conditions. This skill documents how to integrate WEMS with OpenClaw for automated monitoring and intelligent alerting.

## Installation

### Prerequisites
- Python 3.8+
- OpenClaw Gateway with MCP support
- Network connectivity for data sources

### Install WEMS MCP Server
```bash
# Install from PyPI
pip install wems-mcp

# Verify installation
wems-mcp --version
```

## Running as MCP Server

### Stdio Transport (Recommended)
```bash
# Start WEMS MCP server with stdio transport
wems-mcp --transport stdio

# Or with custom config
wems-mcp --transport stdio --config ~/.openclaw/wems-config.json
```

### Configuration File (`~/.openclaw/wems-config.json`)
```json
{
  "earthquake": {
    "enabled": true,
    "min_magnitude": 4.0,
    "regions": ["global", "us", "pacific"]
  },
  "weather": {
    "enabled": true,
    "alert_types": ["severe_thunderstorm", "tornado", "hurricane", "flood"],
    "countries": ["US", "CA", "EU"]
  },
  "space_weather": {
    "enabled": true,
    "monitor_solar_flares": true,
    "monitor_geomagnetic_storms": true
  },
  "drought": {
    "enabled": true,
    "severity_threshold": "moderate",
    "regions": ["us_states"]
  },
  "polling_interval": 300,
  "webhook_url": null
}
```

### OpenClaw Gateway Integration
Add to your `gateway.config.json`:
```json
{
  "mcp_servers": {
    "wems": {
      "command": "wems-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true,
      "auto_restart": true
    }
  }
}
```

## Available Tools

### 1. Earthquake Monitoring (`earthquake_monitor`)
**Purpose**: Monitor global seismic activity and significant earthquakes

**Parameters**:
- `region` (string): Geographic region ("global", "us", "pacific", "europe", etc.)
- `min_magnitude` (float): Minimum earthquake magnitude (default: 4.0)
- `time_window` (string): Time period ("1day", "7day", "30day")
- `limit` (int): Maximum number of results (default: 50)

**Example**:
```python
# Get recent significant earthquakes globally
earthquakes = earthquake_monitor(region="global", min_magnitude=5.0, time_window="7day")
```

### 2. Weather Alerts (`weather_alerts`)
**Purpose**: Monitor severe weather conditions and official alerts

**Parameters**:
- `country` (string): Country code ("US", "CA", "GB", etc.)
- `state_province` (string): State/province filter
- `alert_types` (array): Types to monitor ["tornado", "hurricane", "flood", "severe_thunderstorm"]
- `severity` (string): Minimum severity ("minor", "moderate", "severe", "extreme")
- `active_only` (bool): Only return active alerts (default: true)

**Example**:
```python
# Get active severe weather alerts for US
alerts = weather_alerts(country="US", alert_types=["tornado", "hurricane"], severity="severe")
```

### 3. Space Weather (`space_weather_monitor`)
**Purpose**: Monitor solar activity, geomagnetic storms, and space weather events

**Parameters**:
- `event_types` (array): Types to monitor ["solar_flare", "geomagnetic_storm", "solar_wind", "cosmic_rays"]
- `severity` (string): Minimum event severity ("minor", "moderate", "strong", "severe", "extreme")
- `time_window` (string): Monitoring period ("1hour", "6hour", "24hour", "7day")

**Example**:
```python
# Monitor severe space weather events
space_events = space_weather_monitor(event_types=["solar_flare", "geomagnetic_storm"], severity="severe")
```

### 4. Drought Monitor (`drought_monitor`)
**Purpose**: Track drought conditions and water resource status

**Parameters**:
- `region` (string): Geographic region ("us_states", "global_basins", "europe")
- `severity` (string): Minimum drought level ("abnormally_dry", "moderate", "severe", "extreme", "exceptional")
- `trend` (string): Filter by trend ("improving", "worsening", "stable", "all")

**Example**:
```python
# Monitor severe drought conditions in US states
drought_data = drought_monitor(region="us_states", severity="severe", trend="worsening")
```

### 5. Event Summary (`get_event_summary`)
**Purpose**: Get aggregated summary of all monitored events

**Parameters**:
- `time_window` (string): Summary period ("1hour", "6hour", "24hour", "7day")
- `include_minor` (bool): Include minor events (default: false)
- `group_by` (string): Grouping method ("type", "region", "severity")

**Example**:
```python
# Get 24-hour event summary
summary = get_event_summary(time_window="24hour", group_by="severity")
```

## Web Fetch Fallback

When WEMS MCP server is unavailable at the gateway level, you can query event data directly via web_fetch:

### USGS Earthquake Data
```python
# Recent earthquakes M4.5+ past 7 days
earthquake_data = web_fetch("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson")
```

### NOAA Weather Alerts
```python
# US weather alerts
weather_data = web_fetch("https://api.weather.gov/alerts/active")
```

### NOAA Space Weather
```python
# Space weather conditions
space_data = web_fetch("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
```

### US Drought Monitor
```python
# Current US drought conditions
drought_data = web_fetch("https://droughtmonitor.unl.edu/data/json/usdm_current_json.json")
```

## Alert Thresholds & Significant Events

### Earthquakes
- **Routine**: Magnitude 4.0-4.9 (regional interest)
- **Notable**: Magnitude 5.0-5.9 (significant regional impact)
- **Major**: Magnitude 6.0-6.9 (strong earthquake, potential damage)
- **Great**: Magnitude 7.0+ (major earthquake, widespread impact)
- **Catastrophic**: Magnitude 8.0+ (great earthquake, international concern)

**Geographic Priority Zones**:
- Ring of Fire (Pacific Rim)
- Mediterranean/Middle East
- Central/Eastern US (unusual activity)
- Major population centers

### Weather Alerts
**Severity Levels**:
- **Minor**: Local advisories, watches
- **Moderate**: Warnings affecting cities
- **Severe**: Life-threatening conditions
- **Extreme**: Catastrophic potential
- **Exceptional**: Historic/unprecedented events

**High Priority Events**:
- Tornado warnings (EF3+)
- Hurricane/Typhoon (Cat 3+)
- Flash flood emergencies
- Blizzard warnings in major metros
- Heat dome events (115°F+)

### Space Weather
**Event Classifications**:
- **S-Scale** (Solar Radiation): S1 (minor) to S5 (extreme)
- **R-Scale** (Radio Blackouts): R1 (minor) to R5 (extreme)  
- **G-Scale** (Geomagnetic): G1 (minor) to G5 (extreme)

**Critical Thresholds**:
- G3+ geomagnetic storms (power grid risk)
- X-class solar flares (satellite/communication risk)
- Cosmic ray ground level events
- Solar particle events affecting aviation

### Drought Conditions
**US Drought Monitor Categories**:
- **D0**: Abnormally Dry (watch level)
- **D1**: Moderate Drought (agricultural impact)
- **D2**: Severe Drought (water restrictions)
- **D3**: Extreme Drought (major water shortages)
- **D4**: Exceptional Drought (emergency conditions)

**Alert Priorities**:
- D2+ affecting major watersheds
- D3+ in agricultural regions
- Rapid drought intensification
- Multi-year exceptional drought

## OpenClaw Cron Integration

### Periodic Monitoring Script (`~/.openclaw/cron/wems-monitor.py`)
```python
#!/usr/bin/env python3
"""
WEMS Periodic Monitor for OpenClaw
Runs every 15 minutes via cron
"""

import json
from datetime import datetime
from openclaw import mcp_call, cortex_add, message_send

def monitor_events():
    """Monitor all WEMS event types and alert on significant events"""
    
    significant_events = []
    
    # Check earthquakes
    try:
        earthquakes = mcp_call('wems', 'earthquake_monitor', {
            'region': 'global',
            'min_magnitude': 5.0,
            'time_window': '1day'
        })
        
        for eq in earthquakes.get('features', []):
            props = eq['properties']
            mag = props.get('mag', 0)
            place = props.get('place', 'Unknown')
            
            if mag >= 6.0:
                significant_events.append({
                    'type': 'earthquake',
                    'severity': 'major' if mag >= 7.0 else 'significant',
                    'details': f"M{mag:.1f} earthquake - {place}",
                    'magnitude': mag,
                    'location': place
                })
                
    except Exception as e:
        print(f"Earthquake monitoring error: {e}")
    
    # Check weather alerts
    try:
        alerts = mcp_call('wems', 'weather_alerts', {
            'country': 'US',
            'severity': 'severe',
            'active_only': True
        })
        
        critical_types = ['Tornado Warning', 'Hurricane Warning', 'Flash Flood Emergency']
        
        for alert in alerts.get('features', []):
            props = alert['properties']
            event_type = props.get('event', '')
            areas = props.get('areas', 'Unknown')
            
            if any(ct in event_type for ct in critical_types):
                significant_events.append({
                    'type': 'weather',
                    'severity': 'critical',
                    'details': f"{event_type} - {areas}",
                    'event_type': event_type,
                    'areas': areas
                })
                
    except Exception as e:
        print(f"Weather monitoring error: {e}")
    
    # Check space weather
    try:
        space_events = mcp_call('wems', 'space_weather_monitor', {
            'event_types': ['solar_flare', 'geomagnetic_storm'],
            'severity': 'strong',
            'time_window': '6hour'
        })
        
        for event in space_events.get('events', []):
            event_type = event.get('type', '')
            scale = event.get('scale', '')
            
            if scale in ['G3', 'G4', 'G5', 'X'] or 'extreme' in event.get('severity', '').lower():
                significant_events.append({
                    'type': 'space_weather',
                    'severity': 'critical',
                    'details': f"{event_type} - {scale} class event",
                    'scale': scale,
                    'event_type': event_type
                })
                
    except Exception as e:
        print(f"Space weather monitoring error: {e}")
    
    # Store and alert on significant events
    if significant_events:
        # Add to Cortex memory
        event_summary = f"WEMS Alert - {len(significant_events)} significant events detected:\\n"
        for event in significant_events:
            event_summary += f"• {event['type'].title()}: {event['details']}\\n"
        
        cortex_add(
            content=event_summary,
            categories=['alerts', 'monitoring', 'wems'],
            importance=3.0  # Critical events
        )
        
        # Send alert message (if configured)
        try:
            message_send(
                action='send',
                target='emergency_channel',  # Configure in gateway
                message=f"🚨 **WEMS CRITICAL ALERTS** ({datetime.now().strftime('%Y-%m-%d %H:%M UTC')})\\n\\n{event_summary}",
                priority='urgent'
            )
        except Exception as e:
            print(f"Alert messaging error: {e}")
    
    return len(significant_events)

if __name__ == "__main__":
    try:
        event_count = monitor_events()
        print(f"WEMS monitoring complete - {event_count} significant events processed")
    except Exception as e:
        print(f"WEMS monitoring failed: {e}")
```

### Cron Schedule
Add to OpenClaw crontab:
```bash
# WEMS Event Monitoring - every 15 minutes
*/15 * * * * /usr/bin/python3 ~/.openclaw/cron/wems-monitor.py >> ~/.openclaw/logs/wems-monitor.log 2>&1

# WEMS Daily Summary - 8 AM daily
0 8 * * * /usr/bin/python3 ~/.openclaw/cron/wems-daily-summary.py
```

### Daily Summary Script (`~/.openclaw/cron/wems-daily-summary.py`)
```python
#!/usr/bin/env python3
"""
WEMS Daily Summary Generator
"""

from datetime import datetime, timedelta
from openclaw import mcp_call, cortex_add

def generate_daily_summary():
    """Generate comprehensive daily event summary"""
    
    summary_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Get 24-hour event summary
        summary = mcp_call('wems', 'get_event_summary', {
            'time_window': '24hour',
            'include_minor': False,
            'group_by': 'severity'
        })
        
        report = f"WEMS Daily Summary - {summary_date}\\n\\n"
        
        # Add summary statistics
        stats = summary.get('statistics', {})
        report += f"**Event Statistics (24h):**\\n"
        report += f"• Total Events: {stats.get('total_events', 0)}\\n"
        report += f"• Critical: {stats.get('critical', 0)}\\n"
        report += f"• Major: {stats.get('major', 0)}\\n"
        report += f"• Significant: {stats.get('significant', 0)}\\n\\n"
        
        # Add notable events
        notable = summary.get('notable_events', [])
        if notable:
            report += "**Notable Events:**\\n"
            for event in notable[:10]:  # Top 10
                report += f"• {event.get('type', 'Unknown').title()}: {event.get('summary', 'No details')}\\n"
        else:
            report += "**Notable Events:** None reported\\n"
        
        # Store in Cortex
        cortex_add(
            content=report,
            categories=['wems', 'daily_reports', 'monitoring'],
            importance=2.0
        )
        
        print(f"Daily summary generated: {len(notable)} events")
        return report
        
    except Exception as e:
        print(f"Daily summary generation failed: {e}")
        return None

if __name__ == "__main__":
    generate_daily_summary()
```

## Best Practices

### 1. Alert Fatigue Prevention
- Set appropriate thresholds for your region/interests
- Use severity filtering to focus on actionable events
- Implement alert escalation (minor → moderate → severe)
- Consider time-based muting for routine events

### 2. Resource Management
- Limit polling frequency to avoid rate limiting
- Cache non-critical data locally
- Use web_fetch fallback sparingly
- Monitor API quotas and usage

### 3. Integration Patterns
- Store significant events in Cortex for pattern analysis
- Use Synapse for inter-agent event coordination
- Implement graceful degradation when MCP is unavailable
- Log all monitoring activities for debugging

### 4. Data Quality
- Cross-reference multiple data sources when possible
- Validate event timestamps and locations
- Handle API rate limits and outages gracefully
- Implement data freshness checks

## Troubleshooting

### Common Issues

**MCP Server Won't Start**:
```bash
# Check Python environment
python3 -m pip show wems-mcp

# Verify dependencies
wems-mcp --check-deps

# Run with debug logging
wems-mcp --transport stdio --debug
```

**No Event Data**:
- Verify network connectivity to data sources
- Check API rate limiting
- Ensure proper geographic region settings
- Validate configuration file syntax

**High Resource Usage**:
- Increase polling intervals
- Reduce monitored regions/event types
- Implement local caching
- Use severity thresholds

**False Positive Alerts**:
- Adjust magnitude/severity thresholds
- Implement location-based filtering
- Add event correlation logic
- Review alert logic and timing

## Support & Resources

- **Documentation**: [WEMS MCP Documentation]
- **GitHub Issues**: [heliosarchitect/wems-mcp/issues]
- **PyPI Package**: [wems-mcp on PyPI]
- **Data Sources**: USGS, NOAA, SWPC, US Drought Monitor
- **OpenClaw Integration**: See OpenClaw MCP documentation

---

*This skill provides comprehensive monitoring capabilities for global events. Always verify critical events through multiple sources and maintain appropriate response procedures for your use case.*