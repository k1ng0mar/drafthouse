"""Hermes installer — copies skills/design-systems/references into a Hermes home.

Simplest-to-install shape:
  1. copy skills, design-systems, and the reference catalog into the Hermes home
  2. write the small `drafthouse:` admin block (default design system, gate flags)
  3. print the exact `hermes mcp add` command for the user to run — no YAML surgery

The MCP server registration is left to `hermes mcp add` because that is the
sanctioned Hermes path: it validates the config, manages the key, and `hermes mcp
remove` is the matching uninstall. The installer used to hand-edit config.yaml
with a regex merge of `mcp_servers:`; that code is gone.

Safe by default: --dry-run prints the plan; refuses to overwrite user skill
files unless --force.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def product_root() -> Path:
    return Path(__file__).resolve().parents[2]


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()


def skills_source() -> Path:
    return product_root() / "skills"


def design_systems_source() -> Path:
    return product_root() / "design-systems"


def references_source() -> Path:
    return product_root() / "references"


def mcp_shim(product: Path) -> Path:
    return product / "bin" / "drafthouse-mcp"


# The top-level `drafthouse:` block documents the default design system and the
# gate flags the skills read. This is a single, stable, top-level key — never a
# regex merge of an existing `mcp_servers:` map.
ADMIN_BLOCK = """\
drafthouse:
  design_system: default
  verify:
    enabled: true
    preemit_5dim: true
    lint_on_write: true
    max_correct_rounds: 3
    ship_requires_p0_clear: true
    vision_gate: false
  references:
    enabled: true
    catalog: auto  # copies under ~/.hermes/design-systems/drafthouse/references
"""


def mcp_add_command(product: Path) -> str:
    """The exact command the user runs to register the MCP server."""
    shim = mcp_shim(product)
    return (
        f"hermes mcp add drafthouse "
        f"--command {shim} "
        f"--env DRAFTHOUSE_ROOT={product} "
        f"--env PYTHONPATH={product / 'src'}"
    )


def write_admin_block(config_path: Path, dry_run: bool) -> str:
    """Write or refresh the top-level `drafthouse:` admin block.

    Idempotent: if a `drafthouse:` top-level block already exists it is left
    alone (user may have tuned values). Only written when missing.
    """
    if config_path.exists():
        text = config_path.read_text(encoding="utf-8")
        if "\ndrafthouse:" in text or text.startswith("drafthouse:"):
            return f"{config_path} already has a `drafthouse:` block (left as-is)"
    if dry_run:
        return f"would write `drafthouse:` block to {config_path}"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    suffix = "" if not existing or existing.endswith("\n") else "\n"
    config_path.write_text(existing + suffix + "\n" + ADMIN_BLOCK, encoding="utf-8")
    return f"wrote `drafthouse:` block to {config_path}"


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


def uninstall_skills(home: Path, dry_run: bool) -> list[str]:
    notes: list[str] = []
    skills_dst = home / "skills"
    for name in (
        "drafthouse-design-verify",
        "drafthouse-design-systems",
        "drafthouse-design-references",
        "drafthouse-design-vision",
    ):
        target = skills_dst / name
        if not target.exists():
            notes.append(f"absent: {target}")
            continue
        if dry_run:
            notes.append(f"would remove: {target}")
            continue
        shutil.rmtree(target)
        notes.append(f"removed: {target}")
    ds_dst = home / "design-systems" / "drafthouse"
    if ds_dst.exists():
        notes.append(f"note: manually remove {ds_dst} if you no longer use it")
    notes.append("note: run `hermes mcp remove drafthouse` to unregister the MCP server")
    return notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install Drafthouse skills into a Hermes home (no YAML surgery)"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill files")
    parser.add_argument("--hermes-home", default=None)
    parser.add_argument("--skip-admin-block", action="store_true")
    parser.add_argument("--uninstall", action="store_true", help="Remove installed drafthouse skills")
    args = parser.parse_args(argv)

    product = product_root()
    home = Path(args.hermes_home).expanduser() if args.hermes_home else hermes_home()

    print(f"drafthouse product: {product}")
    print(f"hermes home:        {home}")
    print(f"mode:               {'uninstall' if args.uninstall else ('dry-run' if args.dry_run else 'install')}")
    print()

    if args.uninstall:
        for note in uninstall_skills(home, dry_run=args.dry_run):
            print(f"  {note}")
        print()
        print("Done. The admin `drafthouse:` block and the MCP registration are yours to keep or remove:")
        print(f"  hermes mcp remove drafthouse")
        return 0

    skills_dst = home / "skills"
    ds_dst = home / "design-systems" / "drafthouse"

    print("== skills ==")
    for note in copy_tree(skills_source(), skills_dst, force=args.force, dry_run=args.dry_run):
        print(f"  {note}")
    print("== design-systems ==")
    for note in copy_tree(design_systems_source(), ds_dst, force=args.force, dry_run=args.dry_run):
        print(f"  {note}")
    print("== references catalog ==")
    ref_dst = ds_dst / "references"
    for note in copy_tree(references_source(), ref_dst, force=args.force, dry_run=args.dry_run):
        print(f"  {note}")

    if not args.skip_admin_block:
        print("== admin config ==")
        config_path = home / "config.yaml"
        print(f"  {write_admin_block(config_path, dry_run=args.dry_run)}")

    print()
    print("Next (MCP server — one command, no YAML editing):")
    print(f"  {mcp_add_command(product)}")
    print("  hermes mcp test drafthouse")
    print("  restart Hermes / start a new session so the skills + MCP load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
