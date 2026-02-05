# Task Graph Schema

Minimal JSON structure stored at `skills/task-graph/graph.json`.

```json
{
  "nodes": {
    "node_id": {
      "type": "endpoint|model|env|process|file|script|db|person|service|task|other",
      "attrs": { "key": "value" },
      "updated": 1738700000
    }
  },
  "edges": [
    { "src": "a", "dst": "b", "rel": "uses|depends-on|serves|runs-on|exposes|blocks|produces|owned-by", "attrs": {}, "updated": 1738700000 }
  ]
}
```

Notes:
- IDs are unique strings (snake_case). Keep stable.
- `updated` is a Unix timestamp (seconds).
- Attributes are free-form; prefer small, composable keys.
- Relationship direction: choose the intuitive read, e.g. `endpoint serves model` or `bot uses db`.
