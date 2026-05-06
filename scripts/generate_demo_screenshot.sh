#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
OUT_DIR="${OUT_DIR:-.demo-screenshot}"
SCREENSHOT_PATH="${SCREENSHOT_PATH:-docs/assets/demo-report.png}"

"$PYTHON_BIN" inbox_application_reporter.py demo --report-dir "$OUT_DIR" --quiet

CHROME_BIN="${CHROME_BIN:-}"
if [ -z "$CHROME_BIN" ]; then
  CHROME_BIN="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
fi
if [ -z "$CHROME_BIN" ] && [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
fi
if [ -z "$CHROME_BIN" ]; then
  echo "Chrome or Chromium is required to regenerate the demo screenshot." >&2
  exit 2
fi

mkdir -p "$(dirname "$SCREENSHOT_PATH")"
"$CHROME_BIN" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --window-size=1440,1100 \
  "--screenshot=$SCREENSHOT_PATH" \
  "file://$ROOT_DIR/$OUT_DIR/applications_report.html"

echo "$SCREENSHOT_PATH"
