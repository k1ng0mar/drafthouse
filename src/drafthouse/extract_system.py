"""MVP: extract a draft design-system package from CSS/HTML frequency heuristics."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

_HEX = re.compile(r"#(?:[0-9a-fA-F]{3,8})\b")
_FONT = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)
_VAR = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);")


def extract_from_text(text: str, name: str = "extracted") -> dict:
    hexes = Counter(h.lower() for h in _HEX.findall(text))
    fonts = Counter()
    for m in _FONT.finditer(text):
        fonts[re.sub(r"\s+", " ", m.group(1)).strip()[:60]] += 1
    vars_ = {m.group(1): m.group(2).strip() for m in _VAR.finditer(text)}
    # drop pure black/white noise from top palette unless only colors present
    noise = {"#000", "#000000", "#fff", "#ffffff", "#fff5e9"}
    palette = [(c, n) for c, n in hexes.most_common(24) if c not in noise] or hexes.most_common(8)
    return {
        "name": name,
        "palette": palette,
        "fonts": fonts.most_common(6),
        "css_vars": dict(list(vars_.items())[:40]),
        "notes": [
            "Draft only — human review required before publishing as org default.",
            "Frequencies are not brand judgments; drop accidental UI grays.",
        ],
    }


def render_package(data: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = data["name"]
    lines = [
        f"# {name} (extracted draft)",
        "",
        "Auto-extracted draft. Review tokens, delete noise, set type roles before use.",
        "",
        "## Palette candidates",
    ]
    for color, count in data["palette"][:12]:
        lines.append(f"- `{color}` ×{count}")
    lines += ["", "## Font-family candidates"]
    for font, count in data["fonts"]:
        lines.append(f"- `{font}` ×{count}")
    lines += ["", "## Notes"]
    lines += [f"- {n}" for n in data["notes"]]
    (out_dir / "DESIGN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    css_lines = [f":root {{ /* extracted:{name} */ "]
    for i, (color, _) in enumerate(data["palette"][:12]):
        css_lines.append(f"  --x-color-{i}: {color};")
    for i, (font, _) in enumerate(data["fonts"][:3]):
        css_lines.append(f"  --x-font-{i}: {font};")
    for k, v in list(data["css_vars"].items())[:30]:
        css_lines.append(f"  {k}: {v};")
    css_lines.append("}")
    (out_dir / "tokens.css").write_text("\n".join(css_lines) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(
        f'{{"name": "{name}", "title": "{name}", "version": "0.0.1-draft", "spec": "drafthouse-design-system/v1", "extracted": true}}\n',
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract draft design tokens from CSS/HTML")
    parser.add_argument("input", help="CSS or HTML file")
    parser.add_argument("--name", default=None)
    parser.add_argument("--out", required=True, help="Output package directory")
    args = parser.parse_args(argv)
    src = Path(args.input).expanduser()
    text = src.read_text(encoding="utf-8", errors="replace")
    name = args.name or src.stem
    data = extract_from_text(text, name=name)
    out = Path(args.out).expanduser()
    render_package(data, out)
    print(f"wrote draft package → {out}")
    print(f"palette candidates: {len(data['palette'])} · fonts: {len(data['fonts'])}")
    print("REVIEW REQUIRED before design_system pin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
