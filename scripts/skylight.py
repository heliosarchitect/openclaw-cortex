#!/usr/bin/env python3
"""Skylight list & calendar CLI for Helios.

Usage:
    skylight.py lists                          — show all lists
    skylight.py list [grocery|actions|farm]     — show items in a list
    skylight.py add <list> "item" ["item2" …]   — add items to a list
    skylight.py done <list> <item_id>           — mark item complete
    skylight.py remove <list> <item_id>         — delete item
    skylight.py calendar [days=7]               — show upcoming events
    skylight.py event "title" "2026-02-14" [category] — add calendar event

Lists: grocery (4223068), actions (4223069), farm (5461677)
Categories: mlh (Matthew), jjh (Jennifer), shared
"""

import sys
import os
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("ERROR: requests module required. pip install requests", file=sys.stderr)
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────

SKYLIGHT_API = "https://app.ourskylight.com/api"
SKYLIGHT_FRAME = "4231849"

LISTS = {
    "grocery":    "4223068",
    "actions":    "4223069",
    "farm":       "5461677",
    "farm_store": "5461677",  # alias
}

CATEGORIES = {
    "mlh":    "12994209",   # Matthew
    "jjh":    "12994226",   # Jennifer
    "shared": "13067222",   # Shared / bonsaihorn@gmail.com
}

SECRETS_FILE = Path.home() / ".secrets" / "skylight.env"


# ── Auth ────────────────────────────────────────────────────────────────────

_cached_headers = None

def auth() -> dict:
    """Authenticate and return headers. Caches for session."""
    global _cached_headers
    if _cached_headers:
        return _cached_headers

    env = {}
    with open(SECRETS_FILE) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")

    r = requests.post(f"{SKYLIGHT_API}/sessions", json={
        "email": env["SKYLIGHT_EMAIL"],
        "password": env["SKYLIGHT_PASSWORD"],
        "name": "", "phone": "",
        "resettingPassword": "false",
        "textMeTheApp": "true",
        "agreedToMarketing": "true",
    })
    if r.status_code != 200:
        print(f"Auth failed: {r.status_code} {r.text[:200]}", file=sys.stderr)
        sys.exit(1)

    data = r.json()["data"]
    user_id = data["id"]
    token = data["attributes"]["token"]
    auth_b64 = base64.b64encode(f"{user_id}:{token}".encode()).decode()
    _cached_headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
    }
    return _cached_headers


# ── List Operations ─────────────────────────────────────────────────────────

def resolve_list(name: str) -> str:
    """Resolve list name to ID."""
    name_lower = name.lower()
    if name_lower in LISTS:
        return LISTS[name_lower]
    # Try partial match
    for k, v in LISTS.items():
        if k.startswith(name_lower):
            return v
    # Maybe it's already an ID
    if name.isdigit():
        return name
    print(f"Unknown list: {name}", file=sys.stderr)
    print(f"Available: {', '.join(LISTS.keys())}", file=sys.stderr)
    sys.exit(1)


def get_all_lists(headers: dict) -> dict:
    """Fetch all lists with items."""
    r = requests.get(f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists", headers=headers)
    if r.status_code != 200:
        print(f"Failed to fetch lists: {r.status_code}", file=sys.stderr)
        return {}
    data = r.json()
    included = {i["id"]: i for i in data.get("included", [])}
    result = {}
    for lst in data.get("data", []):
        list_id = lst["id"]
        list_name = lst.get("attributes", {}).get("name", f"list-{list_id}")
        items = []
        for ref in lst.get("relationships", {}).get("list_items", {}).get("data", []):
            item = included.get(ref["id"], {})
            attrs = item.get("attributes", {})
            items.append({
                "id": ref["id"],
                "label": attrs.get("label", ""),
                "status": attrs.get("status", "pending"),
                "quantity": attrs.get("quantity", 1),
            })
        result[list_id] = {"name": list_name, "items": items}
    return result


def cmd_lists():
    """Show all lists."""
    headers = auth()
    lists = get_all_lists(headers)
    # Reverse lookup
    id_to_name = {v: k for k, v in LISTS.items()}
    for list_id, data in lists.items():
        alias = id_to_name.get(list_id, "")
        pending = sum(1 for i in data["items"] if i["status"] != "completed")
        total = len(data["items"])
        print(f"  {data['name']:20s} ({list_id}) [{alias}]  — {pending} pending / {total} total")


def cmd_list(list_name: str):
    """Show items in a list."""
    headers = auth()
    list_id = resolve_list(list_name)
    lists = get_all_lists(headers)
    data = lists.get(list_id)
    if not data:
        print(f"List {list_id} not found or empty")
        return

    print(f"\n📋 {data['name']} ({list_id})")
    print("─" * 50)

    pending = [i for i in data["items"] if i["status"] != "completed"]
    completed = [i for i in data["items"] if i["status"] == "completed"]

    if not pending and not completed:
        print("  (empty)")
        return

    for item in pending:
        qty = f" x{item['quantity']}" if item["quantity"] > 1 else ""
        print(f"  ☐ {item['label']}{qty}  [{item['id']}]")

    if completed:
        print(f"\n  ── completed ({len(completed)}) ──")
        for item in completed:
            print(f"  ☑ {item['label']}  [{item['id']}]")


def cmd_add(list_name: str, *items: str):
    """Add items to a list."""
    headers = auth()
    list_id = resolve_list(list_name)

    for label in items:
        r = requests.post(
            f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists/{list_id}/list_items",
            headers=headers,
            json={"label": label, "quantity": 1},
        )
        if r.status_code == 200:
            item_id = r.json().get("data", {}).get("id", "?")
            print(f"  ✅ Added: {label} [{item_id}]")
        else:
            print(f"  ❌ Failed ({r.status_code}): {label}")


def cmd_done(list_name: str, item_id: str):
    """Mark item as completed."""
    headers = auth()
    list_id = resolve_list(list_name)

    r = requests.patch(
        f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists/{list_id}/list_items/{item_id}",
        headers=headers,
        json={"status": "completed"},
    )
    if r.status_code == 200:
        print(f"  ✅ Marked done: {item_id}")
    else:
        print(f"  ❌ Failed ({r.status_code}): {r.text[:100]}")


def cmd_remove(list_name: str, item_id: str):
    """Delete an item."""
    headers = auth()
    list_id = resolve_list(list_name)

    r = requests.delete(
        f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists/{list_id}/list_items/{item_id}",
        headers=headers,
    )
    if r.status_code == 200:
        print(f"  ✅ Removed: {item_id}")
    else:
        print(f"  ❌ Failed ({r.status_code}): {r.text[:100]}")


# ── Calendar Operations ─────────────────────────────────────────────────────

def cmd_calendar(days: int = 7):
    """Show upcoming calendar events.
    Note: Skylight calendar API is unreliable (500s).
    Use `gog cal list` instead — Skylight syncs from Google Calendar.
    """
    print("  ℹ️  Skylight calendar API is unreliable.")
    print("  Use `gog cal list` instead — Skylight syncs from Google Calendar.")


def cmd_event(title: str, date_str: str, category: str = "shared"):
    """Add a calendar event. Use `gog cal add` instead — more reliable."""
    print("  ℹ️  Use `gog cal add` for calendar events — Skylight syncs from Google Calendar.")
    print(f"  Run: gog cal add '{title}' --date '{date_str}'")


# ── JSON mode (for scripting) ───────────────────────────────────────────────

def cmd_json(list_name: str):
    """Output list as JSON (for piping)."""
    headers = auth()
    list_id = resolve_list(list_name)
    lists = get_all_lists(headers)
    data = lists.get(list_id, {"name": list_name, "items": []})
    print(json.dumps(data, indent=2))


# ── Main ────────────────────────────────────────────────────────────────────

def usage():
    print("""skylight.py — Skylight list & calendar CLI

Commands:
  lists                              Show all lists
  list <name>                        Show items (grocery|actions|farm)
  add <list> "item" ["item2" ...]    Add items
  done <list> <item_id>              Mark complete
  remove <list> <item_id>            Delete item
  json <list>                        Output as JSON
  calendar [days]                    Show upcoming events
  event "title" "YYYY-MM-DD" [cat]   Add event (cat: mlh|jjh|shared)

Lists: grocery, actions, farm
""")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()
        sys.exit(0)

    cmd = args[0].lower()

    if cmd == "lists":
        cmd_lists()
    elif cmd in ("list", "ls", "show"):
        cmd_list(args[1] if len(args) > 1 else "actions")
    elif cmd == "add":
        if len(args) < 3:
            print("Usage: skylight.py add <list> 'item' ['item2' ...]", file=sys.stderr)
            sys.exit(1)
        cmd_add(args[1], *args[2:])
    elif cmd == "done":
        if len(args) < 3:
            print("Usage: skylight.py done <list> <item_id>", file=sys.stderr)
            sys.exit(1)
        cmd_done(args[1], args[2])
    elif cmd == "remove":
        if len(args) < 3:
            print("Usage: skylight.py remove <list> <item_id>", file=sys.stderr)
            sys.exit(1)
        cmd_remove(args[1], args[2])
    elif cmd == "json":
        cmd_json(args[1] if len(args) > 1 else "actions")
    elif cmd in ("calendar", "cal"):
        days = int(args[1]) if len(args) > 1 else 7
        cmd_calendar(days)
    elif cmd == "event":
        if len(args) < 3:
            print("Usage: skylight.py event 'title' 'YYYY-MM-DD' [category]", file=sys.stderr)
            sys.exit(1)
        cat = args[3] if len(args) > 3 else "shared"
        cmd_event(args[1], args[2], cat)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        usage()
        sys.exit(1)
