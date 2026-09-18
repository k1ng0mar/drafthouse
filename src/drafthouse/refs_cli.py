from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drafthouse.references import (
    CATALOG_VERSION,
    categories_index,
    load_catalog,
    search_references,
    write_catalog,
)
from drafthouse.vision import format_vision_block, parse_vision, vision_prompt


def cmd_refs_list(_: argparse.Namespace) -> int:
    idx = categories_index()
    payload = {
        "version": CATALOG_VERSION,
        "count": len(load_catalog()),
        "categories": {k: v for k, v in sorted(idx.items())},
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_refs_search(args: argparse.Namespace) -> int:
    hits = search_references(
        query=args.query or "",
        category=args.category,
        tag=args.tag,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps(hits, indent=2))
        return 0
    if not hits:
        print("No references matched.")
        return 1
    for item in hits:
        print(f"{item['id']:22}  {item['category']:16}  {item['url']}")
        print(f"  {item['best_for']}")
    return 0


def cmd_refs_category(args: argparse.Namespace) -> int:
    hits = search_references(category=args.category, limit=args.limit or 50)
    if args.json:
        print(json.dumps(hits, indent=2))
        return 0
    if not hits:
        print(f"No references in category: {args.category}")
        return 1
    print(f"# {args.category}")
    for item in hits:
        print(f"- **{item['name']}** — {item['url']}")
        print(f"  {item['best_for']}")
    return 0


def cmd_refs_write(_: argparse.Namespace) -> int:
    path = write_catalog()
    print(path)
    return 0


def cmd_vision_rubric(_: argparse.Namespace) -> int:
    print(vision_prompt())
    return 0


def cmd_vision_parse(args: argparse.Namespace) -> int:
    text = Path(args.path).read_text(encoding="utf-8", errors="replace") if args.path else sys.stdin.read()
    report = parse_vision(text, screenshot_path=args.screenshot, round_no=args.round)
    print(json.dumps(report.to_dict(), indent=2))
    print(report.gate_summary(), file=sys.stderr)
    return 0 if report.passes_ship else 1


def cmd_vision_demo(args: argparse.Namespace) -> int:
    """Self-check: format + parse a sample vision block."""
    block = format_vision_block(
        {
            "philosophy": args.philosophy,
            "hierarchy": args.hierarchy,
            "execution": args.execution,
            "specificity": args.specificity,
            "restraint": args.restraint,
            "accessibility": args.accessibility,
            "craft": args.craft,
        },
        must_fix=[] if args.no_fix else ["CTA contrast below 4.5:1 on parchment"],
        notes="demo",
    )
    print(block)
    report = parse_vision(block)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.passes_ship else 1


def build_refs_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("refs", help="Design reference catalog")
    refs_sub = p.add_subparsers(dest="refs_cmd", required=True)

    p_list = refs_sub.add_parser("list")
    p_list.set_defaults(func=cmd_refs_list)

    p_search = refs_sub.add_parser("search")
    p_search.add_argument("query", nargs="?")
    p_search.add_argument("--category")
    p_search.add_argument("--tag")
    p_search.add_argument("--limit", type=int, default=12)
    p_search.add_argument("--json", action="store_true")
    p_search.set_defaults(func=cmd_refs_search)

    p_cat = refs_sub.add_parser("category")
    p_cat.add_argument("category")
    p_cat.add_argument("--limit", type=int, default=50)
    p_cat.add_argument("--json", action="store_true")
    p_cat.set_defaults(func=cmd_refs_category)

    p_write = refs_sub.add_parser("write-catalog")
    p_write.set_defaults(func=cmd_refs_write)


def build_vision_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("vision", help="Vision gate helpers")
    v_sub = p.add_subparsers(dest="vision_cmd", required=True)

    p_r = v_sub.add_parser("rubric")
    p_r.set_defaults(func=cmd_vision_rubric)

    p_p = v_sub.add_parser("parse")
    p_p.add_argument("path", nargs="?")
    p_p.add_argument("--screenshot")
    p_p.add_argument("--round", type=int, default=1)
    p_p.set_defaults(func=cmd_vision_parse)

    p_d = v_sub.add_parser("demo")
    for name, default in [
        ("philosophy", 8),
        ("hierarchy", 8),
        ("execution", 8),
        ("specificity", 8),
        ("restraint", 8),
        ("accessibility", 8),
        ("craft", 8),
    ]:
        p_d.add_argument(f"--{name}", type=int, default=default)
    p_d.add_argument("--no-fix", action="store_true")
    p_d.set_defaults(func=cmd_vision_demo)

    def cmd_vision_gate(args: argparse.Namespace) -> int:
        from drafthouse.vision_gate import main as gate_main

        rest = list(getattr(args, "gate_args", None) or [])
        if rest and rest[0] == "--":
            rest = rest[1:]
        return gate_main(rest)

    p_g = v_sub.add_parser("gate", help="L4 runner: plan | parse | rounds | demo | rubric")
    p_g.add_argument("gate_args", nargs=argparse.REMAINDER)
    p_g.set_defaults(func=cmd_vision_gate)
