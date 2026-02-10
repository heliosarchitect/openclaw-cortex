# LBF Enterprise Task Board — Rebuild Summary

**Date:** 2026-02-09
**Status:** Complete

## What Changed

### Data Model
The flat AUGUR task board was restructured into a 3-level hierarchy:

```
LBF (enterprise)
├── Programs (AUGUR, Helios, BLISS, cluck-book)
│   └── Projects (Phase 0, Phase 1, H0: Injection Bloat, etc.)
│       └── Tasks (unchanged task model + project_id FK)
```

**New tables:**
- `programs` — name, description, emoji, color, archived flag
- `projects` — program_id FK, name, description, phase, status

**Modified table:**
- `tasks` — added `project_id` column (nullable FK to projects)

### Seed Data
- 4 programs: AUGUR (🔮), Helios (🌞), BLISS (🧠), cluck-book (🐔)
- 6 projects: AUGUR Phase 0/1/2, Helios H0/H1/H2
- Each program has a unique LCARS accent color

### Migration
- All 16 existing tasks preserved (zero data loss)
- Tasks mapped to AUGUR projects by phase:
  - Phase 0 tasks → AUGUR > Phase 0 (12 tasks)
  - Phase 1 tasks → AUGUR > Phase 1 (2 tasks)
  - Phase 2 tasks → AUGUR > Phase 2 (2 tasks)
- DB backup saved as `tasks.db.bak`

### UI Changes

| Page | Route | Description |
|------|-------|-------------|
| LBF Landing | `GET /` | Program cards with stats (projects, open/done tasks) |
| Program | `GET /programs/{id}` | Project list grouped by status (active/backlog/completed) |
| Project Board | `GET /projects/{id}` | Kanban board (unchanged pipeline columns) |
| Task Detail | `GET /tasks/{id}` | Full detail with program/project context |
| Task Form | `GET /projects/{id}/tasks/new` | Create task under specific project |
| Team | `GET /team` | Global team view (shows program emoji per task) |
| QA | `GET /qa` | Unchanged |

**Breadcrumb navigation** on every page: `◆ LBF › 🔮 AUGUR › Phase 0 › Task #1`

**Program accent colors** apply to:
- Header bar (elbow + bar change color per program)
- Kanban column headers
- Project card indicators

**Modals** for "Add Program" and "Add Project" (no page navigation needed)

### Files Modified
1. `app.py` — New schema, migration logic, enterprise routes
2. `templates/base.html` — Hierarchy-aware header, breadcrumb block, updated nav
3. `templates/landing.html` — **NEW** — LBF program overview
4. `templates/program.html` — **NEW** — Projects under a program
5. `templates/board.html` — Now project-scoped kanban board
6. `templates/task_detail.html` — Added program/project context + breadcrumbs
7. `templates/task_form.html` — Simplified (phase removed, project-scoped)
8. `templates/team.html` — Shows program emoji per task
9. `templates/qa.html` — Added breadcrumbs
10. `templates/qa_report.html` — Added breadcrumbs
11. `static/lcars-dashboard.css` — Added breadcrumb, program card, project card, modal styles

### What Was Preserved
- LCARS CSS theme (all existing styles intact)
- All task functionality (detail, edit, move, delete, QA badges)
- QA report integration (scan, render, badges)
- Team page
- Port 8090
- SQLite DB path
- HTMX-only (no JS frameworks)
- Auto-refresh (30s)
- Star field background animation

### Routes Removed
- `GET /phases` — replaced by program/project hierarchy (template kept for reference)

### How to Restart
```bash
cd ~/Projects/AUGUR/dashboard
python3 -m uvicorn app:app --host 0.0.0.0 --port 8090
```
