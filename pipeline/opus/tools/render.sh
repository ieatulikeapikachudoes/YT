#!/usr/bin/env bash
# render.sh <short_dir> <V> <out_dir>: renders proj-<V> to <out_dir>/<slug>-<V>.mp4 (phone-friendly size) and runs the final check.
set -e
D=$1; V=$2; OUT=$3; SLUG=$(python3 -c "import json;print(json.load(open('$D/short.json'))['slug'])")
mkdir -p "$OUT"
export HYPERFRAMES_BROWSER_PATH=${HYPERFRAMES_BROWSER_PATH:-/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell} HYPERFRAMES_SKIP_SKILLS=1
npx hyperframes render "$(realpath $D/proj-$V)" -o "$OUT/$SLUG-$V-raw.mp4" > "$D/render-$V.log" 2>&1
ffmpeg -y -v error -i "$OUT/$SLUG-$V-raw.mp4" -c:v libx264 -preset veryfast -crf ${CRF:-21} -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT/$SLUG-$V.mp4"
ffmpeg -y -v error -i "$OUT/$SLUG-$V.mp4" -vf scale=720:1280:flags=lanczos -c:v libx264 -profile:v main -level 3.1 -preset slow -crf 26 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -movflags +faststart "$OUT/$SLUG-$V-phone.mp4"
rm -f "$OUT/$SLUG-$V-raw.mp4"
COVER="$OUT/$SLUG-$V-cover.jpg"; [ -f "$COVER" ] || COVER=""
python3 "$(dirname "$0")/check.py" final "$OUT/$SLUG-$V.mp4" $COVER
