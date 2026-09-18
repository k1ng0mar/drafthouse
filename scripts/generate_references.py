"""Generate references/catalog.json + by-category markdown notes."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drafthouse.references import CATEGORIES, REFERENCES, write_catalog  # noqa: E402


def write_category_docs() -> list[Path]:
    by_cat: dict[str, list] = defaultdict(list)
    for ref in REFERENCES:
        by_cat[ref.category].append(ref)
    out_dir = ROOT / "references" / "by-category"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for category in sorted(by_cat):
        path = out_dir / f"{category}.md"
        lines = [
            f"# {category}",
            "",
            "Study structure/hierarchy only. Re-skin via active `DESIGN.md` tokens.",
            "",
        ]
        for ref in sorted(by_cat[category], key=lambda r: r.name.lower()):
            lines.append(f"## {ref.name}")
            lines.append("")
            lines.append(f"- **URL:** {ref.url}")
            lines.append(f"- **ID:** `{ref.id}`")
            lines.append(f"- **Best for:** {ref.best_for}")
            tags = ", ".join(ref.tags)
            lines.append(f"- **Tags:** {tags}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        written.append(path)
    # category index
    index = ROOT / "references" / "CATEGORIES.md"
    idx_lines = ["# Reference categories", ""]
    for category in CATEGORIES:
        ids = [r.id for r in REFERENCES if r.category == category]
        idx_lines.append(f"- [`{category}`](by-category/{category}.md) — {', '.join(ids)}")
    idx_lines.append("")
    index.write_text("\n".join(idx_lines), encoding="utf-8")
    written.append(index)
    return written


if __name__ == "__main__":
    catalog = write_catalog()
    docs = write_category_docs()
    print(catalog)
    for d in docs:
        print(d)
    print(f"references: {len(REFERENCES)}")
    print(f"categories: {len(CATEGORIES)}")
