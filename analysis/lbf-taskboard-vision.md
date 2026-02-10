# LBF Enterprise Task Board — Vision Document

**Version:** 2.1  
**Date:** 2026-02-09  
**Author:** Helios (Writer sub-agent)  
**Status:** DRAFT — awaiting Matthew's approval

---

## 1. Purpose & Scope

### What This Board IS

The LBF Enterprise Task Board is a **single-user internal dashboard** for tracking all Lover Bear Farm initiatives across business areas. It provides:

- A hierarchical view of work: **Enterprise → Programs → Projects → Tasks**
- Kanban-style task management within each project
- A team view showing work distribution across sub-agent roles (Engineer, QA, Analyst, Writer, Builder, Researcher)
- QA report integration with automated pass/fail badges
- LCARS-themed UI consistent with the cluck-book.com design system

### What This Board IS NOT

- Not a multi-user collaboration tool (one human + one AI)
- Not a project management SaaS (no auth, no RBAC, no billing)
- Not a real-time notification system
- Not an integration hub (no Jira/GitHub/Slack sync — yet)
- Not a reporting/analytics platform (that's a future concern)

### Why Restructure

The current board already has the Enterprise → Program → Project → Task hierarchy implemented in code (`app.py` has `programs`, `projects`, and `tasks` tables with FK relationships). However:

1. **Seed data is AUGUR-centric** — BLISS and cluck-book are flat programs with no projects; Helios projects are phase-oriented but missing key workstreams (gog, Moltbook, Skills, Cortex)
2. **No proper program grouping** — BLISS sits alone as a program when it belongs under a broader R&D umbrella; cluck-book needs a Digital/Web parent
3. **Missing CRUD flows** — Program edit/archive, project edit/archive, and bulk task operations don't exist
4. **The data model works but the seed data needs a complete overhaul** to match the actual LBF organizational structure

---

## 2. Hierarchy Definition

```
LBF (Enterprise)                          ← The company. One instance. Not stored in DB.
  └── Programs (strategic business areas)  ← Stored in `programs` table
       └── Projects (functional workstreams) ← Stored in `projects` table
            └── Tasks (actionable items)    ← Stored in `tasks` table
```

### Level Definitions

| Level | Definition | Examples | Lifecycle |
|-------|-----------|----------|-----------|
| **Enterprise** | Lover Bear Farm as a whole. Implicit — not a DB entity. | LBF | Permanent |
| **Program** | A strategic business area with its own mission and budget. Programs are long-lived (years). | AUGUR, Helios, R&D, Digital | Created rarely, archived never (in practice) |
| **Project** | A functional workstream within a program. Projects have a defined scope and may complete. | Data Collection, OpenClaw, BLISS | Created as needed, status: active → completed → archived |
| **Task** | An actionable work item. Has an assignee, priority, and pipeline stage. | "Fix direction bug", "Add temporal split" | Created frequently, flows through pipeline: backlog → spec → build → verify → validate → deploy → done |

### Naming Conventions

- **Programs**: Short, capitalized names. Preferably one word. (AUGUR, Helios, R&D, Digital)
- **Projects**: Descriptive names. Can include phase indicators if phased. (Data Collection, Phase 0: Stabilization)
- **Tasks**: Imperative verb phrases. ("Fix direction bug", "Build monitoring dashboard", "Add flock lock")

---

## 3. Programs & Projects — Recommended Structure

### Program Name Recommendations

**BLISS's parent: "R&D"**

Matthew's pick. Broad enough to house future experiments beyond neural optimization — any research or experimental hardware lands here.

**cluck-book's parent: "Digital"**

Reasoning: This program covers web presence, e-commerce, and marketing — all digital channels. "Web Presence" is too narrow (excludes Etsy, social media). "Digital" is concise, industry-standard, and covers the full spectrum: websites, online stores, social marketing, SEO. It's also the only program that faces the outside world (customers, not internal tools).

### Complete Structure

```
LBF Enterprise
├── AUGUR 🔮 (#FF9900)
│   ├── Data Collection      — enhanced-collector service, websocket feeds, raw data ingestion (4.7GB DB)
│   ├── Data Aggregation     — feature engineering, orderbook depth analysis, trade flow metrics
│   ├── Pattern Discovery    — unsupervised pattern finding, GPU-accelerated (RTX 5090), statistical validation
│   ├── Crypto Trading       — paper trading engine, regime detection, position management, live trading (future)
│   └── Infrastructure       — systemd services, monitoring, database management, shared modules
│
├── Helios 🌞 (#9999FF)
│   ├── OpenClaw             — gateway config, self-modification, context optimization (H0-H3)
│   ├── gog                  — Gmail/Drive/Calendar CLI integration (Google Workspace)
│   ├── Moltbook             — social engagement, profile management
│   ├── Skills               — ClawHub skills, skill creation/publishing
│   ├── Cortex               — memory system, atoms, temporal search
│   ├── Gitea                — local Git server, repo management, issue tracking integration
│   ├── Enterprise Dashboard — this task board itself (LCARS, FastAPI, auth)
│   ├── Communications       — Discord server (LBF Operations), channel structure, branding, bot integration
│   ├── Local LLM Fleet      — Ollama Modelfiles, phi3:mini/lexi on RTX 5090, specialized tool LLMs
│   └── BC/DR                — Business Continuity & Disaster Recovery
│
├── R&D 🧠 (#FF6699)
│   └── BLISS                — Neural optimization chamber, EEG hardware, biofeedback protocols
│
└── Digital 🌐 (#66FF66)
    ├── cluck-book.com       — Cloudflare Pages website, LCARS theme
    ├── Stripe               — Payment Links, checkout customization, branding
    ├── Etsy Store           — farm products online (future)
    └── Social / Marketing   — social media, content, outreach (future)
```

### Migration from Current State

The current DB has 4 programs and 11 projects. The migration:

| Current | New |
|---------|-----|
| Program "BLISS" | Becomes **project** "BLISS" under new program "R&D" |
| Program "cluck-book" | Becomes **project** "cluck-book.com" under new program "Digital" |
| Program "AUGUR" | Keeps existing projects; add Data Collection, Data Aggregation, Pattern Discovery, Crypto Trading (replace phase-named projects with functional names) |
| Program "Helios" | Keeps H0-H3 as tasks/milestones under OpenClaw project; add gog, Moltbook, Skills, Cortex as new projects |

The AUGUR phase-named projects (Phase 0, Phase 1, etc.) should be **replaced** with functionally-named projects. Phases become metadata/tags on tasks, not project names. This matches Matthew's philosophy: the board should reflect *what work is being done*, not *when it was planned*.

---

## 4. Data Model

### Schema (SQLite)

The existing schema is already correct. No structural changes needed:

```sql
CREATE TABLE IF NOT EXISTS programs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    emoji       TEXT DEFAULT '📋',
    color       TEXT DEFAULT '#FF9900',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived    BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS projects (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id   INTEGER NOT NULL REFERENCES programs(id),
    name         TEXT NOT NULL,
    description  TEXT DEFAULT '',
    phase        TEXT DEFAULT '',        -- Legacy; keep for backward compat
    status       TEXT DEFAULT 'active',  -- active | backlog | completed | archived
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT NOT NULL,
    description    TEXT DEFAULT '',
    phase          TEXT DEFAULT '',           -- Legacy; keep for backward compat
    priority       TEXT DEFAULT 'medium',     -- critical | high | medium | low
    assigned_to    TEXT DEFAULT 'Unassigned', -- Engineer | QA | Analyst | Writer | Builder | Researcher
    pipeline_stage TEXT DEFAULT 'backlog',    -- backlog | spec | build | verify | validate | deploy | done
    project_id     INTEGER REFERENCES projects(id),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at   TIMESTAMP
);
```

### Indexes (Add)

```sql
CREATE INDEX IF NOT EXISTS idx_projects_program ON projects(program_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_stage ON tasks(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
```

### Seed Data — Complete Replacement

```python
SEED_PROGRAMS = [
    # (name, description, emoji, color)
    ("AUGUR",     "Algorithmic trading platform — data collection through live execution",  "🔮", "#FF9900"),
    ("Helios",    "AI platform — self-improvement, memory, tools, and infrastructure",      "🌞", "#9999FF"),
    ("R&D", "Research & Development — neural optimization, experimental hardware, future tech",      "🧠", "#FF6699"),
    ("Digital",   "Web presence — websites, e-commerce, marketing, and public-facing media", "🌐", "#66FF66"),
]

SEED_PROJECTS = [
    # (program_name, project_name, description, status)
    # --- AUGUR ---
    ("AUGUR", "Data Collection",    "enhanced-collector service, websocket feeds, raw data ingestion (4.7GB DB)", "active"),
    ("AUGUR", "Data Aggregation",   "Feature engineering, orderbook depth analysis, trade flow metrics",          "active"),
    ("AUGUR", "Pattern Discovery",  "Unsupervised pattern finding, GPU-accelerated (RTX 5090), statistical validation", "active"),
    ("AUGUR", "Crypto Trading",     "Paper trading engine, regime detection, position management, live trading (future)", "active"),
    ("AUGUR", "Infrastructure",     "systemd services, monitoring, database management, shared modules, tests",   "active"),

    # --- Helios ---
    ("Helios", "OpenClaw",   "Gateway config, self-modification, context optimization (H0-H3 phases)", "active"),
    ("Helios", "gog",        "Gmail/Drive/Calendar CLI integration — Google Workspace tools",          "active"),
    ("Helios", "Moltbook",   "Social engagement and profile management",                               "active"),
    ("Helios", "Skills",     "ClawHub skills, skill creation and publishing",                          "active"),
    ("Helios", "Cortex",     "Memory system — STM, embeddings, atoms, temporal search",                "active"),
    ("Helios", "Gitea",      "Local Git server — repo management, issue tracking, CI integration",     "active"),
    ("Helios", "Enterprise Dashboard", "This task board — LCARS UI, auth, Gitea issue linking",        "active"),
    ("Helios", "BC/DR",      "Business Continuity & Disaster Recovery planning",                       "backlog"),

    # --- R&D ---
    ("R&D", "BLISS",   "Neural optimization chamber — EEG hardware, biofeedback protocols, calibration", "active"),

    # --- Digital ---
    ("Digital", "cluck-book.com",      "Cloudflare Pages website — LCARS theme, farm content",          "active"),
    ("Digital", "Stripe",              "Payment Links, checkout customization, branding to match LBF",   "active"),
    ("Digital", "Etsy Store",          "Farm products online store (future)",                            "backlog"),
    ("Digital", "Social / Marketing",  "Social media presence, content strategy, outreach (future)",     "backlog"),
]
```

**No tasks are seeded.** Tasks are created as work is identified — the board should reflect real work, not speculative placeholders.

---

## 5. UI/UX Specification

### Design Principles

1. **Preserve the LCARS aesthetic** — all existing CSS classes, colors, and animations stay. The `lcars-dashboard.css` file (1,100+ lines) is the single source of truth for styling.
2. **Hierarchy = navigation depth** — the URL path mirrors the hierarchy: `/` → `/programs/{id}` → `/projects/{id}` → `/tasks/{id}`
3. **Breadcrumbs everywhere** — every page below the landing shows a clickable breadcrumb trail: `◆ LBF › 🔮 AUGUR › Data Collection`
4. **Progressive disclosure** — landing shows programs (high level), drilling down reveals more detail at each level
5. **HTMX for interactions** — form submissions, stage transitions, and modal operations use HTMX where possible to avoid full page reloads

### Navigation Flow

```
┌─────────────────────────────────────────────────┐
│  /  (Landing Page)                              │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 🔮 AUGUR │  │ 🌞 Helios│  │ 🧠 Neuro │ ... │
│  │ 5 proj   │  │ 6 proj   │  │ 1 proj   │      │
│  │ 12 open  │  │ 8 open   │  │ 3 open   │      │
│  └────┬─────┘  └──────────┘  └──────────┘      │
│       │  [+ New Program]                        │
└───────┼─────────────────────────────────────────┘
        ▼
┌─────────────────────────────────────────────────┐
│  /programs/1  (AUGUR Program Page)              │
│  ◆ LBF › 🔮 AUGUR                              │
│                                                 │
│  ACTIVE ●                                       │
│  ┌─────────────────────────────────────────┐    │
│  │ Data Collection    [active]  ██████░ 70% │    │
│  │ Pattern Discovery  [active]  ████░░░ 55% │    │
│  │ Crypto Trading     [active]  ██░░░░░ 25% │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  BACKLOG ●                                      │
│  ┌─────────────────────────────────────────┐    │
│  │ ... (none currently)                     │    │
│  └─────────────────────────────────────────┘    │
│  [+ New Project]                                │
└─────────────────────────────────────────────────┘
        ▼
┌─────────────────────────────────────────────────┐
│  /projects/1  (Project Kanban Board)            │
│  ◆ LBF › 🔮 AUGUR › Data Collection            │
│                                                 │
│  ┌────────┬────────┬────────┬────────┬────┐     │
│  │BACKLOG │ SPEC   │ BUILD  │ VERIFY │... │     │
│  │        │        │        │        │    │     │
│  │ ┌────┐ │        │ ┌────┐ │        │    │     │
│  │ │Task│ │        │ │Task│ │        │    │     │
│  │ └────┘ │        │ └────┘ │        │    │     │
│  │ ┌────┐ │        │        │        │    │     │
│  │ │Task│ │        │        │        │    │     │
│  │ └────┘ │        │        │        │    │     │
│  └────────┴────────┴────────┴────────┴────┘     │
│  [+ New Task]                                   │
└─────────────────────────────────────────────────┘
```

### Page Specifications

#### Landing Page (`/`) — EXISTS, needs minor updates

Current implementation is correct. Updates needed:
- Ensure "R&D" and "Digital" programs appear after migration
- Add a subtitle or tagline under the LBF header: "Enterprise Overview"
- No structural template changes needed

#### Program Page (`/programs/{id}`) — EXISTS, needs minor updates

Current implementation is correct. Updates needed:
- Add Edit/Archive buttons to program header (inline, not modal — keep it simple)
- Project cards already show status grouping, progress bars, and task counts ✅

#### Project Kanban Board (`/projects/{id}`) — EXISTS, works as-is

Current implementation with 7-column kanban (backlog → spec → build → verify → validate → deploy → done) is correct and should not change.

#### Task Detail (`/tasks/{id}`) — EXISTS, works as-is

Shows task metadata, QA badge, description, move controls, edit/delete buttons.

#### Task Form (`/projects/{id}/tasks/new`, `/tasks/{id}/edit`) — EXISTS, works as-is

Form with title, description, priority, assignee, pipeline stage.

#### Team Page (`/team`) — EXISTS, works as-is

Grid of sub-agent role cards with active tasks, done counts. Cross-program view.

#### QA Page (`/qa`) — EXISTS, works as-is

Scans `~/Projects/AUGUR/qa/*.md` for reports. Shows health dashboard, task verification matrix, rendered report viewer.

### New Pages / Features Needed

#### Program Edit Modal (NEW)

Triggered by an edit button on the program page header. Modal form with:
- Name (text)
- Description (text)
- Emoji (text, maxlength 4)
- Color (color picker)
- Archive toggle

#### Project Edit Modal (NEW)

Triggered by an edit button on the project kanban header. Modal form with:
- Name (text)
- Description (text)
- Status (select: active / backlog / completed / archived)

#### Global Search (NICE-TO-HAVE, not required for v2.0)

A search box in the sidebar that searches across tasks by title. Not required for initial delivery.

---

## 6. API Endpoints

### Existing Routes (keep as-is)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Landing page — all programs |
| `GET` | `/programs/{id}` | Program page — its projects |
| `POST` | `/programs/new` | Create program (form) |
| `GET` | `/projects/{id}` | Project kanban board |
| `POST` | `/projects/new` | Create project (form) |
| `GET` | `/projects/{id}/tasks/new` | New task form |
| `POST` | `/projects/{id}/tasks/new` | Create task |
| `GET` | `/tasks/{id}` | Task detail |
| `GET` | `/tasks/{id}/edit` | Edit task form |
| `POST` | `/tasks/{id}/edit` | Update task |
| `POST` | `/tasks/{id}/move` | Move task to stage |
| `POST` | `/tasks/{id}/delete` | Delete task |
| `GET` | `/team` | Team overview |
| `GET` | `/qa` | QA overview |
| `GET` | `/qa/{slug}` | QA report viewer |

### New Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/programs/{id}/edit` | Update program (name, desc, emoji, color) |
| `POST` | `/programs/{id}/archive` | Toggle program archive flag |
| `POST` | `/projects/{id}/edit` | Update project (name, desc, status) |
| `POST` | `/projects/{id}/archive` | Set project status to archived |

### API Design Notes

- All mutations use `POST` with form-encoded data (HTMX compatibility)
- All mutations redirect back to the parent page (303 See Other)
- No REST API / JSON endpoints needed — this is a server-rendered HTMX app
- HTMX `hx-post` / `hx-swap` can be added incrementally for smoother UX

---

## 7. Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | **FastAPI** (Python 3.12) | Already deployed, running on port 8090 |
| Templating | **Jinja2** via `fastapi.templating` | Already configured |
| Frontend | **HTMX 1.9.10** (CDN) | Already loaded in base.html |
| Database | **SQLite** (`tasks.db`) | File-based, same directory as app.py |
| CSS | **Custom LCARS theme** (`lcars-dashboard.css`) | 1,100+ lines, do not replace |
| Font | **Antonio** (Google Fonts) | Already loaded via CSS |
| Server | **Uvicorn** | `python app.py` or `uvicorn app:app --host 0.0.0.0 --port 8090` |
| Dependencies | `fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `markdown` | Already installed |

### File Structure

```
~/Projects/AUGUR/dashboard/
├── app.py                          # FastAPI application (single file)
├── tasks.db                        # SQLite database
├── tasks.db.bak                    # Backup
├── static/
│   ├── lcars-dashboard.css         # LCARS theme (DO NOT REPLACE)
│   └── style.css                   # (unused legacy, can ignore)
└── templates/
    ├── base.html                   # Base layout with LCARS frame, nav, header, footer
    ├── landing.html                # Program cards grid + new program modal
    ├── program.html                # Project cards with status grouping + new project modal
    ├── board.html                  # Kanban board for a project's tasks
    ├── task_detail.html            # Single task view with QA badge
    ├── task_form.html              # Create/edit task form
    ├── team.html                   # Team member cards with task assignments
    ├── phases.html                 # Legacy phases view (can be removed)
    ├── qa.html                     # QA overview dashboard
    └── qa_report.html              # Rendered QA markdown report
```

---

## 8. Migration Plan

### Step 1: Backup

```bash
cp tasks.db tasks.db.bak.$(date +%Y%m%d)
```

### Step 2: Update Seed Data in `app.py`

Replace `SEED_PROGRAMS` and `SEED_PROJECTS` with the new constants from Section 4.

### Step 3: Write Migration Function

```python
def migrate_to_v2(conn):
    """Restructure programs and projects for v2 hierarchy."""
    
    # 1. Create new programs
    conn.execute("INSERT OR IGNORE INTO programs (name, description, emoji, color) VALUES (?, ?, ?, ?)",
                 ("R&D", "Research & Development — neural optimization, experimental hardware, future tech", "🧠", "#FF6699"))
    conn.execute("INSERT OR IGNORE INTO programs (name, description, emoji, color) VALUES (?, ?, ?, ?)",
                 ("Digital", "Web presence — websites, e-commerce, marketing", "🌐", "#66FF66"))
    
    # 2. Get program IDs
    programs = {r[0]: r[1] for r in conn.execute("SELECT name, id FROM programs").fetchall()}
    
    # 3. Move BLISS from program to project under R&D
    bliss_prog_id = programs.get("BLISS")
    neurotech_id = programs.get("R&D")
    if bliss_prog_id and neurotech_id:
        # Move any tasks that were under BLISS projects
        bliss_projects = conn.execute("SELECT id FROM projects WHERE program_id = ?", (bliss_prog_id,)).fetchall()
        for (proj_id,) in bliss_projects:
            conn.execute("UPDATE projects SET program_id = ? WHERE id = ?", (neurotech_id, proj_id))
        # Create BLISS as a project if it doesn't exist
        existing = conn.execute("SELECT id FROM projects WHERE program_id = ? AND name = 'BLISS'", (neurotech_id,)).fetchone()
        if not existing:
            conn.execute("INSERT INTO projects (program_id, name, description, status) VALUES (?, ?, ?, ?)",
                         (neurotech_id, "BLISS", "Neural optimization chamber — EEG hardware, biofeedback protocols", "active"))
        # Archive the BLISS program
        conn.execute("UPDATE programs SET archived = 1 WHERE id = ?", (bliss_prog_id,))
    
    # 4. Move cluck-book from program to project under Digital
    cluck_prog_id = programs.get("cluck-book")
    digital_id = programs.get("Digital")
    if cluck_prog_id and digital_id:
        cluck_projects = conn.execute("SELECT id FROM projects WHERE program_id = ?", (cluck_prog_id,)).fetchall()
        for (proj_id,) in cluck_projects:
            conn.execute("UPDATE projects SET program_id = ? WHERE id = ?", (digital_id, proj_id))
        existing = conn.execute("SELECT id FROM projects WHERE program_id = ? AND name = 'cluck-book.com'", (digital_id,)).fetchone()
        if not existing:
            conn.execute("INSERT INTO projects (program_id, name, description, status) VALUES (?, ?, ?, ?)",
                         (digital_id, "cluck-book.com", "Cloudflare Pages website — LCARS theme, farm content", "active"))
        conn.execute("UPDATE programs SET archived = 1 WHERE id = ?", (cluck_prog_id,))
    
    # 5. Add missing Helios projects
    helios_id = programs.get("Helios")
    if helios_id:
        new_helios_projects = [
            ("gog", "Gmail/Drive/Calendar CLI integration — Google Workspace tools", "active"),
            ("Moltbook", "Social engagement and profile management", "active"),
            ("Skills", "ClawHub skills, skill creation and publishing", "active"),
            ("Cortex", "Memory system — STM, embeddings, atoms, temporal search", "active"),
        ]
        for name, desc, status in new_helios_projects:
            existing = conn.execute("SELECT id FROM projects WHERE program_id = ? AND name = ?", (helios_id, name)).fetchone()
            if not existing:
                conn.execute("INSERT INTO projects (program_id, name, description, status) VALUES (?, ?, ?, ?)",
                             (helios_id, name, desc, status))
    
    # 6. Add missing AUGUR projects (functional names)
    augur_id = programs.get("AUGUR")
    if augur_id:
        new_augur_projects = [
            ("Data Collection", "enhanced-collector service, websocket feeds, raw data ingestion (4.7GB DB)", "active"),
            ("Data Aggregation", "Feature engineering, orderbook depth analysis, trade flow metrics", "active"),
            ("Pattern Discovery", "Unsupervised pattern finding, GPU-accelerated (RTX 5090), statistical validation", "active"),
            ("Crypto Trading", "Paper trading engine, regime detection, position management, live trading (future)", "active"),
        ]
        for name, desc, status in new_augur_projects:
            existing = conn.execute("SELECT id FROM projects WHERE program_id = ? AND name = ?", (augur_id, name)).fetchone()
            if not existing:
                conn.execute("INSERT INTO projects (program_id, name, description, status) VALUES (?, ?, ?, ?)",
                             (augur_id, name, desc, status))
    
    # 7. Add Digital future projects
    if digital_id:
        future_projects = [
            ("Etsy Store", "Farm products online store (future)", "backlog"),
            ("Social / Marketing", "Social media presence, content strategy, outreach (future)", "backlog"),
        ]
        for name, desc, status in future_projects:
            existing = conn.execute("SELECT id FROM projects WHERE program_id = ? AND name = ?", (digital_id, name)).fetchone()
            if not existing:
                conn.execute("INSERT INTO projects (program_id, name, description, status) VALUES (?, ?, ?, ?)",
                             (digital_id, name, desc, status))
    
    # 8. Update AUGUR description
    conn.execute("UPDATE programs SET description = ? WHERE name = 'AUGUR'",
                 ("Algorithmic trading platform — data collection through live execution",))
    
    # 9. Update Helios description
    conn.execute("UPDATE programs SET description = ? WHERE name = 'Helios'",
                 ("AI platform — self-improvement, memory, tools, and infrastructure",))
    
    # 10. Add indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_program ON projects(program_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_stage ON tasks(pipeline_stage)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to)")
    
    conn.commit()
```

### Step 4: Add New Routes

Add `POST /programs/{id}/edit`, `POST /programs/{id}/archive`, `POST /projects/{id}/edit`, and `POST /projects/{id}/archive` to `app.py`.

### Step 5: Update Templates

- Add edit button to `program.html` header
- Add edit modal to `program.html`
- Add edit button to `board.html` header (for project editing)
- Add edit modal to `board.html`
- Remove `phases.html` (legacy, unused)

### Step 6: Verify

- Visit `http://giggletits:8090/` — should show 4 programs (AUGUR, Helios, R&D, Digital)
- BLISS and cluck-book programs should be hidden (archived)
- Click AUGUR — should show 5+ projects with functional names
- Click Helios — should show 6 projects (OpenClaw, gog, Moltbook, Skills, Cortex, BC/DR)
- Click R&D — should show 1 project (BLISS)
- Click Digital — should show 3 projects (cluck-book.com, Etsy Store, Social / Marketing)
- Existing tasks should still appear in their original projects

---

## 9. What "Done" Looks Like

### Acceptance Criteria

| # | Criterion | Test |
|---|-----------|------|
| 1 | Landing page shows exactly 4 programs: AUGUR, Helios, R&D, Digital | Visit `/`, count cards |
| 2 | BLISS and cluck-book programs are not visible (archived) | Visit `/`, verify absence |
| 3 | AUGUR has ≥5 projects including Data Collection, Pattern Discovery, Infrastructure | Visit `/programs/{augur_id}` |
| 4 | Helios has ≥8 projects including OpenClaw, gog, Moltbook, Skills, Cortex, Gitea, Enterprise Dashboard, BC/DR | Visit `/programs/{helios_id}` |
| 5 | R&D has 1 project: BLISS | Visit `/programs/{rd_id}` |
| 6 | Digital has 4 projects: cluck-book.com, Stripe, Etsy Store, Social / Marketing | Visit `/programs/{digital_id}` |
| 7 | Breadcrumbs work at every level (LBF → Program → Project → Task) | Navigate deep, click each crumb |
| 8 | Creating a new program from landing page works | Click "+ New Program", fill form, verify |
| 9 | Creating a new project from program page works | Click "+ New Project", fill form, verify |
| 10 | Creating a new task from project board works | Click "+ New Task", fill form, verify |
| 11 | Task kanban board shows 7 columns (backlog→done) with drag or button-move | Visit any project with tasks |
| 12 | Editing a program (name, desc, emoji, color) works | Use edit modal, verify changes |
| 13 | Editing a project (name, desc, status) works | Use edit modal, verify changes |
| 14 | Team page shows tasks across all programs | Visit `/team`, verify cross-program tasks |
| 15 | QA page still works (reads from `~/Projects/AUGUR/qa/`) | Visit `/qa` |
| 16 | Existing tasks survive migration (no data loss) | Check task count before/after |
| 17 | LCARS CSS is unchanged | Diff `lcars-dashboard.css` before/after — should be identical |
| 18 | Auto-refresh (30s) still works | Wait, observe reload |
| 19 | Mobile responsive layout still works | Resize browser to <768px |
| 20 | Server starts without errors | `python app.py`, check stdout |
| 21 | Basic auth blocks unauthenticated access | `curl http://giggletits:8090/` returns 401 |
| 22 | Basic auth allows access with credentials | `curl -u admin:pass http://giggletits:8090/` returns 200 |
| 23 | Projects with `gitea_repo` show link to Gitea | Set repo on a project, verify link appears |
| 24 | Gitea repos created for software projects | Verify repos exist at `https://gitea.fleet.wood/lbf/` |

---

## 10. Authentication (NEW — v2.1)

The board displays sensitive project data and is on the local network. Auth is required.

### Phase 1: Basic Auth (ship with v2.1)

- Add HTTP Basic Auth directly in FastAPI using `fastapi.security.HTTPBasic`
- Single hardcoded user/password (stored in env var or `.env` file, NOT in code)
- Protect all routes except `/health` (for monitoring)
- Session cookie so you don't re-auth every page load (use `starlette.middleware.sessions`)

```python
# Example implementation
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets, os

security = HTTPBasic()
ADMIN_USER = os.getenv("BOARD_USER", "admin")
ADMIN_PASS = os.getenv("BOARD_PASS")  # MUST be set, no default

def verify(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username, ADMIN_USER) and 
            secrets.compare_digest(credentials.password, ADMIN_PASS)):
        raise HTTPException(status_code=401, detail="Unauthorized",
                          headers={"WWW-Authenticate": "Basic"})
    return credentials.username
```

### Phase 2: Gitea OAuth (future)

- Use Gitea as OAuth2 provider for SSO across board + Gitea
- Not required for initial delivery

---

## 11. Gitea Integration (NEW — v2.1)

Gitea is running at `https://gitea.fleet.wood` (v1.23.6, self-signed cert). Software projects should link to Gitea repos and issues.

### What Gitea Provides

- **Issue tracking** with labels, milestones, kanban boards
- **Git repos** for all code projects
- **API** (`/api/v1/`) for automation
- **Webhooks** for event-driven updates

### Integration Plan

#### Step 1: Create Repos in Gitea

Create repos for each software project that has code:

| Program | Project | Gitea Repo |
|---------|---------|------------|
| AUGUR | Data Collection | `augur-collector` |
| AUGUR | Pattern Discovery | `augur-discovery` |
| AUGUR | Crypto Trading | `augur-trading` |
| AUGUR | Infrastructure | `augur-infra` |
| Helios | OpenClaw | (upstream — `openclaw/openclaw`) |
| Helios | Enterprise Dashboard | `lbf-dashboard` |
| Helios | Cortex | `cortex` |
| R&D | BLISS | `bliss` |
| Digital | cluck-book.com | `cluck-book` |

Non-software projects (Stripe, Etsy, Marketing, gog, Moltbook, Skills, BC/DR) don't need repos.

#### Step 2: Add `gitea_repo` Column to Projects Table

```sql
ALTER TABLE projects ADD COLUMN gitea_repo TEXT DEFAULT '';
-- e.g., 'augur-collector' → links to https://gitea.fleet.wood/{org}/{repo}
```

#### Step 3: Link Issues from Dashboard

When a project has a `gitea_repo` set:
- Show a "View Issues" link on the project page pointing to Gitea
- Optionally pull open issue count via Gitea API (`GET /api/v1/repos/{owner}/{repo}/issues?state=open`)
- Display issue count badge on project cards

#### Step 4: Gitea Cleanup (prerequisite)

Before creating repos, audit existing Gitea state:
- List existing repos/orgs
- Create an `lbf` org if it doesn't exist
- Clean up any stale repos

### Non-Goals for Gitea Integration

- No bi-directional sync (board tasks ≠ Gitea issues — they serve different levels)
- No automatic issue creation from board tasks
- No commit-to-task linking (keep it simple)
- Gitea is the source of truth for code issues; the board is the source of truth for program/project health

---

## 12. Discord Integration & LBF Branding (NEW — v2.1)

### Purpose

Discord serves as the **structured async output channel** for LBF Operations. Signal remains the direct conversation line between Matthew and Helios; Discord provides organized, browsable channels for reports, alerts, and operational logs.

### Server Structure

**LBF Operations** (Guild ID: `1470466123123265599`)

| Category | Channel | Purpose |
|----------|---------|---------|
| 🔮 AUGUR | `#trading-alerts` | Paper/live trading signals, regime changes |
| | `#pattern-discovery` | New patterns, GPU discovery runs, validation results |
| | `#daily-report` | Daily P/L summaries, win rates, performance metrics |
| 🌞 Helios | `#sub-agent-reports` | Completed sub-agent work: builds, analyses, QA |
| | `#system-health` | Service status, heartbeat results, infrastructure alerts |
| | `#memory-log` | Cortex updates, atoms created, knowledge graph changes |
| 📋 Operations | `#daily-summary` | End-of-day LBF enterprise summary across all programs |
| | `#email-alerts` | Important emails (Twilio, customers, real humans) |

### LBF Branding

All LBF surfaces should present a consistent brand identity:

- **Discord**: Custom server icon (LBF logo), banner, LCARS-inspired role colors, bot avatar for Helios (🌞), welcome message
- **Task Board**: Already LCARS-themed; branding should be consistent with Discord and cluck-book.com
- **cluck-book.com**: Source of truth for brand assets (colors, fonts, logo)
- **Gitea**: Organization avatar matches LBF branding

### Technical Pattern

Cross-context messaging (Signal → Discord) is blocked by OpenClaw's session binding. Workaround: direct Discord API calls via `scripts/discord-post.sh` using `DISCORD_BOT_TOKEN` from `~/.secrets/discord.env`. This is the correct pattern for output-only channels.

Future: OpenClaw Discord session can respond natively to messages received on Discord.

---

## 13. Non-Goals (v2.1)

These are explicitly **out of scope** for this version:

1. ~~Authentication / authorization~~ — **NOW IN SCOPE (Section 10)**
2. **Multi-user / collaboration** — one human + one AI
3. ~~External integrations~~ — **Gitea NOW IN SCOPE (Section 11)**; no Jira, Slack, or email sync
4. **Notifications** — no email/push alerts for task changes
5. **Time tracking** — no hours logged, no burndown charts
6. **File attachments** — tasks have text descriptions only
7. **Comments / activity log** — no comment threads on tasks
8. **Drag-and-drop kanban** — button-based stage moves are sufficient (HTMX drag is a nice-to-have for later)
9. **Reporting / analytics** — no velocity charts, cycle time, or throughput graphs
10. **Task dependencies** — no blocking/blocked-by relationships
11. **Custom fields** — fixed schema, no user-defined metadata
12. **Automated testing** — no pytest for the dashboard itself (focus testing effort on AUGUR trading engine)
13. **Archiving phase-named AUGUR projects** — keep Phase 0, Phase 1, etc. for now; they have tasks attached. Can be cleaned up later after tasks are re-homed.

---

## Appendix A: Current Codebase Audit

### What Already Works ✅

- Full Enterprise → Program → Project → Task hierarchy with FK relationships
- Landing page with program cards showing project counts and task stats
- Program page with project cards, status grouping, progress bars
- Project-level kanban board with 7 pipeline stages
- Task CRUD (create, read, update, delete, move)
- Breadcrumb navigation (LBF → Program → Project)
- Team page with cross-program task assignments
- QA report engine scanning markdown files for pass/fail badges
- LCARS theme with responsive mobile layout
- Auto-refresh every 30 seconds
- Modals for creating programs and projects

### What Needs Work 🔧

- Seed data restructuring (BLISS/cluck-book as programs → projects)
- Missing Helios projects (gog, Moltbook, Skills, Cortex)
- Missing AUGUR functional projects (Data Collection, Data Aggregation, etc.)
- Program edit/archive functionality
- Project edit functionality
- `phases.html` template is unused — delete it

### What's Clean 🧹

- Single-file backend (`app.py`) — easy to modify
- CSS is well-organized with clear section headers
- Templates use proper Jinja2 inheritance
- Database uses `contextmanager` for connection management
- No external dependencies beyond FastAPI ecosystem

---

## Appendix B: LCARS Color Reference

For any new UI elements, use these existing CSS variables:

| Variable | Hex | Usage |
|----------|-----|-------|
| `--lcars-orange` | `#ff9933` | Headers, primary accent, phase titles |
| `--lcars-gold` | `#ffcc66` | Labels, secondary accent, form labels |
| `--lcars-peach` | `#ffcc99` | Hover states, tertiary accent |
| `--lcars-purple` | `#664466` | Dark accents, footer, separators |
| `--lcars-lilac` | `#cc99cc` | Sidebar top, header elbow |
| `--lcars-blue` | `#99ccff` | Primary text, buttons, active nav |
| `--lcars-navy` | `#3366cc` | Footer end block |
| `--lcars-teal` | `#006699` | Borders, column headers |
| `--lcars-green` | `#99dd66` | QA pass, success states |
| `--lcars-red` | `#cc4444` | QA fail, danger, delete |
| `--lcars-bg` | `#000000` | Background |
| `--lcars-text` | `#99ccff` | Default text color |

Program-specific colors (used in `color` column):
- AUGUR: `#FF9900`
- Helios: `#9999FF`
- R&D: `#FF6699`
- Digital: `#66FF66`
