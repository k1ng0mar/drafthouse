"""Vision gate runner (L4) — local orchestration, no model calls.

Hermes does desktop_preview + vision_analyze; this tool:
  1. Records artifact hash for screenshot cache keys
  2. Emits the rubric / expected capture checklist
  3. Parses vision output (file or stdin)
  4. Enforces floor / ship / max-rounds
  5. Appends JSONL gate logs under DRAFTHOUSE_GATE_DIR or ~/.drafthouse/gates
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from drafthouse.vision import VisionReport, parse_vision, write_gate_log, vision_prompt


def product_root() -> Path:
    env = os.environ.get("DRAFTHOUSE_ROOT")
    return Path(env).expanduser() if env else Path(__file__).resolve().parents[2]


def gate_dir() -> Path:
    env = os.environ.get("DRAFTHOUSE_GATE_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".drafthouse" / "gates"


def artifact_hash(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()[:16]


def capture_plan(artifact: Path, hint: str = "") -> dict:
    """What the agent must do in Hermes — checklist, not a camera driver."""
    h = artifact_hash(artifact) if artifact.exists() else ""
    return {
        "artifact": str(artifact),
        "artifact_hash": h,
        "cache_key": f"{artifact.name}:{h}",
        "steps": [
            "Ensure L1–L3 passed (checklist + 5-dim + drafthouse lint/tokens)",
            f"desktop_preview / open_preview → {artifact}",
            "Capture screenshot (preview tool or human-supplied path)",
            "vision_analyze(screenshot, rubric from drafthouse vision rubric)",
            "Pipe model output to: drafthouse vision parse --artifact <path> --screenshot <img>",
            "If not ship and round < 3: fix MUST_FIX + lowest dims, re-render, repeat",
            "Stop at 3 — present honestly to the human",
        ],
        "rubric": vision_prompt(hint or artifact.name),
        "max_rounds": 3,
        "ship_rule": "composite >= 8.0 AND no MUST_FIX AND every dim >= 5",
    }


def load_rounds(artifact: Path) -> list[dict]:
    log = gate_dir() / f"{_slug(artifact)}.jsonl"
    if not log.exists():
        return []
    rounds = []
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rounds.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rounds


def _slug(artifact: Path) -> str:
    raw = f"{artifact.stem}-{artifact_hash(artifact) if artifact.exists() else 'missing'}"
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in raw)[:80]


def run_parse(
    text: str,
    artifact: Path | None,
    screenshot: str | None,
    round_no: int | None,
    log: bool = True,
) -> tuple[VisionReport, dict]:
    prev = load_rounds(artifact) if artifact else []
    if round_no is None:
        round_no = len(prev) + 1
    if round_no > 3:
        report = parse_vision(text, screenshot_path=screenshot, round_no=round_no)
        payload = {
            **report.to_dict(),
            "blocked": True,
            "reason": "max_rounds_exceeded",
            "message": "Round > 3 — stop looping; show human the best verified state.",
        }
        return report, payload

    report = parse_vision(text, screenshot_path=screenshot, round_no=round_no)
    prev_ship = any(r.get("passes_ship") for r in prev)
    payload = {
        **report.to_dict(),
        "artifact": str(artifact) if artifact else None,
        "artifact_hash": artifact_hash(artifact) if artifact and artifact.exists() else None,
        "previous_rounds": len(prev),
        "previously_shipped": prev_ship,
        "ts": time.time(),
    }
    if log and artifact:
        write_gate_log(gate_dir() / f"{_slug(artifact)}.jsonl", payload)
    return report, payload


def cmd_plan(args: argparse.Namespace) -> int:
    artifact = Path(args.artifact).expanduser()
    plan = capture_plan(artifact, hint=args.hint or "")
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"Vision plan for {plan['artifact']}")
        print(f"cache_key={plan['cache_key']}")
        print(f"max_rounds={plan['max_rounds']}")
        print(f"ship_rule={plan['ship_rule']}")
        print()
        for i, step in enumerate(plan["steps"], 1):
            print(f"  {i}. {step}")
        print()
        print("--- rubric (send to vision_analyze) ---")
        print(plan["rubric"])
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    artifact = Path(args.artifact).expanduser() if args.artifact else None
    report, payload = run_parse(
        text,
        artifact=artifact,
        screenshot=args.screenshot,
        round_no=args.round,
        log=not args.no_log,
    )
    print(json.dumps(payload, indent=2))
    print(report.gate_summary(), file=sys.stderr)
    if payload.get("blocked"):
        return 2
    return 0 if report.passes_ship else 1


def cmd_rounds(args: argparse.Namespace) -> int:
    artifact = Path(args.artifact).expanduser()
    rounds = load_rounds(artifact)
    print(json.dumps({"artifact": str(artifact), "rounds": rounds}, indent=2))
    return 0


def cmd_rubric(args: argparse.Namespace) -> int:
    print(vision_prompt(args.artifact_hint or ""))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Self-check parse + ship math without a model."""
    block = (
        "```drafthouse-vision\n"
        "philosophy: 8\nhierarchy: 8\nexecution: 8\nspecificity: 9\n"
        "restraint: 8\naccessibility: 8\ncraft: 8\n"
        "MUST_FIX: none\nnotes: demo plate hierarchy clear\n```"
    )
    report, payload = run_parse(block, artifact=None, screenshot=None, round_no=1, log=False)
    print(json.dumps(payload, indent=2))
    print(report.gate_summary(), file=sys.stderr)
    return 0 if report.passes_ship else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="drafthouse-vision-gate", description="L4 vision gate runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    plan = sub.add_parser("plan", help="Print Hermes capture plan + rubric for an artifact")
    plan.add_argument("artifact")
    plan.add_argument("--hint")
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=cmd_plan)

    parse = sub.add_parser("parse", help="Parse vision_analyze output and evaluate gate")
    parse.add_argument("--text-file")
    parse.add_argument("--artifact")
    parse.add_argument("--screenshot")
    parse.add_argument("--round", type=int)
    parse.add_argument("--no-log", action="store_true")
    parse.set_defaults(func=cmd_parse)

    rounds = sub.add_parser("rounds", help="Show gate log rounds for an artifact")
    rounds.add_argument("artifact")
    rounds.set_defaults(func=cmd_rounds)

    rub = sub.add_parser("rubric", help="Print vision rubric only")
    rub.add_argument("--artifact-hint")
    rub.set_defaults(func=cmd_rubric)

    demo = sub.add_parser("demo", help="Parse a synthetic passing vision block")
    demo.set_defaults(func=cmd_demo)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
