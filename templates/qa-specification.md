# [System/Feature] — QA Specification

> *One-line: what is being tested and why.*

| Field | Value |
|-------|-------|
| **Scope** | [what's under test] |
| **Owner** | [who maintains these tests] |
| **Cadence** | [daily · hourly-on-fail · weekly-stable] |
| **Alerting** | [Discord #channel / Signal / email] |
| **Results** | [path to results directory] |
| **Last Run** | [YYYY-MM-DD HH:MM UTC — auto-updated] |
| **ITIL Process** | Event Management / Incident Management |

---

## 1. Test Inventory

| # | Test Name | Category | Severity | Pass Criteria | Timeout |
|---|-----------|----------|----------|---------------|---------|
| 1 | [name] | [infra/app/security/perf] | [critical/warning/info] | [what constitutes pass] | [seconds] |

---

## 2. Results Schema

```json
{
  "timestamp": "ISO-8601",
  "sweep_id": "unique-id",
  "duration_seconds": 0.0,
  "summary": {
    "total": 0,
    "pass": 0,
    "warn": 0,
    "fail": 0,
    "error": 0
  },
  "results": [
    {
      "test_name": "string",
      "category": "string",
      "severity": "string",
      "result": "pass|warn|fail|error",
      "message": "string",
      "metrics": {}
    }
  ]
}
```

---

## 3. Escalation Matrix

*ITIL Incident Management alignment.*

| Severity | Response Time | Escalation Path | Action |
|----------|--------------|-----------------|--------|
| Critical | Immediate | Signal DM → Matthew | Auto-page, create incident |
| Warning | < 1 hour | Discord #system-health | Log, retry next cadence |
| Info | Next business day | Dashboard only | Log for trending |

---

## 4. Alerting Configuration

- **Channel:** [Discord webhook / Signal / etc.]
- **Format:** [summary only / full details / failures only]
- **Suppression:** [don't re-alert if same failure within N minutes]

---

## 5. Dependencies

| Dependency | Required For | Fallback |
|------------|-------------|----------|
| [service/API] | [which tests] | [graceful skip / cached result] |

---

## 6. Maintenance

- **Adding tests:** [process — where to add, how to register]
- **Disabling tests:** [process — comment out vs delete]
- **Review cadence:** [monthly / quarterly]

---

## 7. History & Trends

- **Results directory:** [path]
- **Retention:** [days/count]
- **Dashboard:** [URL if applicable]

---

*Template version: 1.0 — Based on ITIL 4 Event & Incident Management*
*LBF standard. All QA specs follow this structure.*
