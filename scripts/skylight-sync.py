#!/usr/bin/env python3
"""
Skylight ↔ Discord ↔ Task Board sync engine.

Heartbeat-driven:
1. Poll Discord #matthew-tasks for new posts → mirror to Skylight LBF Actions
2. Poll Skylight LBF Actions for completed items → update task board + notify
3. State tracked in skylight-sync-state.json to avoid duplicates
"""

import json, os, sys, base64, re, subprocess
import requests
from pathlib import Path

# --- Config ---
SKYLIGHT_API = "https://app.ourskylight.com/api"
SKYLIGHT_FRAME = "4231849"
SKYLIGHT_LISTS = {
    "grocery": "4223068",
    "actions": "4223069",  # LBF Actions (Matthew's work tasks)
    "farm_store": "5461677",  # Farm Store (feed, hardware, farm supplies)
}

# Jennifer sees: Grocery, Farm Store
# Matthew sees: Grocery, Farm Store, LBF Actions
JENNIFER_LISTS = ["grocery", "farm_store"]
MATTHEW_LISTS = ["grocery", "farm_store", "actions"]
SKYLIGHT_CATEGORIES = {
    "mlh": "12994209",      # Matthew
    "jjh": "12994226",      # Jennifer
    "shared": "13067222",   # bonsaihorn@gmail.com
}

DISCORD_TASKS_CHANNEL = "1470495480608985172"  # #matthew-tasks

STATE_FILE = Path(os.path.expanduser("~/.openclaw/workspace/data/skylight-sync-state.json"))

# --- Auth ---
def skylight_auth():
    """Get Skylight auth headers."""
    env = {}
    with open(os.path.expanduser("~/.secrets/skylight.env")) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                env[k] = v
    
    r = requests.post(f"{SKYLIGHT_API}/sessions", json={
        "email": env["SKYLIGHT_EMAIL"],
        "password": env["SKYLIGHT_PASSWORD"],
        "name": "", "phone": "",
        "resettingPassword": "false",
        "textMeTheApp": "true",
        "agreedToMarketing": "true"
    })
    data = r.json()["data"]
    user_id = data["id"]
    token = data["attributes"]["token"]
    auth_b64 = base64.b64encode(f"{user_id}:{token}".encode()).decode()
    return {"Authorization": f"Basic {auth_b64}", "Content-Type": "application/json"}

def discord_headers():
    """Get Discord bot headers."""
    env = {}
    with open(os.path.expanduser("~/.secrets/discord.env")) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v.strip('"').strip("'")
    return {"Authorization": f"Bot {env.get('DISCORD_BOT_TOKEN', '')}", "Content-Type": "application/json"}

# --- State ---
def load_state():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"synced_discord_msgs": [], "known_skylight_items": {}}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# --- Skylight Operations ---
def get_skylight_list(headers, list_id):
    """Get all items from a Skylight list."""
    r = requests.get(f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists", headers=headers)
    data = r.json()
    included = {i["id"]: i for i in data.get("included", [])}
    
    for l in data["data"]:
        if l["id"] == list_id:
            items = []
            for ref in l["relationships"]["list_items"]["data"]:
                item = included.get(ref["id"], {})
                attrs = item.get("attributes", {})
                items.append({
                    "id": ref["id"],
                    "label": attrs.get("label", ""),
                    "status": attrs.get("status", "pending"),
                })
            return items
    return []

def add_skylight_item(headers, list_id, label):
    """Add an item to a Skylight list."""
    r = requests.post(
        f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists/{list_id}/list_items",
        headers=headers,
        json={"label": label, "quantity": 1}
    )
    if r.status_code == 200:
        return r.json()["data"]["id"]
    return None

def delete_skylight_item(headers, list_id, item_id):
    """Delete an item from a Skylight list."""
    r = requests.delete(
        f"{SKYLIGHT_API}/frames/{SKYLIGHT_FRAME}/lists/{list_id}/list_items/{item_id}",
        headers=headers
    )
    return r.status_code == 200

# --- Discord Operations ---
def get_discord_tasks(headers, limit=20):
    """Get recent messages from #matthew-tasks."""
    r = requests.get(
        f"https://discord.com/api/v10/channels/{DISCORD_TASKS_CHANNEL}/messages?limit={limit}",
        headers=headers
    )
    if r.status_code == 200:
        return r.json()
    return []

def extract_task_title(content):
    """Extract task title from Discord message format."""
    # Match: 🟡 **#23: Find Wazuh...**
    m = re.search(r'\*\*#?\d+:?\s*(.+?)\*\*', content)
    if m:
        return m.group(1).strip()
    # Fallback: first line
    first_line = content.split("\n")[0].strip()
    # Remove emoji prefix
    first_line = re.sub(r'^[🟡🔴🟢⚪]\s*', '', first_line)
    return first_line[:80] if first_line else None

# --- Sync Logic ---
def sync_discord_to_skylight(sky_headers, disc_headers, state):
    """Mirror new Discord tasks to Skylight LBF Actions."""
    messages = get_discord_tasks(disc_headers)
    new_synced = []
    
    for msg in reversed(messages):  # oldest first
        msg_id = msg["id"]
        if msg_id in state["synced_discord_msgs"]:
            continue
        
        # Only sync bot messages (task posts from Helios)
        if not msg.get("author", {}).get("bot", False):
            state["synced_discord_msgs"].append(msg_id)
            continue
            
        title = extract_task_title(msg["content"])
        if title:
            # Check if already on Skylight (by label match)
            existing = get_skylight_list(sky_headers, SKYLIGHT_LISTS["actions"])
            already_exists = any(title.lower() in item["label"].lower() or 
                               item["label"].lower() in title.lower() 
                               for item in existing)
            
            if not already_exists:
                item_id = add_skylight_item(sky_headers, SKYLIGHT_LISTS["actions"], title)
                if item_id:
                    new_synced.append(title)
                    print(f"📋→🖼️ Synced to Skylight: {title} (ID: {item_id})")
        
        state["synced_discord_msgs"].append(msg_id)
    
    # Keep only last 100 message IDs
    state["synced_discord_msgs"] = state["synced_discord_msgs"][-100:]
    return new_synced

def check_skylight_completions(sky_headers, state):
    """Check for newly completed items on Skylight."""
    items = get_skylight_list(sky_headers, SKYLIGHT_LISTS["actions"])
    completed = []
    
    known = state.get("known_skylight_items", {})
    
    for item in items:
        prev_status = known.get(item["id"], {}).get("status", "pending")
        if item["status"] == "completed" and prev_status != "completed":
            completed.append(item)
            print(f"✅ Completed on Skylight: {item['label']}")
        
        known[item["id"]] = {"label": item["label"], "status": item["status"]}
    
    state["known_skylight_items"] = known
    return completed

# --- List Classification (for Jennifer/Matthew voice commands) ---
def classify_list_item(text):
    """Determine which list an item belongs to based on context.
    Returns: 'grocery', 'actions', or 'ask'
    """
    text_lower = text.lower()
    
    grocery_signals = [
        # Food
        'milk', 'bread', 'eggs', 'butter', 'cheese', 'chicken', 'beef', 'pork',
        'rice', 'pasta', 'cereal', 'fruit', 'vegetable', 'apple', 'banana',
        'lettuce', 'tomato', 'onion', 'potato', 'carrot', 'broccoli',
        # Drinks
        'juice', 'soda', 'water', 'coffee', 'tea', 'beer', 'wine',
        # Household consumables
        'soap', 'shampoo', 'toothpaste', 'toilet paper', 'paper towel',
        'detergent', 'bleach', 'sponge', 'trash bag',
        # Hygiene
        'deodorant', 'floss', 'dental', 'shaving',
        # Grocery-store food items
        'popcorn', 'snack', 'frozen', 'canned', 'sauce', 'seasoning',
        'tortilla', 'shell', 'wrap', 'pickle', 'condiment',
    ]
    
    farm_store_signals = [
        # Animal feed & supplies
        'feed', 'grain', 'hay', 'scratch', 'pellet', 'straw', 'bedding',
        'goat feed', 'chicken feed', 'duck feed', 'layer feed',
        'waterer', 'feeder', 'heat lamp', 'brooder',
        # Farm hardware
        'fence', 'post', 'wire', 'gate', 'hose', 'nozzle',
        'tractor', 'mower', 'chain', 'rope', 'bolt', 'nut',
        'tire', 'battery', 'fuel', 'oil',
        # Garden / land
        'seed', 'fertilizer', 'mulch', 'soil', 'lime', 'compost',
        'salt block', 'mineral', 'supplement',
        # Farm store context
        'rural king', 'tractor supply', 'farm store', 'co-op',
        'timothy', 'alfalfa',
    ]
    
    action_signals = [
        # Tasks
        'call', 'email', 'fix', 'repair', 'clean', 'organize', 'schedule',
        'set up', 'install', 'update', 'check', 'review', 'submit',
        'renew', 'cancel', 'return', 'find', 'look into', 'research',
        # Physical tasks  
        'mow', 'trim', 'paint', 'build', 'move', 'haul', 'dig',
        # Admin
        'license', 'registration', 'appointment', 'meeting', 'deadline',
        'pay', 'bill', 'invoice', 'tax',
    ]
    
    grocery_score = sum(1 for s in grocery_signals if s in text_lower)
    farm_score = sum(1 for s in farm_store_signals if s in text_lower)
    action_score = sum(1 for s in action_signals if s in text_lower)
    
    best = max(grocery_score, farm_score, action_score)
    if best == 0:
        return "ask"
    if grocery_score == best and grocery_score > farm_score and grocery_score > action_score:
        return "grocery"
    elif farm_score == best and farm_score > grocery_score and farm_score > action_score:
        return "farm_store"
    elif action_score == best and action_score > grocery_score and action_score > farm_score:
        return "actions"
    else:
        return "ask"

# --- Main ---
def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "sync"
    
    if action == "sync":
        state = load_state()
        sky_h = skylight_auth()
        disc_h = discord_headers()
        
        new_tasks = sync_discord_to_skylight(sky_h, disc_h, state)
        completed = check_skylight_completions(sky_h, state)
        
        save_state(state)
        
        if not new_tasks and not completed:
            print("No changes")
        
        # Return structured result for heartbeat consumption
        result = {"new_tasks": new_tasks, "completed": [c["label"] for c in completed]}
        if new_tasks or completed:
            print(json.dumps(result))
    
    elif action == "classify":
        text = " ".join(sys.argv[2:])
        result = classify_list_item(text)
        print(f"{result}: {text}")
    
    elif action == "add":
        list_name = sys.argv[2] if len(sys.argv) > 2 else "ask"
        label = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        
        if not label:
            print("Usage: skylight-sync.py add <grocery|actions> <label>")
            sys.exit(1)
        
        if list_name == "auto":
            list_name = classify_list_item(label)
            if list_name == "ask":
                print(f"ASK: Can't determine list for '{label}'. Grocery or LBF Actions?")
                sys.exit(2)
        
        sky_h = skylight_auth()
        list_id = SKYLIGHT_LISTS.get(list_name)
        if not list_id:
            print(f"Unknown list: {list_name}")
            sys.exit(1)
        
        item_id = add_skylight_item(sky_h, list_id, label)
        if item_id:
            list_display = "Grocery List" if list_name == "grocery" else "LBF Actions"
            print(f"✅ Added '{label}' to {list_display}")
        else:
            print(f"❌ Failed to add '{label}'")
    
    elif action == "status":
        sky_h = skylight_auth()
        for name, lid in SKYLIGHT_LISTS.items():
            items = get_skylight_list(sky_h, lid)
            pending = [i for i in items if i["status"] != "completed"]
            done = [i for i in items if i["status"] == "completed"]
            print(f"\n📋 {name.title()} ({len(pending)} pending, {len(done)} done)")
            for i in pending:
                print(f"  ⬜ {i['label']}")
    
    else:
        print("Usage: skylight-sync.py <sync|classify|add|status>")

if __name__ == "__main__":
    main()
