#!/usr/bin/env bash
# CI gate for Drafthouse — tests + fixtures + golden plates + vision + bench
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
export DRAFTHOUSE_ROOT="${DRAFTHOUSE_ROOT:-$ROOT}"
export HERMES_HOME="${HERMES_HOME:-$ROOT/.hermes-ci-sandbox}"

cd "$ROOT"
echo "== drafthouse CI =="
echo "ROOT=$ROOT"
echo "HERMES_HOME=$HERMES_HOME"

echo "-- unit tests --"
python3 -m unittest discover -s tests -q

echo "-- must-fail slop fixtures --"
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "src")
from drafthouse.lint import lint_file
fails = list(Path("tests/fixtures").glob("slop*.html"))
if len(fails) < 3:
    raise SystemExit(f"expected >=3 slop fixtures, got {fails}")
for p in fails:
    if lint_file(p).pass_gate:
        raise SystemExit(f"FAIL: {p.name} unexpectedly passed lint")
    print(f"  fail-ok {p.name}")
print(f"{len(fails)} slop fixtures correctly fail")
PY

echo "-- must-pass clean fixture --"
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default >/dev/null
echo "clean.html correctly passes"

echo "-- golden plates --"
python3 scripts/eval_plate.py

echo "-- vision gate demo --"
python3 -m drafthouse.cli vision gate demo >/dev/null
echo "vision gate demo ok"

echo "-- doctor --"
python3 -m drafthouse.doctor || true

echo "-- bench --"
python3 scripts/bench.py

echo "== CI OK =="
