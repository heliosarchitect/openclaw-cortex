# LBF Enterprise Dashboard — Bottleneck Tracking & Tool→Infrastructure Graduation

## System Overview

```
Dependency Graph Builder → Critical Path Analyzer → Bottleneck Detector
        ↓                          ↓                       ↓
Task Relationships DB ←→ Dashboard UI ←→ Graduation Evaluator
        ↓                          ↓                       ↓
Alert System ←────────── Metrics Engine ←──────── Tool Registry
```

## Core Components

### Bottleneck Detection Engine
- **Purpose:** Identifies tasks that block multiple downstream dependencies
- **File:** `bottleneck-detector.js`
- **Runs as:** Background service (updates every 15 minutes)
- **Algorithm:** 
  - Build dependency graph from task relationships
  - Calculate fan-out coefficient (# of downstream tasks)
  - Weight by downstream task priorities and deadlines
  - Flag tasks with coefficient > threshold as bottlenecks

### Critical Path Analyzer
- **Purpose:** Visualizes longest path through project dependencies
- **File:** `critical-path.js`
- **Runs as:** On-demand calculation triggered by UI
- **Algorithm:**
  - Modified CPM (Critical Path Method) for task networks
  - Account for resource constraints (assignee availability)
  - Factor in task complexity estimates and historical velocity

### Tool→Infrastructure Graduation Evaluator
- **Purpose:** Determines when ad-hoc tools should become permanent infrastructure
- **File:** `graduation-evaluator.js`
- **Runs as:** Weekly evaluation cron job
- **Criteria:** Uses multi-factor scoring system (detailed below)

## Bottleneck Identification Logic

### 1. Dependency Graph Construction
```javascript
// Task relationships are inferred from:
// - Explicit dependencies (when supported by LBF API)
// - Implicit dependencies (same assignee, sequential priorities)
// - Cross-project dependencies (shared resources/deliverables)

const dependencyTypes = {
  BLOCKING: 'task A must complete before B starts',
  RESOURCE: 'same assignee working sequential tasks',
  DELIVERABLE: 'task A output required for task B input'
}
```

### 2. Bottleneck Scoring Formula
```
Bottleneck Score = (Downstream Count × Priority Weight × Time Criticality)
                   / (Task Complexity × Assignee Availability)

Where:
- Downstream Count: Number of tasks waiting on this one
- Priority Weight: critical=4, high=3, medium=2, low=1
- Time Criticality: Days overdue / Planned duration (capped at 2.0)
- Task Complexity: Estimated effort (default: 1.0 if unknown)
- Assignee Availability: Current workload factor (0.5-2.0)
```

### 3. Alert Thresholds
- **Level 1** (Score > 10): Yellow warning in dashboard
- **Level 2** (Score > 20): Red alert + assignee notification
- **Level 3** (Score > 40): Critical alert + program manager notification

## Critical Path Visualization

### Dashboard Interface
```
Program View:
├── Critical Path Timeline (Gantt-style)
├── Bottleneck Heat Map (task cards with color coding)
├── Resource Allocation View (assignee workload)
└── Dependency Network Graph (interactive D3.js visualization)

Task Card Enhancement:
├── Bottleneck indicator (🚨 icon with score)
├── Downstream impact count ("Blocking 5 tasks")
├── Critical path membership ("On critical path")
└── Graduation candidate flag ("Tool→Infra candidate")
```

### Metrics Dashboard
```
Per-Program Bottleneck Metrics:
├── Current Bottlenecks: Count by severity level
├── Avg Resolution Time: Time from detection to resolution
├── Bottleneck Recurrence: Tasks that become bottlenecks repeatedly
├── Critical Path Length: Days (with trend over time)
├── Resource Utilization: % capacity by assignee
└── Graduation Pipeline: Tools evaluated for infrastructure promotion
```

## Tool→Infrastructure Graduation System

### Evaluation Criteria Matrix

| Factor | Weight | Measurement | Threshold |
|--------|--------|-------------|-----------|
| **Usage Frequency** | 30% | Invocations/week across programs | >50/week |
| **User Adoption** | 25% | Unique users in past month | >5 users |
| **Business Impact** | 20% | Tasks unblocked/revenue protected | High impact |
| **Maintenance Burden** | 15% | Support tickets + downtime incidents | <2/month |
| **Technical Debt** | 10% | Code quality + security compliance | No critical issues |

### Graduation Scoring Formula
```
Graduation Score = Σ(Factor Score × Weight)

Factor Scores (0-100):
- Usage: min(weekly_invocations / 50 * 100, 100)
- Adoption: min(unique_users / 10 * 100, 100)  
- Impact: Business_value_score (manual assessment)
- Maintenance: max(100 - (incidents * 20), 0)
- Tech_Debt: Code_quality_score (automated analysis)
```

### Graduation Stages
1. **Ad-hoc Tool** (Score 0-30): Personal/team scripts
2. **Shared Tool** (Score 31-60): Cross-team usage, basic monitoring
3. **Service Tool** (Score 61-80): Formal support, SLA expectations
4. **Infrastructure** (Score 81-100): Mission-critical, full operational support

### Auto-Graduation Triggers
```javascript
const autoGraduationRules = {
  // Emergency graduation: Tool becomes critical path bottleneck resolver
  emergency: (tool) => tool.criticalPathImpact > 0.8 && tool.downtime > 4,
  
  // Natural graduation: Sustained high usage + quality
  natural: (tool) => tool.score > 81 && tool.monthlyTrend > 0,
  
  // Forced graduation: Business dependency identified
  forced: (tool) => tool.businessCritical && tool.score > 60
}
```

## Implementation Phases

### Phase 1: Data Collection (Week 1-2)
- Extend LBF API to capture task relationships
- Add dependency tracking to task creation/update flows
- Implement basic bottleneck detection algorithm
- Create metrics collection infrastructure

### Phase 2: Visualization (Week 3-4) 
- Build critical path visualization component
- Add bottleneck indicators to existing task cards
- Create per-program bottleneck dashboard
- Implement alert notification system

### Phase 3: Graduation System (Week 5-6)
- Build tool registry and usage tracking
- Implement graduation scoring engine
- Add graduation candidate detection to dashboard
- Create graduation workflow (approval, migration, monitoring)

### Phase 4: Advanced Features (Week 7-8)
- Machine learning bottleneck prediction
- Resource optimization recommendations
- Integration with ITSM SLA monitoring
- Historical trend analysis and forecasting

## Database Schema Extensions

### New Tables
```sql
-- Task Dependencies
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY,
    parent_task_id INTEGER,
    child_task_id INTEGER,
    dependency_type VARCHAR(20), -- 'blocking', 'resource', 'deliverable'
    created_at TIMESTAMP,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id),
    FOREIGN KEY (child_task_id) REFERENCES tasks(id)
);

-- Bottleneck History
CREATE TABLE bottleneck_events (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    score DECIMAL(10,2),
    downstream_count INTEGER,
    detected_at TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Tool Registry
CREATE TABLE tools_registry (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    graduation_score DECIMAL(5,2),
    graduation_stage VARCHAR(20),
    last_evaluation TIMESTAMP
);

-- Tool Usage Tracking
CREATE TABLE tool_usage (
    id INTEGER PRIMARY KEY,
    tool_id INTEGER,
    user_id VARCHAR(50),
    program_id INTEGER,
    invocation_time TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools_registry(id)
);
```

### Existing Schema Enhancements
```sql
-- Add bottleneck tracking to tasks
ALTER TABLE tasks ADD COLUMN bottleneck_score DECIMAL(10,2) DEFAULT 0;
ALTER TABLE tasks ADD COLUMN is_critical_path BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN downstream_count INTEGER DEFAULT 0;

-- Add graduation tracking to projects
ALTER TABLE projects ADD COLUMN tool_graduation_candidates TEXT; -- JSON array
```

## API Extensions

### New Endpoints
```javascript
// Bottleneck detection
GET /api/bottlenecks/program/{id}     // List current bottlenecks
GET /api/bottlenecks/task/{id}/impact // Get downstream impact analysis

// Critical path
GET /api/critical-path/project/{id}   // Get critical path for project
POST /api/critical-path/calculate     // Trigger recalculation

// Tool graduation
GET /api/graduation/candidates        // List graduation candidates
POST /api/graduation/evaluate/{id}    // Trigger evaluation
PUT /api/graduation/promote/{id}      // Manual graduation
```

## Monitoring & Alerts

### Key Metrics
- **Bottleneck Resolution Time**: Average time from detection to resolution
- **Critical Path Stability**: How often critical path changes
- **Graduation Pipeline Health**: Tools moving through stages
- **Resource Utilization**: Assignee workload distribution

### Alert Conditions
- New critical bottleneck detected (score > 40)
- Critical path length increases >20%
- Tool graduation candidate identified
- Resource over-allocation detected (>120% capacity)

## Failure Modes & Mitigation

| Failure Mode | Detection | Impact | Recovery |
|--------------|-----------|--------|----------|
| Dependency graph corruption | Data validation checks | Incorrect bottleneck detection | Rebuild from task audit logs |
| Critical path calculation timeout | Request timeout monitoring | Dashboard unavailable | Fallback to cached results |
| Bottleneck alert storm | Alert rate limiting | Notification fatigue | Batch alerts, increase thresholds |
| Tool registry data loss | Backup verification | Lost graduation history | Restore from daily snapshots |

## Success Metrics

### Bottleneck Tracking
- **Detection Accuracy**: >90% of manually identified bottlenecks caught
- **False Positive Rate**: <10% of flagged bottlenecks are false alarms
- **Resolution Acceleration**: 30% faster bottleneck resolution vs. manual detection

### Critical Path
- **Visualization Usage**: >80% of program managers use critical path view weekly
- **Path Prediction Accuracy**: Critical path estimates within 20% of actual delivery

### Tool Graduation
- **Graduation Pipeline**: 5-10 tools evaluated monthly
- **Infrastructure Quality**: <1% downtime for graduated tools
- **Resource Optimization**: 25% reduction in duplicate tool development

---
*Design Document: LBF Enterprise Dashboard Bottleneck Tracking & Tool→Infrastructure Graduation System*
*Author: Claude Code Subagent*
*Date: February 16, 2026*