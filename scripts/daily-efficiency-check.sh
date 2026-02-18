#!/bin/bash
#
# Daily Token Efficiency Check
# Run via cron to track progress: 0 9 * * * ~/.openclaw/workspace/scripts/daily-efficiency-check.sh
#

cd ~/.openclaw/workspace

# Run the tracker and save to daily log
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="analysis/token-efficiency-daily-$DATE.txt"

echo "Running daily token efficiency check..."

# Try real data first, fall back to demo if no logs available
python3 scripts/token-efficiency-tracker.py --days 1 --output "$OUTPUT_FILE" 2>/dev/null

# If no real data, generate demo for tracking setup
if [ $? -ne 0 ]; then
    echo "No transcript logs found - generating demo report"
    python3 scripts/token-efficiency-tracker.py --demo --output "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "NOTE: This is demo data. Real tracking will begin once OpenClaw transcript logging is configured." >> "$OUTPUT_FILE"
fi

echo "Token efficiency report saved to: $OUTPUT_FILE"

# Keep only last 30 days of reports
find analysis/ -name "token-efficiency-daily-*.txt" -mtime +30 -delete 2>/dev/null

# Optional: send summary to Signal if improvement detected
# Uncomment and customize as needed:
# if grep -q "improvement" "$OUTPUT_FILE"; then
#     echo "Token efficiency improvement detected - check $OUTPUT_FILE" | signal-cli send --message-from-stdin
# fi