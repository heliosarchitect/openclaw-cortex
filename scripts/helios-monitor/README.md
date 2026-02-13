# Helios Self-Monitor

Lightweight observability service for Helios operations.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:9090/` | Web dashboard (auto-refresh 10s) |
| `http://localhost:9090/metrics` | Prometheus-compatible metrics |
| `http://localhost:9090/api/health` | JSON health summary |
| `http://localhost:9090/api/alerts` | Active alerts |

## Metrics Collected

- **System**: RAM, swap, disk, load average, uptime
- **OpenClaw Gateway**: running state, RSS, CPU, uptime, tool failures, Discord reconnects, lane waits
- **Brain/Cortex**: STM entries, atoms, embeddings, causal links, threads, categories
- **Log Events**: tool exec failures, lane wait exceeded, Discord gateway reconnects

## Alerts

| Alert | Threshold | Severity |
|-------|-----------|----------|
| memory_high | RAM > 80% | warning |
| memory_critical | RAM > 95% | critical |
| swap_high | Swap > 30GB | warning |
| disk_high | Disk > 80% | warning |
| openclaw_down | Gateway not running | critical |
| discord_reconnect_storm | > 50 reconnects | warning |
| high_load | Load > 16 | warning |

## Service Management

```bash
systemctl --user status helios-monitor
systemctl --user restart helios-monitor
journalctl --user -u helios-monitor -f
```

## Collection Interval

Every 30 seconds. Dashboard auto-refreshes every 10 seconds.
