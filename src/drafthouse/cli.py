from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drafthouse import __version__
from drafthouse.critique import parse_critique
from drafthouse.lint import lint_file, lint_text
from drafthouse.tokens import DesignSystem, bind_snippet, check_artifact_tokens


def _repo_design_systems() -> Path:
    # src/drafthouse/cli.py -> products/drafthouse/design-systems
    return Path(__file__).resolve().parents[2] / "design-systems"


def cmd_lint(args: argparse.Namespace) -> int:
    result = lint_file(args.path)
    if args.json:
        payload = result.to_dict()
        if args.system:
            system = DesignSystem.load(args.system)
            token_issues = check_artifact_tokens(
                Path(args.path).read_text(encoding="utf-8", errors="replace"), system
            )
            payload["token_issues"] = [t.to_dict() for t in token_issues]
            if token_issues:
                payload["pass"] = False
        print(json.dumps(payload, indent=2))
    else:
        print(result.to_markdown())
        if args.system:
            system = DesignSystem.load(args.system)
            text = Path(args.path).read_text(encoding="utf-8", errors="replace")
            token_issues = check_artifact_tokens(text, system)
            print(f"\n### tokens — system `{system.name}`")
            if not token_issues:
                print("_OK — no token issues._")
            for issue in token_issues:
                extra = f" ({issue.value})" if issue.value else ""
                print(f"- `{issue.kind}` — {issue.message}{extra}")
    if args.system:
        system = DesignSystem.load(args.system)
        text = Path(args.path).read_text(encoding="utf-8", errors="replace")
        if check_artifact_tokens(text, system):
            return 1
    return 0 if result.pass_gate else 1


def cmd_tokens(args: argparse.Namespace) -> int:
    system = DesignSystem.load(args.system)
    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
    issues = check_artifact_tokens(text, system)
    if args.json:
        print(
            json.dumps(
                {
                    "system": system.name,
                    "path": str(system.root),
                    "token_count": len(system.tokens),
                    "issues": [i.to_dict() for i in issues],
                    "pass": not issues,
                },
                indent=2,
            )
        )
    else:
        print(f"Design system: {system.name}")
        print(f"Path: {system.root}")
        print(f"Tokens: {len(system.tokens)}")
        if not issues:
            print("PASS")
        else:
            print("FAIL")
            for issue in issues:
                extra = f" — {issue.value}" if issue.value else ""
                print(f"- {issue.kind}: {issue.message}{extra}")
    return 0 if not issues else 1


def cmd_bind(args: argparse.Namespace) -> int:
    system = DesignSystem.load(args.system)
    print(bind_snippet(system, max_chars=args.max_chars))
    return 0


def cmd_critique_parse(args: argparse.Namespace) -> int:
    text = Path(args.path).read_text(encoding="utf-8", errors="replace") if args.path else sys.stdin.read()
    scores = parse_critique(text)
    print(json.dumps(scores.to_dict(), indent=2))
    return 0 if scores.passes_preemit else 1


def cmd_selfcheck(args: argparse.Namespace) -> int:
    """Print the L2 pre-emit prompt for skill composition."""
    print(critique_prompt())
    return 0


def critique_prompt() -> str:
    from drafthouse.critique import PREEMIT_PROMPT

    return PREEMIT_PROMPT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drafthouse",
        description="Design verify loop tools for Hermes Agent",
    )
    parser.add_argument("--version", action="version", version=f"drafthouse {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_lint = sub.add_parser("lint", help="L3 anti-slop lint for an artifact")
    p_lint.add_argument("path")
    p_lint.add_argument("--system", help="Design system package dir")
    p_lint.add_argument("--json", action="store_true")
    p_lint.set_defaults(func=cmd_lint)

    p_tok = sub.add_parser("tokens", help="Token adherence checks")
    tok_sub = p_tok.add_subparsers(dest="tokens_cmd", required=True)
    p_tok_check = tok_sub.add_parser("check")
    p_tok_check.add_argument("path")
    p_tok_check.add_argument("--system", required=True)
    p_tok_check.add_argument("--json", action="store_true")
    p_tok_check.set_defaults(func=cmd_tokens)

    p_bind = sub.add_parser("bind", help="Print DESIGN.md/tokens bind block")
    p_bind.add_argument("--system", required=True)
    p_bind.add_argument("--max-chars", type=int, default=4000)
    p_bind.set_defaults(func=cmd_bind)

    p_crit = sub.add_parser("critique", help="Parse a drafthouse-critique block")
    crit_sub = p_crit.add_subparsers(dest="critique_cmd", required=True)
    p_crit_parse = crit_sub.add_parser("parse")
    p_crit_parse.add_argument("path", nargs="?")
    p_crit_parse.set_defaults(func=cmd_critique_parse)

    p_sc = sub.add_parser("selfcheck", help="Print L2 5-dim pre-emit prompt")
    p_sc.set_defaults(func=cmd_selfcheck)

    def cmd_doctor(args: argparse.Namespace) -> int:
        from drafthouse.doctor import main as doctor_main

        argv = ["--json"] if getattr(args, "json", False) else []
        return doctor_main(argv)

    p_doc = sub.add_parser("doctor", help="Environment / install health checks")
    p_doc.add_argument("--json", action="store_true")
    p_doc.set_defaults(func=cmd_doctor)

    from drafthouse.refs_cli import build_refs_parser, build_vision_parser

    build_refs_parser(sub)
    build_vision_parser(sub)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    # default system path convenience
    if hasattr(args, "system") and args.system in {None, "default", "auto"}:
        default = _repo_design_systems() / "default"
        if default.exists():
            args.system = str(default)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
