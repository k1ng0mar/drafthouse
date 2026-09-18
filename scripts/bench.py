#!/usr/bin/env python3
"""Benchmark lint / tokens / refs / MCP — Phase A performance baseline."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DRAFTHOUSE_ROOT", str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT / "src"))

from drafthouse.lint import lint_text  # noqa: E402
from drafthouse.references import search_references  # noqa: E402
from drafthouse.tokens import DesignSystem, check_artifact_tokens  # noqa: E402


def _pct(samples: list[float], p: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def _ms(samples: list[float]) -> dict:
    return {
        "n": len(samples),
        "p50_ms": round(_pct(samples, 50), 2),
        "p95_ms": round(_pct(samples, 95), 2),
        "mean_ms": round(statistics.fmean(samples), 2) if samples else 0.0,
        "max_ms": round(max(samples), 2) if samples else 0.0,
    }


def make_plate(size_kb: int = 50) -> str:
    """Synthetic HTML plate ~size_kb."""
    section = (
        "<section class=\"plate\"><h2>Section {i}</h2>"
        "<p>Specific product copy for plate body {i} — no lorem, no invented metrics.</p>"
        "<a href=\"#\">Open details {i}</a></section>\n"
    )
    body = "".join(section.format(i=i) for i in range(max(4, size_kb)))
    return (
        "<!doctype html><html><head><title>Perf plate</title>"
        "<style>body{font-family:Georgia,serif;color:#1e241d;background:#ecebe2}"
        ".plate{padding:1rem;border:1px solid #c5c9b8}a{color:#e65b35}</style>"
        f"</head><body><h1>Perf plate</h1>{body}</body></html>"
    )


def bench_lint(iters: int = 80) -> dict:
    html = make_plate(50)
    # warmup
    lint_text(html)
    samples = []
    for _ in range(iters):
        t0 = time.perf_counter()
        lint_text(html)
        samples.append((time.perf_counter() - t0) * 1000)
    return {"operation": "lint_text_50kb", **_ms(samples)}


def bench_tokens(iters: int = 50) -> dict:
    system = DesignSystem.load(ROOT / "design-systems" / "default")
    html = make_plate(30)
    check_artifact_tokens(html, system)
    samples = []
    for _ in range(iters):
        t0 = time.perf_counter()
        check_artifact_tokens(html, system)
        samples.append((time.perf_counter() - t0) * 1000)
    return {"operation": "tokens_check", **_ms(samples)}


def bench_refs(iters: int = 100) -> dict:
    search_references(query="hero")
    samples = []
    queries = ["hero", "navbar", "pricing", "footer", "bento", "dashboard", "cta", "404"]
    for i in range(iters):
        q = queries[i % len(queries)]
        t0 = time.perf_counter()
        search_references(query=q, limit=8)
        samples.append((time.perf_counter() - t0) * 1000)
    return {"operation": "refs_search", **_ms(samples)}


def bench_mcp_initialize(iters: int = 20, warmup: int = 3) -> dict:
    script = ROOT / "src" / "drafthouse" / "mcp_server.py"
    msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)}

    def once() -> float:
        t0 = time.perf_counter()
        subprocess.run(
            [sys.executable, str(script)],
            input=msg,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        return (time.perf_counter() - t0) * 1000

    for _ in range(warmup):
        once()
    samples = [once() for _ in range(iters)]
    return {"operation": "mcp_initialize_process", "warmup": warmup, **_ms(samples)}


def bench_mcp_lint_roundtrip(iters: int = 20, warmup: int = 2) -> dict:
    script = ROOT / "src" / "drafthouse" / "mcp_server.py"
    html = make_plate(20)
    lines = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "drafthouse_lint", "arguments": {"text": html}},
            }
        ),
    ]
    stdin = "\n".join(lines) + "\n"
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)}

    def once() -> float:
        t0 = time.perf_counter()
        subprocess.run(
            [sys.executable, str(script)],
            input=stdin,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        return (time.perf_counter() - t0) * 1000

    for _ in range(warmup):
        once()
    samples = [once() for _ in range(iters)]
    return {"operation": "mcp_init_plus_lint_process", "warmup": warmup, **_ms(samples)}


# p50 is the primary MCP cold-start metric after warmup (p95 can spike on first FS touch)
TARGETS = {
    "lint_text_50kb": {"p95_ms": 150},
    "tokens_check": {"p95_ms": 80},
    "refs_search": {"p95_ms": 20},
    "mcp_initialize_process": {"p50_ms": 250, "p95_ms": 400},
}


def _violations(row: dict) -> list[str]:
    op = row["operation"]
    if op not in TARGETS:
        return []
    target = TARGETS[op]
    out = []
    if "p50_ms" in target and row.get("p50_ms", 0) > target["p50_ms"]:
        out.append(f"{op}: p50 {row['p50_ms']}ms > {target['p50_ms']}ms")
    if "p95_ms" in target and row.get("p95_ms", 0) > target["p95_ms"]:
        out.append(f"{op}: p95 {row['p95_ms']}ms > {target['p95_ms']}ms")
    return out


def main() -> int:
    results = [
        bench_lint(),
        bench_tokens(),
        bench_refs(),
        bench_mcp_initialize(),
        bench_mcp_lint_roundtrip(),
    ]
    print(json.dumps({"benchmarks": results, "targets": TARGETS}, indent=2))

    failures: list[str] = []
    for row in results:
        failures.extend(_violations(row))
    strict = os.environ.get("DRAFTHOUSE_BENCH_STRICT", "0") == "1"
    if failures:
        msg = "; ".join(failures)
        if strict:
            print(f"BENCH FAIL: {msg}", file=sys.stderr)
            return 1
        print(f"BENCH WARN (non-strict): {msg}", file=sys.stderr)
        return 0
    print("BENCH OK — all measured ops within targets", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
