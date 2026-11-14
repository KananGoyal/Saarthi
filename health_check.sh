#!/bin/bash
URL="https://saarthi-8ecr.onrender.com/"
LOG="health.log"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 60 "$URL")
TIME=$(date '+%Y-%m-%d %H:%M:%S')

if [ "$STATUS" = "200" ]; then
  echo "$TIME UP status=$STATUS" >> "$LOG"
else
  echo "$TIME DOWN status=$STATUS" >> "$LOG"
  exit 1
fi