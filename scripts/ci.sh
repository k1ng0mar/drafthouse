#!/usr/bin/env bash
# CI gate for Drafthouse — tests + must-pass fixtures + bench smoke + doctor
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export DRAFTHOUSE_ROOT="${DRAFTHOUSE_ROOT:-$ROOT}"
# Isolate by default so CI never touches live ~/.hermes
export HERMES_HOME="${HERMES_HOME:-$ROOT/.hermes-ci-sandbox}"

cd "$ROOT"
echo "== drafthouse CI =="
echo "ROOT=$ROOT"
echo "HERMES_HOME=$HERMES_HOME"

echo "-- unit tests --"
python3 -m unittest discover -s tests -q

echo "-- must-fail slop fixture --"
if bash bin/drafthouse lint tests/fixtures/slop.html --system design-systems/default >/dev/null 2>&1; then
  echo "FAIL: slop.html unexpectedly passed lint" >&2
  exit 1
fi
echo "slop.html correctly fails"

echo "-- must-pass clean fixture --"
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default >/dev/null
echo "clean.html correctly passes"

echo "-- doctor --"
python3 -m drafthouse.doctor || true

echo "-- bench smoke --"
python3 scripts/bench.py

echo "== CI OK =="
