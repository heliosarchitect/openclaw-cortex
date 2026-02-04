---
name: earthquake-monitor
description: Monitor global earthquake activity using USGS data. Check for significant quakes, alert on major events (6.0+), track patterns. Use for earthquake awareness, disaster monitoring, or seismic research.
---

# Earthquake Monitor

Monitor global seismic activity using USGS (United States Geological Survey) earthquake feeds.

## Quick Usage

```bash
# Check significant quakes (4.5+ magnitude)
python3 scripts/check_quakes.py

# Check all quakes (any magnitude)
python3 scripts/check_quakes.py --all

# Alert threshold (only show 6.0+)
python3 scripts/check_quakes.py --min 6.0

# JSON output
python3 scripts/check_quakes.py --format json
```

## Alert Thresholds

Default behavior:
- **6.0-6.9:** Notable (report if checking)
- **7.0-7.9:** Major (always alert)
- **8.0+:** Catastrophic (immediate alert)

## USGS API Endpoints

- **All quakes (1 hour):** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`
- **All quakes (1 day):** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
- **4.5+ (1 hour):** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson`
- **4.5+ (1 day):** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson`
- **Significant (1 week):** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson`

Data updates every ~5 minutes.

## Output Fields

- `magnitude` - Richter scale (e.g., 5.2)
- `place` - Location description
- `time` - Unix timestamp (milliseconds)
- `depth` - Kilometers below surface
- `url` - USGS detail page

## Revision Tracking

Track magnitude changes over time (USGS revises magnitudes as more data arrives):

```bash
# Track and report revisions
python3 scripts/track_revisions.py

# View revision history
sqlite3 scripts/quake_history.db "SELECT * FROM revisions ORDER BY detected_at DESC LIMIT 10"
```

Detects:
- Upgrades (magnitude increased)
- Downgrades (magnitude decreased)
- Stores history in SQLite database
- Flags changes ≥0.1 magnitude

**Conspiracy mode activated:** "They downgraded that 6.2 to 5.9... suspicious..."

## Integration

For automated monitoring (cron/heartbeat):

```python
from skills.earthquake_monitor.scripts.check_quakes import check_earthquakes

result = check_earthquakes(min_magnitude=6.0)
if result['alert_level'] == 'catastrophic':
    # Send immediate alert
    pass
```

For revision tracking:

```python
from skills.earthquake_monitor.scripts.track_revisions import track_quakes

revisions = track_quakes(min_magnitude=5.0)
if revisions:
    for rev in revisions:
        print(f"{rev['direction']}: {rev['old']} → {rev['new']}")
```

## Notes

- Data is preliminary for first ~30 minutes, reviewed later
- Magnitudes may be revised as more data arrives
- Location precision varies (±5-20 km typical)
- Depth "0 km" often means shallow (<5 km actual)
