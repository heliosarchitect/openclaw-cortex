#!/usr/bin/env python3
"""
Helios Self-Monitoring Dashboard
=================================
FastAPI service providing:
  - Prometheus-compatible /metrics endpoint (port 9090)
  - Web dashboard at / showing key health indicators
  - JSON API at /api/health for programmatic access
  - Alerting state at /api/alerts

Collects: system resources, OpenClaw gateway health, brain.db stats,
session health, tool failures, Discord gateway status.

Run: python3 helios_monitor.py
Service: systemctl --user start helios-monitor
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from prometheus_client import (
    CollectorRegistry, Counter, Gauge, Histogram,
    generate_latest, CONTENT_TYPE_LATEST,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PORT = 9090
BRAIN_DB = Path.home() / ".openclaw/workspace/memory/brain.db"
COLLECT_INTERVAL = 30  # seconds between metric scrapes
LOG_LINES_SCAN = 500   # journalctl lines to scan per cycle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [helios-monitor] %(levelname)s %(message)s",
)
log = logging.getLogger("helios-monitor")

# ---------------------------------------------------------------------------
# Prometheus Registry
# ---------------------------------------------------------------------------
registry = CollectorRegistry()

# System metrics
sys_mem_total = Gauge("system_memory_total_mb", "Total RAM MB", registry=registry)
sys_mem_used = Gauge("system_memory_used_mb", "Used RAM MB", registry=registry)
sys_mem_pct = Gauge("system_memory_used_percent", "RAM used %", registry=registry)
sys_swap_used = Gauge("system_swap_used_mb", "Swap used MB", registry=registry)
sys_disk_used_pct = Gauge("system_disk_used_percent", "Root disk used %", registry=registry)
sys_load_1m = Gauge("system_load_1m", "1-min load average", registry=registry)
sys_load_5m = Gauge("system_load_5m", "5-min load average", registry=registry)
sys_uptime_days = Gauge("system_uptime_days", "System uptime in days", registry=registry)

# OpenClaw process metrics
oc_process_rss_mb = Gauge("openclaw_process_rss_mb", "OpenClaw gateway RSS MB", registry=registry)
oc_process_cpu_pct = Gauge("openclaw_process_cpu_percent", "OpenClaw gateway CPU %", registry=registry)
oc_uptime_hours = Gauge("openclaw_uptime_hours", "OpenClaw gateway uptime hours", registry=registry)
oc_running = Gauge("openclaw_gateway_running", "1 if gateway is active", registry=registry)

# Brain.db / Cortex metrics
brain_stm_entries = Gauge("brain_stm_entries", "STM entry count", registry=registry)
brain_atoms = Gauge("brain_atoms", "Atom count", registry=registry)
brain_embeddings = Gauge("brain_embeddings", "Embedding count", registry=registry)
brain_causal_links = Gauge("brain_causal_links", "Causal link count", registry=registry)
brain_threads = Gauge("brain_threads", "Thread count", registry=registry)
brain_categories = Gauge("brain_categories", "Category count", registry=registry)

# Log-derived metrics (counters reset on restart — that's fine for rates)
log_tool_failures = Counter("openclaw_tool_failures_total", "Tool exec failures seen in logs", registry=registry)
log_lane_waits = Counter("openclaw_lane_waits_total", "Lane wait exceeded events", registry=registry)
log_discord_reconnects = Counter("openclaw_discord_reconnects_total", "Discord gateway reconnect attempts", registry=registry)
log_errors = Counter("openclaw_errors_total", "Generic error lines in logs", registry=registry)

# Session metrics
sessions_active = Gauge("openclaw_sessions_active", "Active sessions count", registry=registry)

# Heartbeat tracking
heartbeat_last_ts = Gauge("helios_heartbeat_last_unix", "Last heartbeat timestamp", registry=registry)
heartbeat_ok_streak = Gauge("helios_heartbeat_ok_streak", "Consecutive HEARTBEAT_OK count", registry=registry)

# ---------------------------------------------------------------------------
# Alert definitions
# ---------------------------------------------------------------------------
ALERT_THRESHOLDS = {
    "memory_high": {"metric": "system_memory_used_percent", "op": ">", "value": 80, "severity": "warning"},
    "memory_critical": {"metric": "system_memory_used_percent", "op": ">", "value": 95, "severity": "critical"},
    "swap_high": {"metric": "system_swap_used_mb", "op": ">", "value": 30000, "severity": "warning"},
    "disk_high": {"metric": "system_disk_used_percent", "op": ">", "value": 80, "severity": "warning"},
    "openclaw_down": {"metric": "openclaw_gateway_running", "op": "==", "value": 0, "severity": "critical"},
    "discord_reconnect_storm": {"metric": "openclaw_discord_reconnects_total", "op": ">", "value": 50, "severity": "warning"},
    "high_load": {"metric": "system_load_1m", "op": ">", "value": 16, "severity": "warning"},
}

# Runtime state
_state: dict[str, Any] = {
    "last_collect": 0,
    "alerts_active": [],
    "metrics_snapshot": {},
    "log_scan_since": None,
    "collect_count": 0,
    "_counter_tool_failures": 0,
    "_counter_lane_waits": 0,
    "_counter_discord_reconnects": 0,
    "_counter_errors": 0,
}

# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------

def collect_system():
    """Collect system-level metrics."""
    try:
        mem = subprocess.check_output(["free", "-m"], text=True).strip().split("\n")
        # Mem: total used free shared buff/cache available
        parts = mem[1].split()
        total, used = int(parts[1]), int(parts[2])
        sys_mem_total.set(total)
        sys_mem_used.set(used)
        pct = round(used / total * 100, 1) if total > 0 else 0
        sys_mem_pct.set(pct)
        _state["metrics_snapshot"]["system_memory_used_percent"] = pct
        _state["metrics_snapshot"]["system_memory_used_mb"] = used
        _state["metrics_snapshot"]["system_memory_total_mb"] = total

        swap_parts = mem[2].split()
        swap_used = int(swap_parts[2])
        sys_swap_used.set(swap_used)
        _state["metrics_snapshot"]["system_swap_used_mb"] = swap_used
    except Exception as e:
        log.warning(f"Memory collection failed: {e}")

    try:
        df = subprocess.check_output(["df", "--output=pcent", "/"], text=True).strip().split("\n")
        pct = int(df[1].strip().rstrip("%"))
        sys_disk_used_pct.set(pct)
        _state["metrics_snapshot"]["system_disk_used_percent"] = pct
    except Exception as e:
        log.warning(f"Disk collection failed: {e}")

    try:
        load = os.getloadavg()
        sys_load_1m.set(round(load[0], 2))
        sys_load_5m.set(round(load[1], 2))
        _state["metrics_snapshot"]["system_load_1m"] = round(load[0], 2)
        _state["metrics_snapshot"]["system_load_5m"] = round(load[1], 2)
    except Exception as e:
        log.warning(f"Load collection failed: {e}")

    try:
        uptime_s = float(Path("/proc/uptime").read_text().split()[0])
        days = round(uptime_s / 86400, 2)
        sys_uptime_days.set(days)
        _state["metrics_snapshot"]["system_uptime_days"] = days
    except Exception as e:
        log.warning(f"Uptime collection failed: {e}")


def collect_openclaw_process():
    """Collect OpenClaw gateway process metrics."""
    try:
        result = subprocess.check_output(
            ["systemctl", "--user", "is-active", "openclaw-gateway"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        running = 1 if result == "active" else 0
        oc_running.set(running)
        _state["metrics_snapshot"]["openclaw_gateway_running"] = running
    except subprocess.CalledProcessError:
        oc_running.set(0)
        _state["metrics_snapshot"]["openclaw_gateway_running"] = 0

    try:
        # Find the main gateway process
        ps = subprocess.check_output(
            ["ps", "aux"], text=True
        )
        for line in ps.split("\n"):
            if "openclaw-gateway" in line and "grep" not in line:
                parts = line.split()
                cpu = float(parts[2])
                rss_kb = int(parts[5])
                oc_process_cpu_pct.set(cpu)
                oc_process_rss_mb.set(round(rss_kb / 1024, 1))
                _state["metrics_snapshot"]["openclaw_process_rss_mb"] = round(rss_kb / 1024, 1)
                _state["metrics_snapshot"]["openclaw_process_cpu_percent"] = cpu
                break
    except Exception as e:
        log.warning(f"Process collection failed: {e}")

    try:
        # Gateway uptime from systemctl
        show = subprocess.check_output(
            ["systemctl", "--user", "show", "openclaw-gateway", "--property=ActiveEnterTimestamp"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        # ActiveEnterTimestamp=Thu 2026-02-12 21:02:33 EST
        ts_str = show.split("=", 1)[1]
        if ts_str:
            from dateutil.parser import parse as dateparse
            start = dateparse(ts_str)
            hours = (datetime.now(start.tzinfo) - start).total_seconds() / 3600
            oc_uptime_hours.set(round(hours, 2))
            _state["metrics_snapshot"]["openclaw_uptime_hours"] = round(hours, 2)
    except Exception:
        pass  # dateutil may not be available


def collect_brain_stats():
    """Collect brain.db / cortex stats."""
    try:
        import urllib.request
        resp = urllib.request.urlopen("http://localhost:8031/stats", timeout=5)
        data = json.loads(resp.read())
        brain_stm_entries.set(data.get("stm_entries", 0))
        brain_atoms.set(data.get("atoms", 0))
        brain_embeddings.set(data.get("embeddings", 0))
        brain_causal_links.set(data.get("causal_links", 0))
        brain_threads.set(data.get("threads", 0))
        brain_categories.set(data.get("categories", 0))
        for k in ["stm_entries", "atoms", "embeddings", "causal_links", "threads", "categories"]:
            _state["metrics_snapshot"][f"brain_{k}"] = data.get(k, 0)
    except Exception as e:
        log.warning(f"Brain stats collection failed: {e}")


def collect_logs():
    """Scan recent journalctl logs for events."""
    try:
        since = _state.get("log_scan_since") or "5 min ago"
        lines = subprocess.check_output(
            ["journalctl", "--user", "-u", "openclaw-gateway",
             "--since", since, "--no-pager", "-q"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip().split("\n")

        tool_fail = 0
        lane_wait = 0
        discord_reconnect = 0
        errors = 0

        for line in lines:
            if "exec failed" in line or "tool" in line.lower() and "failed" in line.lower():
                tool_fail += 1
            if "lane wait exceeded" in line:
                lane_wait += 1
            if "Attempting resume" in line:
                discord_reconnect += 1
            if "error" in line.lower() and "failed" in line.lower():
                errors += 1

        # Increment counters
        if tool_fail > 0:
            log_tool_failures.inc(tool_fail)
            _state["_counter_tool_failures"] += tool_fail
        if lane_wait > 0:
            log_lane_waits.inc(lane_wait)
            _state["_counter_lane_waits"] += lane_wait
        if discord_reconnect > 0:
            log_discord_reconnects.inc(discord_reconnect)
            _state["_counter_discord_reconnects"] += discord_reconnect
        if errors > 0:
            log_errors.inc(errors)
            _state["_counter_errors"] += errors

        _state["metrics_snapshot"]["openclaw_tool_failures_total"] = _state["_counter_tool_failures"]
        _state["metrics_snapshot"]["openclaw_discord_reconnects_total"] = _state["_counter_discord_reconnects"]
        _state["metrics_snapshot"]["openclaw_lane_waits_total"] = _state["_counter_lane_waits"]
        _state["metrics_snapshot"]["openclaw_errors_total"] = _state["_counter_errors"]

        # Only scan since last run next time
        _state["log_scan_since"] = "30 sec ago"
    except Exception as e:
        log.warning(f"Log scan failed: {e}")


def evaluate_alerts():
    """Check thresholds and generate active alerts."""
    active = []
    snap = _state["metrics_snapshot"]
    for name, rule in ALERT_THRESHOLDS.items():
        val = snap.get(rule["metric"])
        if val is None:
            continue
        triggered = False
        if rule["op"] == ">" and val > rule["value"]:
            triggered = True
        elif rule["op"] == ">=" and val >= rule["value"]:
            triggered = True
        elif rule["op"] == "==" and val == rule["value"]:
            triggered = True
        elif rule["op"] == "<" and val < rule["value"]:
            triggered = True
        if triggered:
            active.append({
                "name": name,
                "severity": rule["severity"],
                "metric": rule["metric"],
                "value": val,
                "threshold": rule["value"],
                "op": rule["op"],
            })
    _state["alerts_active"] = active
    return active


def run_collection():
    """Run all collectors."""
    t0 = time.time()
    collect_system()
    collect_openclaw_process()
    collect_brain_stats()
    collect_logs()
    alerts = evaluate_alerts()
    _state["last_collect"] = time.time()
    _state["collect_count"] += 1
    elapsed = round(time.time() - t0, 3)
    if alerts:
        log.info(f"Collection #{_state['collect_count']} ({elapsed}s) — {len(alerts)} alert(s) active")
    else:
        log.debug(f"Collection #{_state['collect_count']} ({elapsed}s) — all clear")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(title="Helios Monitor", version="1.0.0")


@app.on_event("startup")
async def startup():
    run_collection()
    asyncio.create_task(periodic_collector())


async def periodic_collector():
    while True:
        await asyncio.sleep(COLLECT_INTERVAL)
        try:
            await asyncio.get_event_loop().run_in_executor(None, run_collection)
        except Exception as e:
            log.error(f"Collection error: {e}")


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    return PlainTextResponse(
        generate_latest(registry).decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/api/health", response_class=JSONResponse)
async def api_health():
    """JSON health summary."""
    snap = _state["metrics_snapshot"]
    return {
        "status": "critical" if any(a["severity"] == "critical" for a in _state["alerts_active"])
                  else "warning" if _state["alerts_active"]
                  else "healthy",
        "alerts": _state["alerts_active"],
        "system": {
            "memory_used_pct": snap.get("system_memory_used_percent"),
            "memory_used_mb": snap.get("system_memory_used_mb"),
            "memory_total_mb": snap.get("system_memory_total_mb"),
            "swap_used_mb": snap.get("system_swap_used_mb"),
            "disk_used_pct": snap.get("system_disk_used_percent"),
            "load_1m": snap.get("system_load_1m"),
            "load_5m": snap.get("system_load_5m"),
            "uptime_days": snap.get("system_uptime_days"),
        },
        "openclaw": {
            "running": bool(snap.get("openclaw_gateway_running")),
            "rss_mb": snap.get("openclaw_process_rss_mb"),
            "cpu_pct": snap.get("openclaw_process_cpu_percent"),
            "uptime_hours": snap.get("openclaw_uptime_hours"),
            "tool_failures": snap.get("openclaw_tool_failures_total", 0),
            "discord_reconnects": snap.get("openclaw_discord_reconnects_total", 0),
            "lane_waits": snap.get("openclaw_lane_waits_total", 0),
        },
        "brain": {
            "stm_entries": snap.get("brain_stm_entries"),
            "atoms": snap.get("brain_atoms"),
            "embeddings": snap.get("brain_embeddings"),
            "causal_links": snap.get("brain_causal_links"),
            "threads": snap.get("brain_threads"),
            "categories": snap.get("brain_categories"),
        },
        "meta": {
            "collect_count": _state["collect_count"],
            "last_collect": datetime.fromtimestamp(
                _state["last_collect"], tz=timezone.utc
            ).isoformat() if _state["last_collect"] else None,
        },
    }


@app.get("/api/alerts", response_class=JSONResponse)
async def api_alerts():
    return {"alerts": _state["alerts_active"], "count": len(_state["alerts_active"])}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Web dashboard."""
    return DASHBOARD_HTML


# ---------------------------------------------------------------------------
# Dashboard HTML (self-contained, auto-refreshes)
# ---------------------------------------------------------------------------
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Helios Monitor</title>
<style>
  :root {
    --bg: #0a0e17; --card: #111827; --border: #1f2937;
    --text: #e5e7eb; --dim: #9ca3af; --accent: #3b82f6;
    --green: #10b981; --yellow: #f59e0b; --red: #ef4444;
    --orange: #f97316;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'JetBrains Mono', 'Fira Code', monospace; background: var(--bg); color: var(--text); padding: 1.5rem; }
  h1 { font-size: 1.5rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
  h1 .dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
  h1 .dot.healthy { background: var(--green); box-shadow: 0 0 8px var(--green); }
  h1 .dot.warning { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); }
  h1 .dot.critical { background: var(--red); box-shadow: 0 0 8px var(--red); animation: pulse 1s infinite; }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
  .meta { color: var(--dim); font-size: 0.75rem; margin-bottom: 1.5rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
  .card h2 { font-size: 0.9rem; color: var(--accent); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid var(--border); }
  .row:last-child { border-bottom: none; }
  .label { color: var(--dim); font-size: 0.8rem; }
  .value { font-size: 0.85rem; font-weight: 600; }
  .value.ok { color: var(--green); }
  .value.warn { color: var(--yellow); }
  .value.crit { color: var(--red); }
  .alerts { margin-top: 1rem; }
  .alert { padding: 0.5rem 0.75rem; border-radius: 6px; margin-bottom: 0.5rem; font-size: 0.8rem; }
  .alert.warning { background: rgba(245,158,11,0.15); border: 1px solid var(--yellow); color: var(--yellow); }
  .alert.critical { background: rgba(239,68,68,0.15); border: 1px solid var(--red); color: var(--red); }
  .bar-bg { height: 6px; background: var(--border); border-radius: 3px; margin-top: 0.25rem; }
  .bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
  footer { margin-top: 2rem; text-align: center; color: var(--dim); font-size: 0.7rem; }
</style>
</head>
<body>
<h1><span class="dot" id="statusDot"></span> Helios Monitor</h1>
<div class="meta" id="meta">Loading...</div>
<div id="alertsArea" class="alerts"></div>
<div class="grid" id="grid"></div>
<footer>Helios Self-Monitor v1.0 · Auto-refresh 10s · <a href="/metrics" style="color:var(--accent)">Prometheus /metrics</a> · <a href="/api/health" style="color:var(--accent)">JSON API</a></footer>

<script>
function cls(val, warn, crit, invert) {
  if (invert) return val < crit ? 'crit' : val < warn ? 'warn' : 'ok';
  return val > crit ? 'crit' : val > warn ? 'warn' : 'ok';
}
function fmt(v, suffix) { return v != null ? v + (suffix||'') : '—'; }

function renderCard(title, rows) {
  let html = `<div class="card"><h2>${title}</h2>`;
  for (const [label, value, extra] of rows) {
    html += `<div class="row"><span class="label">${label}</span><span class="value ${extra||''}">${value}</span></div>`;
  }
  html += '</div>';
  return html;
}

async function refresh() {
  try {
    const r = await fetch('/api/health');
    const d = await r.json();
    const s = d.system, o = d.openclaw, b = d.brain;

    // Status dot
    const dot = document.getElementById('statusDot');
    dot.className = 'dot ' + d.status;

    // Meta
    document.getElementById('meta').textContent =
      `Status: ${d.status.toUpperCase()} · Collections: ${d.meta.collect_count} · Last: ${d.meta.last_collect ? new Date(d.meta.last_collect).toLocaleTimeString() : '—'}`;

    // Alerts
    const aa = document.getElementById('alertsArea');
    if (d.alerts.length) {
      aa.innerHTML = d.alerts.map(a =>
        `<div class="alert ${a.severity}">⚠ ${a.name}: ${a.metric} = ${a.value} (threshold ${a.op} ${a.threshold})</div>`
      ).join('');
    } else {
      aa.innerHTML = '';
    }

    // Cards
    let html = '';
    html += renderCard('⚙ System', [
      ['Memory', fmt(s.memory_used_pct, '%') + ` (${fmt(s.memory_used_mb)}/${fmt(s.memory_total_mb)} MB)`, cls(s.memory_used_pct, 70, 90)],
      ['Swap', fmt(s.swap_used_mb, ' MB'), cls(s.swap_used_mb, 20000, 40000)],
      ['Disk /', fmt(s.disk_used_pct, '%'), cls(s.disk_used_pct, 70, 90)],
      ['Load (1m/5m)', `${fmt(s.load_1m)} / ${fmt(s.load_5m)}`, cls(s.load_1m, 8, 16)],
      ['Uptime', fmt(s.uptime_days, ' days'), 'ok'],
    ]);

    html += renderCard('🔷 OpenClaw Gateway', [
      ['Status', o.running ? '● Running' : '● Down', o.running ? 'ok' : 'crit'],
      ['RSS', fmt(o.rss_mb, ' MB'), cls(o.rss_mb||0, 400, 800)],
      ['CPU', fmt(o.cpu_pct, '%'), cls(o.cpu_pct||0, 50, 90)],
      ['Uptime', fmt(o.uptime_hours, ' hrs'), 'ok'],
      ['Tool Failures', fmt(o.tool_failures), cls(o.tool_failures||0, 10, 50)],
      ['Discord Reconnects', fmt(o.discord_reconnects), cls(o.discord_reconnects||0, 20, 100)],
      ['Lane Waits', fmt(o.lane_waits), cls(o.lane_waits||0, 5, 20)],
    ]);

    html += renderCard('🧠 Brain / Cortex', [
      ['STM Entries', fmt(b.stm_entries), 'ok'],
      ['Atoms', fmt(b.atoms), 'ok'],
      ['Embeddings', fmt(b.embeddings), 'ok'],
      ['Causal Links', fmt(b.causal_links), 'ok'],
      ['Threads', fmt(b.threads), 'ok'],
      ['Categories', fmt(b.categories), 'ok'],
    ]);

    document.getElementById('grid').innerHTML = html;
  } catch(e) {
    document.getElementById('meta').textContent = 'Error: ' + e.message;
  }
}

refresh();
setInterval(refresh, 10000);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log.info(f"Starting Helios Monitor on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
