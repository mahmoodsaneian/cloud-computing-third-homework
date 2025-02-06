#!/bin/bash
STATE_FILE="/app/state.txt"
if [ ! -f "$STATE_FILE" ]; then
  echo "2017 01" > "$STATE_FILE"
fi
read year month < "$STATE_FILE"
/usr/local/bin/python3 /app/app.py "$year" "$month"
month=$((10#$month + 1))
if [ "$month" -gt 12 ]; then
  month=1
  year=$((year + 1))
fi
if [ "$year" -eq 2022 ] && [ "$month" -eq 1 ]; then
  echo "2021 12" > "$STATE_FILE"  
  exit 0  s
fi
printf "%d %02d\n" "$year" "$month" > "$STATE_FILE"
