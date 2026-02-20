#!/bin/bash
# Alert consolidator - checks for alert flags and wakes OpenClaw with consolidated message
# This runs as an OpenClaw cron job

ALERT_DIR="/tmp/helios-alerts"
mkdir -p "$ALERT_DIR"

alerts=""
alert_count=0

# Check for email alerts
if [ -f "$ALERT_DIR/email-alert" ]; then
    email_alert=$(cat "$ALERT_DIR/email-alert")
    alerts="$alerts📧 $email_alert\n"
    rm "$ALERT_DIR/email-alert"
    alert_count=$((alert_count + 1))
fi

# Check for world events alerts
if [ -f "$ALERT_DIR/world-events-alert" ]; then
    events_alert=$(cat "$ALERT_DIR/world-events-alert")
    alerts="$alerts🌍 $events_alert\n"
    rm "$ALERT_DIR/world-events-alert"
    alert_count=$((alert_count + 1))
fi

# Check for synapse alerts
if [ -f "$ALERT_DIR/synapse-alert" ]; then
    synapse_alert=$(cat "$ALERT_DIR/synapse-alert")
    alerts="$alerts📡 $synapse_alert\n"
    rm "$ALERT_DIR/synapse-alert"
    alert_count=$((alert_count + 1))
fi

# Check for proactive work alerts
if [ -f "$ALERT_DIR/proactive-work-alert" ]; then
    work_alert=$(cat "$ALERT_DIR/proactive-work-alert")
    alerts="$alerts🔧 $work_alert\n"
    rm "$ALERT_DIR/proactive-work-alert"
    alert_count=$((alert_count + 1))
fi

# Check for webhook failure alerts
if [ -f "$ALERT_DIR/webhook-failure-alert" ]; then
    webhook_alert=$(cat "$ALERT_DIR/webhook-failure-alert")
    alerts="$alerts🔗 $webhook_alert\n"
    rm "$ALERT_DIR/webhook-failure-alert"
    alert_count=$((alert_count + 1))
fi

# If any alerts found, wake up with consolidated message
if [ "$alert_count" -gt 0 ]; then
    echo -e "🔔 CONSOLIDATED ALERTS ($alert_count):\n$alerts"
else
    echo "HEARTBEAT_OK"
fi