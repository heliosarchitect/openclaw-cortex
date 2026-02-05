---
name: task-graph
description: Maintain a lightweight knowledge graph of systems, APIs, models, environments, processes, and tasks to improve coherence and recall. Use to record endpoints, credentials locations, model availability, PIDs, dependencies, and decisions; query relationships; and generate next-step suggestions.
---

# Task Graph Skill

This skill gives you a simple graph database for operational memory. It helps prevent context slips (e.g., forgetting API endpoints or model locations) by:

- Capturing entities: tools, endpoints, envs, models, scripts, PIDs, files, configs, people
- Linking relationships: uses, depends-on, runs-on, exposes, blocks, produces, owned-by
- Attaching attributes: url, port, path, version, status, freshness, notes
- Answering queries and generating suggestions

Data store: `graph.json` (JSON) with a tiny CLI (`scripts/graph.py`). No external deps.

## Quick Start

- Add nodes:
  - `graph.py add-node oai_local type=endpoint url=http://localhost:5000 kind=openai status=up`
  - `graph.py add-node qwen32 type=model family=qwen2.5 size=32b quant=q4_k_m status=downloading`
- Link them:
  - `graph.py add-edge oai_local qwen32 rel=serves`
- Show neighborhood:
  - `graph.py neighbors oai_local`
- Render mermaid:
  - `graph.py mermaid oai_local --depth 2 > /tmp/graph.mmd`
- Suggest next steps:
  - `graph.py suggest`

## Commands

- `add-node <id> [k=v ...]`
- `add-edge <src> <dst> rel=<name> [k=v ...]`
- `set <id> [k=v ...]` (update attrs)
- `get <id>`
- `neighbors <id>`
- `find key=<k> [value=<v>] [type=<t>]`
- `mermaid <id> [--depth N]` (outputs a Mermaid graph)
- `status` (high-level summary)
- `suggest` (heuristic next actions)

## Heuristics (suggest)

- Endpoints with status=up and no models linked → suggest linking or loading a model
- Models with status=downloading older than 30 min → suggest verifying progress
- Processes (type=process) with stale=true → suggest recheck/cleanup
- Trading bot below WR threshold → suggest inspect last_10 trades

## Files

- Data: `graph.json`
- CLI: `scripts/graph.py`
- Schema reference: `references/schema.md`

Keep entries concise; prefer stable IDs (snake_case). Use attributes instead of long notes when possible.
