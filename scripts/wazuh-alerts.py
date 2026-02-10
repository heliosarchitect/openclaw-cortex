#!/usr/bin/env python3
"""
Wazuh-to-Discord Security Alert Pipeline
Fetches alert stats from Wazuh Manager API, summarizes by severity,
posts to Discord #system-health channel.

Designed for cron scheduling. Python3 stdlib only.
"""

import json
import os
import ssl
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
WAZUH_HOST = "https://192.168.10.143:55000"
WAZUH_USER = "wazuh-wui"
WAZUH_PASS = "wazuh-wui"

DISCORD_CHANNEL = "system-health"
DISCORD_POST_SCRIPT = os.path.expanduser("~/.openclaw/workspace/scripts/discord-post.sh")

# Wazuh alert level mapping to severity categories
# Levels 0-4: low, 5-8: medium, 9-11: high, 12+: critical
SEVERITY_THRESHOLDS = {
    "critical": 12,
    "high": 9,
    "medium": 5,
    "low": 0,
}

# ── SSL Context (self-signed cert) ─────────────────────────────────────────
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def wazuh_request(endpoint, token=None, method="GET", data=None):
    """Make a request to the Wazuh API."""
    url = f"{WAZUH_HOST}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers, method=method)

    if data:
        req.data = json.dumps(data).encode("utf-8")

    # For basic auth on the authenticate endpoint
    if not token:
        import base64
        creds = base64.b64encode(f"{WAZUH_USER}:{WAZUH_PASS}".encode()).decode()
        req.add_header("Authorization", f"Basic {creds}")

    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def authenticate():
    """Get JWT token from Wazuh API."""
    result = wazuh_request("/security/user/authenticate", method="POST")
    return result["data"]["token"]


def classify_level(level):
    """Classify a Wazuh alert level into severity category."""
    if level >= 12:
        return "critical"
    elif level >= 9:
        return "high"
    elif level >= 5:
        return "medium"
    else:
        return "low"


def get_alert_stats(token):
    """Fetch today's alert statistics from /manager/stats."""
    result = wazuh_request("/manager/stats", token=token)
    items = result["data"]["affected_items"]

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    rule_details = {}  # {sigid: {"count": N, "level": N}}
    total = 0

    for hour_data in items:
        for alert in hour_data.get("alerts", []):
            level = alert["level"]
            count = alert["times"]
            sigid = alert["sigid"]
            total += count

            sev = classify_level(level)
            severity_counts[sev] += count

            if sigid not in rule_details:
                rule_details[sigid] = {"count": 0, "level": level}
            rule_details[sigid]["count"] += count

    return {
        "total": total,
        "severity": severity_counts,
        "rules": rule_details,
    }


def get_rule_descriptions(token, rule_ids):
    """Fetch descriptions for specific rule IDs."""
    if not rule_ids:
        return {}

    ids_str = ",".join(str(r) for r in rule_ids)
    result = wazuh_request(f"/rules?rule_ids={ids_str}", token=token)

    descriptions = {}
    for rule in result["data"]["affected_items"]:
        descriptions[rule["id"]] = rule["description"]

    return descriptions


def get_agent_status(token):
    """Fetch agent connection status."""
    result = wazuh_request("/agents?select=id,name,status", token=token)
    agents = result["data"]["affected_items"]
    return agents


def get_sca_summary(token, agents):
    """Fetch SCA (Security Configuration Assessment) summaries per agent."""
    sca_results = []
    for agent in agents:
        aid = agent["id"]
        name = agent["name"]
        try:
            result = wazuh_request(f"/sca/{aid}", token=token)
            for policy in result["data"]["affected_items"]:
                sca_results.append({
                    "agent": name,
                    "policy": policy["name"],
                    "score": policy.get("score", 0),
                    "pass": policy.get("pass", 0),
                    "fail": policy.get("fail", 0),
                })
        except Exception:
            pass  # agent might not have SCA data
    return sca_results


def build_discord_message(stats, rule_descs, agents, sca_data):
    """Build a formatted Discord message."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sev = stats["severity"]
    total = stats["total"]

    lines = [f"🛡️ **Wazuh Security Report** — {now}"]
    lines.append("")

    # Agent status
    active = sum(1 for a in agents if a["status"] == "active")
    disconnected = [a["name"] for a in agents if a["status"] != "active"]
    lines.append(f"**Agents:** {active}/{len(agents)} active")
    if disconnected:
        lines.append(f"⚠️ Disconnected: {', '.join(disconnected)}")
    lines.append("")

    # Severity summary
    if total == 0:
        lines.append("✅ **0 alerts in 24h — all clear.**")
    else:
        lines.append(f"**Alert Summary** ({total} total):")

        if sev["critical"] > 0:
            lines.append(f"  🔴 Critical: **{sev['critical']}**")
        if sev["high"] > 0:
            lines.append(f"  🟠 High: **{sev['high']}**")
        if sev["medium"] > 0:
            lines.append(f"  🟡 Medium: {sev['medium']}")
        if sev["low"] > 0:
            lines.append(f"  🟢 Low: {sev['low']}")

    # Detail critical/high rules
    high_rules = {
        rid: info for rid, info in stats["rules"].items()
        if info["level"] >= 7
    }
    if high_rules:
        lines.append("")
        lines.append("**Notable Rules (level ≥ 7):**")
        # Sort by count descending
        for rid, info in sorted(high_rules.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            desc = rule_descs.get(rid, f"Rule {rid}")
            lines.append(f"  • `{rid}` {desc} — {info['count']}x (lvl {info['level']})")

    # SCA summary (only show low-scoring)
    low_sca = [s for s in sca_data if s["score"] < 50]
    if low_sca:
        lines.append("")
        lines.append("**SCA Warnings (score < 50%):**")
        for s in low_sca:
            lines.append(f"  • {s['agent']}: {s['policy']} — {s['score']}% ({s['fail']} failed checks)")

    return "\n".join(lines)


def post_to_discord(message):
    """Post message to Discord via discord-post.sh."""
    try:
        result = subprocess.run(
            [DISCORD_POST_SCRIPT, DISCORD_CHANNEL, message],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"Discord post failed: {result.stderr}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Discord post error: {e}", file=sys.stderr)
        return False


def main():
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unknown",
        "total_alerts": 0,
        "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        "agents": [],
        "notable_rules": [],
    }

    try:
        # Authenticate
        token = authenticate()

        # Gather data
        stats = get_alert_stats(token)
        agents = get_agent_status(token)
        sca_data = get_sca_summary(token, agents)

        # Get descriptions for rules with level >= 7
        high_rule_ids = [rid for rid, info in stats["rules"].items() if info["level"] >= 7]
        rule_descs = get_rule_descriptions(token, high_rule_ids)

        # Build summary
        summary["status"] = "ok"
        summary["total_alerts"] = stats["total"]
        summary["severity"] = stats["severity"]
        summary["agents"] = [
            {"name": a["name"], "status": a["status"]}
            for a in agents
        ]
        summary["notable_rules"] = [
            {
                "id": rid,
                "description": rule_descs.get(rid, f"Rule {rid}"),
                "count": info["count"],
                "level": info["level"],
            }
            for rid, info in stats["rules"].items()
            if info["level"] >= 7
        ]

        # Build and post Discord message
        message = build_discord_message(stats, rule_descs, agents, sca_data)
        posted = post_to_discord(message)
        summary["discord_posted"] = posted

    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
        # Wazuh unreachable
        summary["status"] = "offline"
        summary["error"] = str(e)
        offline_msg = (
            "🛡️ **Wazuh Security Report**\n\n"
            "🔴 **Wazuh OFFLINE** — Cannot reach API at 192.168.10.143:55000\n"
            f"Error: `{e}`\n\n"
            "Investigate: Is the Wazuh manager service running on blackview?"
        )
        post_to_discord(offline_msg)

    except Exception as e:
        summary["status"] = "error"
        summary["error"] = str(e)
        error_msg = (
            "🛡️ **Wazuh Security Report**\n\n"
            f"⚠️ **Script Error:** `{e}`\n"
            "Check logs on giggletits."
        )
        post_to_discord(error_msg)

    # Always output JSON summary to stdout
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
