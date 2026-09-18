"""Stdio MCP server for Drafthouse design tools.

Tools:
  drafthouse_lint          — L3 anti-slop lint
  drafthouse_tokens_check  — design-system token adherence
  drafthouse_bind          — DESIGN.md / tokens bind block
  drafthouse_selfcheck     — L2 5-dim pre-emit prompt
  drafthouse_critique_parse— parse a critique score block
  drafthouse_systems_list  — known design-system packages

Protocol: newline-delimited JSON-RPC 2.0 on stdio (MCP subset sufficient
for Hermes MCP client). No third-party deps.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from drafthouse import __version__
from drafthouse.critique import PREEMIT_PROMPT, parse_critique
from drafthouse.lint import lint_file, lint_text
from drafthouse.references import categories_index, load_catalog, search_references
from drafthouse.tokens import DesignSystem, bind_snippet, check_artifact_tokens
from drafthouse.vision import parse_vision, vision_prompt


def product_root() -> Path:
    env = os.environ.get("DRAFTHOUSE_ROOT")
    if env:
        return Path(env).expanduser()
    return Path(__file__).resolve().parents[2]


def systems_dir() -> Path:
    return product_root() / "design-systems"


def list_systems() -> list[dict[str, Any]]:
    root = systems_dir()
    out: list[dict[str, Any]] = []
    if not root.exists():
        return out
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "DESIGN.md").exists():
            out.append({"id": child.name, "path": str(child)})
    # bundled default via installer path
    hermes_ds = Path.home() / ".hermes" / "design-systems" / "drafthouse"
    if hermes_ds.exists():
        for child in sorted(hermes_ds.iterdir()):
            if child.is_dir() and (child / "DESIGN.md").exists():
                out.append({"id": f"hermes:{child.name}", "path": str(child)})
    return out


def resolve_system(ref: str | None) -> Path | None:
    if not ref or ref in {"default", "auto"}:
        cand = systems_dir() / "default"
        return cand if cand.exists() else None
    p = Path(ref).expanduser()
    if p.exists():
        return p
    cand = systems_dir() / ref
    if cand.exists():
        return cand
    return None


TOOLS = [
    {
        "name": "drafthouse_lint",
        "description": (
            "Deterministic design anti-slop lint (P0/P1/P2). "
            "FAIL if any P0. Use before showing/shipping an HTML/CSS artifact."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Artifact file path"},
                "text": {"type": "string", "description": "Or inline HTML/CSS"},
                "system": {"type": "string", "description": "Design system id or path"},
            },
        },
    },
    {
        "name": "drafthouse_tokens_check",
        "description": "Check artifact colors/vars against a DESIGN.md tokens.css package",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "text": {"type": "string"},
                "system": {"type": "string"},
            },
            "required": ["system"],
        },
    },
    {
        "name": "drafthouse_bind",
        "description": "Return the bind block (tokens.css + DESIGN.md excerpt) for a design system",
        "inputSchema": {
            "type": "object",
            "properties": {"system": {"type": "string"}},
        },
    },
    {
        "name": "drafthouse_selfcheck",
        "description": "Return the 5-dim pre-emit self-check prompt (any dim <3/5 = fix and re-score)",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "drafthouse_critique_parse",
        "description": "Parse a ```drafthouse-critique score block and evaluate the pre-emit gate",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "drafthouse_systems_list",
        "description": "List available design-system packages",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "drafthouse_references_search",
        "description": (
            "Search design inspiration galleries by pattern (navbar, hero, pricing…). "
            "Use structure only — re-skin via design system."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string"},
                "tag": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "drafthouse_references_list",
        "description": "List reference categories and catalog size",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "drafthouse_reference_get",
        "description": "Fetch one design reference entry by id",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "drafthouse_vision_rubric",
        "description": "L4 vision-gate rubric prompt for screenshot scoring",
        "inputSchema": {
            "type": "object",
            "properties": {"artifact_hint": {"type": "string"}},
        },
    },
    {
        "name": "drafthouse_vision_parse",
        "description": "Parse ```drafthouse-vision scores and evaluate ship gate (composite>=8, no MUST_FIX)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "screenshot_path": {"type": "string"},
                "round": {"type": "integer"},
            },
            "required": ["text"],
        },
    },
]


def _read_artifact(args: dict[str, Any]) -> tuple[str, str]:
    if args.get("path"):
        p = Path(str(args["path"])).expanduser()
        return p.read_text(encoding="utf-8", errors="replace"), str(p)
    return str(args.get("text") or ""), "<inline>"


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "drafthouse_lint":
        if args.get("path"):
            result = lint_file(args["path"])
        else:
            text, path = _read_artifact(args)
            result = lint_text(text, path=path)
        payload = result.to_dict()
        sys_ref = args.get("system")
        if sys_ref:
            root = resolve_system(str(sys_ref))
            if root:
                system = DesignSystem.load(root)
                text, _ = _read_artifact(args) if not args.get("path") else (
                    Path(args["path"]).read_text(encoding="utf-8", errors="replace"),
                    args["path"],
                )
                token_issues = check_artifact_tokens(text, system)
                payload["token_issues"] = [t.to_dict() for t in token_issues]
                if token_issues:
                    payload["pass"] = False
        return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}

    if name == "drafthouse_tokens_check":
        root = resolve_system(str(args.get("system") or "default"))
        if not root:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": "system not found"})}],
                "isError": True,
            }
        system = DesignSystem.load(root)
        text, _ = _read_artifact(args)
        issues = check_artifact_tokens(text, system)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "system": system.name,
                            "pass": not issues,
                            "issues": [i.to_dict() for i in issues],
                        },
                        indent=2,
                    ),
                }
            ]
        }

    if name == "drafthouse_bind":
        root = resolve_system(str(args.get("system") or "default"))
        if not root:
            return {
                "content": [{"type": "text", "text": "No design system found."}],
                "isError": True,
            }
        return {"content": [{"type": "text", "text": bind_snippet(DesignSystem.load(root))}]}

    if name == "drafthouse_selfcheck":
        return {"content": [{"type": "text", "text": PREEMIT_PROMPT}]}

    if name == "drafthouse_critique_parse":
        scores = parse_critique(str(args.get("text") or ""))
        return {"content": [{"type": "text", "text": json.dumps(scores.to_dict(), indent=2)}]}

    if name == "drafthouse_systems_list":
        return {"content": [{"type": "text", "text": json.dumps(list_systems(), indent=2)}]}

    if name == "drafthouse_references_search":
        hits = search_references(
            query=str(args.get("query") or ""),
            category=args.get("category") or None,
            tag=args.get("tag") or None,
            limit=int(args.get("limit") or 12),
        )
        return {"content": [{"type": "text", "text": json.dumps(hits, indent=2)}]}

    if name == "drafthouse_references_list":
        payload = {
            "count": len(load_catalog()),
            "categories": categories_index(),
        }
        return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}

    if name == "drafthouse_reference_get":
        ref_id = str(args.get("id") or "")
        for item in load_catalog():
            if item.get("id") == ref_id:
                return {"content": [{"type": "text", "text": json.dumps(item, indent=2)}]}
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "not found", "id": ref_id})}],
            "isError": True,
        }

    if name == "drafthouse_vision_rubric":
        return {
            "content": [
                {"type": "text", "text": vision_prompt(str(args.get("artifact_hint") or ""))}
            ]
        }

    if name == "drafthouse_vision_parse":
        report = parse_vision(
            str(args.get("text") or ""),
            screenshot_path=args.get("screenshot_path"),
            round_no=int(args.get("round") or 1),
        )
        return {"content": [{"type": "text", "text": json.dumps(report.to_dict(), indent=2)}]}

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def handle_message(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "drafthouse", "version": __version__},
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name") or ""
        args = params.get("arguments") or {}
        try:
            result = call_tool(name, args)
        except Exception as exc:  # noqa: BLE001 — surface to agent
            result = {
                "content": [{"type": "text", "text": f"drafthouse error: {exc}"}],
                "isError": True,
            }
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    if msg_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_message(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
