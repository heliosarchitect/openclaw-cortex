# AGENTS.md

## Memory
- **Cortex FIRST** — STM + embeddings + atoms = primary memory
- Daily logs: `memory/YYYY-MM-DD.md` | Task queue: `memory/task-queue.md`
- Write it down. Mental notes don't survive restarts.

## Safety
- `trash` > `rm` | Ask before external actions | Internal actions are free

## Groups
- Speak when you add value. You're a participant, not Matthew's voice.

## Nova Pattern
- Every session: pull tasks, dispatch Nova in parallel (60s/spawn, 2hr budget)
- Check results during heartbeats, not auto-announced

## Pre-Reset Sweep
When context > 80%: update daily log, cortex dump, note pending work.

## CI/CD
- Repos get `.gitea/workflows/test.yaml` | Run tests before commit
- Gitea token: `~/.secrets/gitea-helios-token.txt`
