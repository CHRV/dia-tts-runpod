#!/bin/bash
set -Eeuo pipefail
INPUT_FILE="input.jsonl"   # your jsonl file
LINE_NUM=1

while IFS= read -r line; do
  echo "Processing line $LINE_NUM..."

  echo "$line" | \
  curl -f -X POST "https://api.runpod.ai/v2/$ENDPOINT_ID/runsync" \
       --max-time 600 \
       --header "Authorization: Bearer $RUNPOD_API_KEY" \
       --header "Content-Type: application/json" \
       --data-binary @- | \
  jq -r '.output.audio_base64' | \
  base64 --decode -i > "${LINE_NUM}.mp3"

  LINE_NUM=$((LINE_NUM+1))
done < "$INPUT_FILE"

echo "✅ All lines processed."
