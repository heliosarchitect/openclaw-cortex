#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path

ROOT = Path(os.path.expanduser("~/.openclaw/workspace/skills/task-graph"))
DB = ROOT / "graph.json"
LOCK = ROOT / ".graph.lock"

ROOT.mkdir(parents=True, exist_ok=True)

def now():
    return int(time.time())

def load():
    if not DB.exists():
        return {"nodes": {}, "edges": []}
    try:
        with open(DB, "r") as f:
            return json.load(f)
    except Exception:
        return {"nodes": {}, "edges": []}

def save(data):
    tmp = DB.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, DB)

# simple lock to avoid concurrent writes
class Lock:
    def __enter__(self):
        for _ in range(100):
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(now()).encode())
                os.close(fd)
                return
            except FileExistsError:
                time.sleep(0.05)
        # stale lock recovery
        try:
            os.remove(LOCK)
        except FileNotFoundError:
            pass
    def __exit__(self, *args):
        try:
            os.remove(LOCK)
        except FileNotFoundError:
            pass


def parse_kv(args):
    kv = {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            kv[k] = v
    return kv


def add_node(g, node_id, **attrs):
    n = g["nodes"].setdefault(node_id, {"type": attrs.pop("type", "other"), "attrs": {}, "updated": now()})
    # don't overwrite type unless provided
    if "type" in attrs:
        n["type"] = attrs.pop("type")
    n["attrs"].update(attrs)
    n["updated"] = now()


def add_edge(g, src, dst, rel, **attrs):
    g["edges"].append({"src": src, "dst": dst, "rel": rel, "attrs": attrs, "updated": now()})


def cmd_add_node(argv):
    if len(argv) < 2:
        print("Usage: graph.py add-node <id> [k=v ...]")
        return 1
    node_id = argv[1]
    kv = parse_kv(argv[2:])
    with Lock():
        g = load()
        add_node(g, node_id, **kv)
        save(g)
    print(f"✓ node '{node_id}' upserted")
    return 0


def cmd_add_edge(argv):
    if len(argv) < 4:
        print("Usage: graph.py add-edge <src> <dst> rel=<name> [k=v ...]")
        return 1
    src, dst = argv[1], argv[2]
    kv = parse_kv(argv[3:])
    rel = kv.pop("rel", None)
    if not rel:
        print("Error: rel=<name> is required")
        return 1
    with Lock():
        g = load()
        add_edge(g, src, dst, rel, **kv)
        save(g)
    print(f"✓ edge {src} -[{rel}]-> {dst}")
    return 0


def cmd_set(argv):
    if len(argv) < 2:
        print("Usage: graph.py set <id> [k=v ...]")
        return 1
    node_id = argv[1]
    kv = parse_kv(argv[2:])
    with Lock():
        g = load()
        if node_id not in g["nodes"]:
            add_node(g, node_id)
        add_node(g, node_id, **kv)
        save(g)
    print(f"✓ node '{node_id}' updated")
    return 0


def cmd_get(argv):
    if len(argv) < 2:
        print("Usage: graph.py get <id>")
        return 1
    g = load()
    n = g["nodes"].get(argv[1])
    if not n:
        print("(not found)")
        return 1
    print(json.dumps(n, indent=2))
    return 0


def cmd_neighbors(argv):
    if len(argv) < 2:
        print("Usage: graph.py neighbors <id>")
        return 1
    g = load()
    nid = argv[1]
    out = [(e["rel"], e["dst"]) for e in g["edges"] if e["src"] == nid]
    inc = [(e["rel"], e["src"]) for e in g["edges"] if e["dst"] == nid]
    print("Outgoing:")
    for rel, dst in out:
        print(f"  - {rel} -> {dst}")
    print("Incoming:")
    for rel, src in inc:
        print(f"  - {rel} <- {src}")
    return 0


def cmd_find(argv):
    # graph.py find key=status value=up type=endpoint
    kv = parse_kv(argv[1:])
    key = kv.get("key")
    val = kv.get("value")
    typ = kv.get("type")
    g = load()
    for nid, n in g["nodes"].items():
        if typ and n.get("type") != typ:
            continue
        if key is None:
            print(nid)
            continue
        v = n["attrs"].get(key)
        if val is None:
            if v is not None:
                print(nid)
        else:
            if str(v) == val:
                print(nid)
    return 0


def cmd_mermaid(argv):
    if len(argv) < 2:
        print("Usage: graph.py mermaid <id> [--depth N]")
        return 1
    nid = argv[1]
    depth = 2
    if "--depth" in argv:
        i = argv.index("--depth")
        if i+1 < len(argv):
            try:
                depth = int(argv[i+1])
            except:
                pass
    g = load()
    # BFS to depth
    seen = set([nid])
    frontier = [nid]
    for _ in range(depth):
        nxt = []
        for x in frontier:
            for e in g["edges"]:
                if e["src"] == x and e["dst"] not in seen:
                    seen.add(e["dst"]); nxt.append(e["dst"])
                if e["dst"] == x and e["src"] not in seen:
                    seen.add(e["src"]); nxt.append(e["src"])
        frontier = nxt
    print("graph TD")
    for e in g["edges"]:
        if e["src"] in seen and e["dst"] in seen:
            print(f"  {e['src']}--{e['rel']}-->{e['dst']}")
    return 0


def cmd_status(argv):
    g = load()
    counts = {}
    for n in g["nodes"].values():
        counts[n["type"]] = counts.get(n["type"], 0) + 1
    print(json.dumps({"types": counts, "nodes": len(g["nodes"]), "edges": len(g["edges"])}, indent=2))
    return 0


def cmd_suggest(argv):
    g = load()
    out = []
    ts = now()
    # endpoints up with no serves edges
    for nid, n in g["nodes"].items():
        if n.get("type") == "endpoint" and n["attrs"].get("status") == "up":
            has = any(e for e in g["edges"] if e["src"] == nid and e["rel"] == "serves")
            if not has:
                out.append(f"Link a model to endpoint {nid} ({n['attrs'].get('url')})")
    # models downloading too long
    for nid, n in g["nodes"].items():
        if n.get("type") == "model" and n["attrs"].get("status") == "downloading":
            age = ts - n.get("updated", ts)
            if age > 1800:
                out.append(f"Verify download progress for {nid}")
    # processes marked stale
    for nid, n in g["nodes"].items():
        if n.get("type") == "process" and n["attrs"].get("stale") == "true":
            out.append(f"Recheck or cleanup process {nid}")
    print("- " + "\n- ".join(out) if out else "(no suggestions)")
    return 0


CMDS = {
    "add-node": cmd_add_node,
    "add-edge": cmd_add_edge,
    "set": cmd_set,
    "get": cmd_get,
    "neighbors": cmd_neighbors,
    "find": cmd_find,
    "mermaid": cmd_mermaid,
    "status": cmd_status,
    "suggest": cmd_suggest,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print("Commands: " + ", ".join(CMDS.keys()))
        sys.exit(1)
    sys.exit(CMDS[sys.argv[1]](sys.argv[1:]))

if __name__ == "__main__":
    main()
