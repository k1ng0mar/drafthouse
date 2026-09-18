"""Hermes installer — writes MCP config + copies skills without forking core.

Safe by default: --dry-run prints the plan; refuses to overwrite user skill
files unless --force.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional
    yaml = None


def product_root() -> Path:
    return Path(__file__).resolve().parents[2]


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()


def skills_source() -> Path:
    return product_root() / "skills"


def design_systems_source() -> Path:
    return product_root() / "design-systems"


def build_mcp_block(python_bin: str, product: Path) -> dict:
    # Zero-install: PYTHONPATH injection (works even if product dir is noexec).
    return {
        "command": python_bin,
        "args": ["-m", "drafthouse.mcp_server"],
        "env": {
            "DRAFTHOUSE_ROOT": str(product),
            "PYTHONPATH": str(product / "src"),
        },
        "description": "Drafthouse design verify + lint MCP for Hermes",
    }


def render_yaml_snippet(python_bin: str, product: Path) -> str:
    block = build_mcp_block(python_bin, product)
    args = list(block.get("args") or [])
    lines = [
        "# Add under ~/.hermes/config.yaml  (mcp: → servers: → drafthouse:)",
        "mcp:",
        "  servers:",
        "    drafthouse:",
        f"      command: {block['command']}",
        "      args:",
    ]
    for a in args:
        lines.append(f"        - {a}")
    lines += [
        "      env:",
        f"        DRAFTHOUSE_ROOT: {block['env']['DRAFTHOUSE_ROOT']}",
        f"        PYTHONPATH: {block['env']['PYTHONPATH']}",
        f"      description: {json_quote(block['description'])}",
        "",
        "drafthouse:",
        "  design_system: default",
        "  verify:",
        "    enabled: true",
        "    preemit_5dim: true",
        "    lint_on_write: true",
        "    max_correct_rounds: 3",
        "    ship_requires_p0_clear: true",
        "    vision_gate: false",
    ]
    return "\n".join(lines) + "\n"


def json_quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def merge_hermes_config(config_path: Path, python_bin: str, product: Path, dry_run: bool) -> str:
    snippet = render_yaml_snippet(python_bin, product)
    if not config_path.exists():
        action = f"would create {config_path}" if dry_run else f"created {config_path}"
        if not dry_run:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(snippet, encoding="utf-8")
        return action

    text = config_path.read_text(encoding="utf-8")
    if "drafthouse:" in text and "mcp:" in text and "DRAFTHOUSE_ROOT" in text:
        return f"{config_path} already contains drafthouse MCP block (skipped)"

    # Append a clearly marked section — safest without a YAML dependency.
    marker = "# --- drafthouse (managed) ---"
    addition = f"\n{marker}\n{snippet}"
    if dry_run:
        return f"would append drafthouse MCP block to {config_path}"
    backup = config_path.with_suffix(config_path.suffix + ".bak.drafthouse")
    shutil.copy2(config_path, backup)
    config_path.write_text(text.rstrip() + addition, encoding="utf-8")
    return f"appended drafthouse block to {config_path} (backup: {backup.name})"


def copy_tree(src: Path, dst: Path, force: bool, dry_run: bool) -> list[str]:
    notes: list[str] = []
    if not src.exists():
        notes.append(f"missing source: {src}")
        return notes
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = dst / rel
        if target.exists() and not force:
            notes.append(f"skip (exists): {target}")
            continue
        if dry_run:
            notes.append(f"would copy: {path} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        notes.append(f"copied: {rel}")
    return notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Drafthouse into a Hermes home")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill files")
    parser.add_argument("--hermes-home", default=None)
    parser.add_argument("--skip-config", action="store_true")
    parser.add_argument("--skip-skills", action="store_true")
    args = parser.parse_args(argv)

    product = product_root()
    home = Path(args.hermes_home).expanduser() if args.hermes_home else hermes_home()
    skills_dst = home / "skills"
    ds_dst = home / "design-systems" / "drafthouse"
    python_bin = sys.executable

    print(f"drafthouse product: {product}")
    print(f"hermes home:        {home}")
    print(f"mode:               {'dry-run' if args.dry_run else 'install'}")
    print()

    if not args.skip_skills:
        print("== skills ==")
        for note in copy_tree(skills_source(), skills_dst, force=args.force, dry_run=args.dry_run):
            print(f"  {note}")
        print("== design-systems ==")
        for note in copy_tree(design_systems_source(), ds_dst, force=args.force, dry_run=args.dry_run):
            print(f"  {note}")

    if not args.skip_config:
        print("== hermes config ==")
        config_path = home / "config.yaml"
        note = merge_hermes_config(config_path, python_bin, product, dry_run=args.dry_run)
        print(f"  {note}")
        print()
        print("YAML reference:")
        print(render_yaml_snippet(python_bin, product))

    print()
    print("Next:")
    print("  1. Make wrappers executable:  chmod +x bin/drafthouse bin/drafthouse-mcp")
    print("  2. Put bin/ on PATH (or call by absolute path)")
    print("  3. Restart Hermes / new conversation so skills + MCP load")
    print("  4. In Hermes:  /hermes-design-verify   or ask to lint an HTML artifact")
    print("  Optional pip install if you want the `drafthouse` console script globally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
