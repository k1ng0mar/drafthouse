#!/usr/bin/env python3
"""Evaluate a golden artifact plate — lint, tokens, structure, optional vision log."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DRAFTHOUSE_ROOT", str(ROOT))

from drafthouse.lint import lint_file  # noqa: E402
from drafthouse.tokens import DesignSystem, check_artifact_tokens  # noqa: E402
from drafthouse.vision_gate import load_rounds  # noqa: E402


def structure_checks(html: str, brief_constraints: list[str]) -> list[dict]:
    """Heuristic structure checks driven by brief constraint tokens."""
    checks = []
    text = html.lower()

    def has(pattern: str, label: str) -> None:
        ok = re.search(pattern, text, re.I) is not None
        checks.append({"id": label, "ok": ok})

    for constraint in brief_constraints:
        c = constraint.strip().lower()
        if c in {"has-nav", "navbar"}:
            has(r"<nav\b|role=[\"']navigation[\"']|class=[\"'][^\"']*nav", "has-nav")
        elif c in {"has-hero", "hero"}:
            has(r"class=[\"'][^\"']*hero|<section[^>]{0,80}hero|<h1", "has-hero")
        elif c in {"has-footer", "footer"}:
            has(r"<footer\b", "has-footer")
        elif c in {"has-cta", "cta"}:
            has(r"cta|get started|sign up|book a demo|contact|request |talk to us|back to|return to|go home|read the", "has-cta")
        elif c in {"has-pricing", "pricing"}:
            has(r"pricing|price|plan|per month|/mo", "has-pricing")
        elif c in {"has-title"}:
            has(r"<title>[^<]+", "has-title")
        elif c in {"has-h1"}:
            has(r"<h1[\s>]", "has-h1")
        elif c == "no-lorem":
            checks.append({"id": "no-lorem", "ok": "lorem" not in text})
        elif c == "no-emoji-icons":
            checks.append(
                {
                    "id": "no-emoji-icons",
                    "ok": not re.search("[\U0001F300-\U0001FAFF✨🚀🎯]", html),
                }
            )
        elif c.startswith("includes:"):
            needle = c.split(":", 1)[1].strip()
            checks.append({"id": f"includes:{needle}", "ok": needle.lower() in text})
    return checks


def evaluate(plate_dir: Path) -> dict:
    brief_path = plate_dir / "brief.md"
    artifact_candidates = list(plate_dir.glob("artifact.*")) + list(plate_dir.glob("*.html"))
    artifact = next((p for p in artifact_candidates if p.suffix in {".html", ".htm"}), None)
    if not artifact:
        return {"plate": plate_dir.name, "ok": False, "error": "no artifact html"}

    constraints: list[str] = []
    expected_system = "default"
    if brief_path.exists():
        brief = brief_path.read_text(encoding="utf-8")
        for line in brief.splitlines():
            if line.strip().startswith("constraints:"):
                constraints = [
                    x.strip() for x in line.split(":", 1)[1].split(",") if x.strip()
                ]
            if line.strip().startswith("design_system:"):
                expected_system = line.split(":", 1)[1].strip() or "default"

    system_path = ROOT / "design-systems" / expected_system
    if not system_path.exists():
        system_path = ROOT / "design-systems" / "default"
    system = DesignSystem.load(system_path)

    lint = lint_file(artifact)
    token_issues = check_artifact_tokens(
        artifact.read_text(encoding="utf-8", errors="replace"), system
    )
    struct = structure_checks(artifact.read_text(encoding="utf-8", errors="replace"), constraints)
    vision_rounds = load_rounds(artifact)

    struct_ok = all(c["ok"] for c in struct) if struct else True
    lint_ok = lint.pass_gate
    tokens_ok = not token_issues
    # vision optional: if rounds exist, last must ship OR plate allows missing vision
    vision_ok = True
    if vision_rounds:
        vision_ok = bool(vision_rounds[-1].get("passes_ship"))

    ok = lint_ok and tokens_ok and struct_ok and vision_ok
    return {
        "plate": plate_dir.name,
        "artifact": str(artifact),
        "design_system": system.name,
        "constraints": constraints,
        "ok": ok,
        "lint": {"pass": lint_ok, "counts": {"p0": len(lint.p0), "p1": len(lint.p1), "p2": len(lint.p2)},
                 "issues": [i.to_dict() for i in lint.issues[:20]]},
        "tokens": {"pass": tokens_ok, "issues": [t.to_dict() for t in token_issues]},
        "structure": {"pass": struct_ok, "checks": struct},
        "vision": {"rounds": len(vision_rounds), "pass": vision_ok, "last": vision_rounds[-1] if vision_rounds else None},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate golden design plates")
    parser.add_argument("path", nargs="?", help="Plate dir or evals/golden (all)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    base = Path(args.path) if args.path else ROOT / "evals" / "golden"
    plates: list[Path]
    if base.is_dir() and (base / "brief.md").exists() or (base.is_dir() and list(base.glob("*.html"))):
        plates = [base]
    elif base.is_dir():
        plates = sorted(p for p in base.iterdir() if p.is_dir())
    else:
        print(f"No plates under {base}", file=sys.stderr)
        return 2

    results = [evaluate(p) for p in plates]
    failed = [r for r in results if not r.get("ok")]
    if args.json:
        print(json.dumps({"results": results, "failed": len(failed)}, indent=2))
    else:
        for r in results:
            status = "PASS" if r.get("ok") else "FAIL"
            print(f"[{status}] {r.get('plate')}  lintP0={r.get('lint',{}).get('counts',{}).get('p0')} tokens={r.get('tokens',{}).get('pass')} struct={r.get('structure',{}).get('pass')}")
            if not r.get("ok"):
                for issue in r.get("lint", {}).get("issues", [])[:5]:
                    if issue.get("severity") == "P0":
                        print(f"    P0 {issue.get('rule_id')}: {issue.get('message')}")
                for t in r.get("tokens", {}).get("issues", [])[:5]:
                    print(f"    token {t.get('kind')}: {t.get('message')}")
                for c in r.get("structure", {}).get("checks", []):
                    if not c.get("ok"):
                        print(f"    struct fail: {c.get('id')}")
        print(f"\n{len(results) - len(failed)}/{len(results)} plates passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
