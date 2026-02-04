#!/usr/bin/env python3
import sqlite3

DB_PATH = "/home/bonsaihorn/Projects/Chad_Volume_tracker/trading_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='fills'")
schema = cursor.fetchone()
print("Fills table schema:")
print(schema[0] if schema else "Table not found")

# Get column info
cursor.execute("PRAGMA table_info(fills)")
columns = cursor.fetchall()
print("\nColumns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get sample rows
cursor.execute("SELECT * FROM fills LIMIT 5")
rows = cursor.fetchall()
print(f"\nSample rows ({len(rows)}):")
for row in rows:
    print(f"  {row}")

conn.close()
