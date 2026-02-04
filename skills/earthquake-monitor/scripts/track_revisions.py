#!/usr/bin/env python3
"""
Track earthquake magnitude revisions over time.
Stores snapshots and compares to detect changes.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from check_quakes import fetch_quakes, format_time

DB_PATH = Path(__file__).parent / 'quake_history.db'

def init_db():
    """Create database for tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id TEXT PRIMARY KEY,
            timestamp INTEGER,
            magnitude REAL,
            place TEXT,
            depth REAL,
            recorded_at INTEGER,
            url TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revisions (
            id TEXT,
            old_magnitude REAL,
            new_magnitude REAL,
            change REAL,
            detected_at INTEGER,
            PRIMARY KEY (id, detected_at)
        )
    ''')
    
    conn.commit()
    return conn

def track_quakes(min_magnitude=5.0):
    """
    Fetch current quakes and compare to stored data.
    Returns list of revisions detected.
    """
    conn = init_db()
    cursor = conn.cursor()
    
    quakes = fetch_quakes('day')
    now = int(datetime.now().timestamp() * 1000)
    
    revisions = []
    
    for quake in quakes:
        quake_id = quake['id']
        props = quake['properties']
        mag = props['mag']
        
        if mag < min_magnitude:
            continue
        
        # Check if we've seen this quake before
        cursor.execute('SELECT magnitude FROM snapshots WHERE id = ?', (quake_id,))
        result = cursor.fetchone()
        
        if result:
            old_mag = result[0]
            if abs(mag - old_mag) >= 0.1:  # Significant change
                change = mag - old_mag
                
                # Record revision
                cursor.execute('''
                    INSERT INTO revisions (id, old_magnitude, new_magnitude, change, detected_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (quake_id, old_mag, mag, change, now))
                
                revisions.append({
                    'id': quake_id,
                    'place': props['place'],
                    'old': old_mag,
                    'new': mag,
                    'change': change,
                    'direction': 'UPGRADED' if change > 0 else 'DOWNGRADED'
                })
                
                # Update stored magnitude
                cursor.execute('UPDATE snapshots SET magnitude = ? WHERE id = ?', (mag, quake_id))
        else:
            # New quake - store it
            cursor.execute('''
                INSERT INTO snapshots (id, timestamp, magnitude, place, depth, recorded_at, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                quake_id,
                props['time'],
                mag,
                props['place'],
                quake['geometry']['coordinates'][2],
                now,
                props.get('url', '')
            ))
    
    conn.commit()
    conn.close()
    
    return revisions

def get_revision_history(quake_id=None, days=7):
    """Get revision history for a specific quake or all recent revisions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = int((datetime.now().timestamp() - days * 86400) * 1000)
    
    if quake_id:
        cursor.execute('''
            SELECT r.*, s.place, s.url
            FROM revisions r
            JOIN snapshots s ON r.id = s.id
            WHERE r.id = ? AND r.detected_at > ?
            ORDER BY r.detected_at DESC
        ''', (quake_id, cutoff))
    else:
        cursor.execute('''
            SELECT r.*, s.place, s.url
            FROM revisions r
            JOIN snapshots s ON r.id = s.id
            WHERE r.detected_at > ?
            ORDER BY r.detected_at DESC
        ''', (cutoff,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def main():
    print("🔍 Checking for earthquake magnitude revisions...")
    print()
    
    revisions = track_quakes(min_magnitude=5.0)
    
    if not revisions:
        print("✅ No revisions detected.")
        print()
        
        # Show recent history
        history = get_revision_history(days=7)
        if history:
            print("📊 Recent revisions (last 7 days):")
            for row in history[:10]:
                place = row[5]
                old = row[1]
                new = row[2]
                change = row[3]
                detected = format_time(row[4])
                
                direction = "⬆️ UPGRADED" if change > 0 else "⬇️ DOWNGRADED"
                print(f"  {direction}: {old:.1f} → {new:.1f} ({change:+.1f})")
                print(f"    {place}")
                print(f"    {detected}")
                print()
    else:
        print(f"🚨 {len(revisions)} REVISION(S) DETECTED:")
        print()
        
        for rev in revisions:
            direction_icon = "⬆️" if rev['change'] > 0 else "⬇️"
            print(f"{direction_icon} {rev['direction']}: {rev['old']:.1f} → {rev['new']:.1f} ({rev['change']:+.1f})")
            print(f"   {rev['place']}")
            print()

if __name__ == '__main__':
    main()
