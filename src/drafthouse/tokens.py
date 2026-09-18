"""Design-system package loading + token checks.

Package shape (portable):
  DESIGN.md      brand contract the agent must follow
  tokens.css     :root custom properties
  manifest.json  optional metadata
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_TOKEN_RE = re.compile(
    r"(?P<name>--[a-zA-Z0-9_-]+)\s*:\s*(?P<value>[^;]+);",
    re.M,
)
_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,8})\b")
_VAR_USE_RE = re.compile(r"var\((--[a-zA-Z0-9_-]+)\)")


@dataclass(slots=True)
class DesignSystem:
    root: Path
    name: str
    design_md: str
    tokens_css: str
    tokens: dict[str, str] = field(default_factory=dict)
    hex_palette: set[str] = field(default_factory=set)

    @classmethod
    def load(cls, path: str | Path) -> "DesignSystem":
        root = Path(path).expanduser().resolve()
        if root.is_file():
            root = root.parent
        design_md = ""
        tokens_css = ""
        dm = root / "DESIGN.md"
        tc = root / "tokens.css"
        if dm.exists():
            design_md = dm.read_text(encoding="utf-8", errors="replace")
        if tc.exists():
            tokens_css = tc.read_text(encoding="utf-8", errors="replace")
        tokens: dict[str, str] = {}
        for m in _TOKEN_RE.finditer(tokens_css):
            tokens[m.group("name")] = m.group("value").strip()
        palette = {h.lower() for h in _HEX_RE.findall(tokens_css)}
        palette |= {h.lower() for h in _HEX_RE.findall(design_md)}
        name = root.name
        manifest = root / "manifest.json"
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                name = str(data.get("name") or name)
            except json.JSONDecodeError:
                pass
        return cls(
            root=root,
            name=name,
            design_md=design_md,
            tokens_css=tokens_css,
            tokens=tokens,
            hex_palette=palette,
        )


@dataclass(slots=True)
class TokenIssue:
    kind: str
    message: str
    value: str | None = None

    def to_dict(self) -> dict:
        return {"kind": self.kind, "message": self.message, "value": self.value}


def check_artifact_tokens(artifact_text: str, system: DesignSystem) -> list[TokenIssue]:
    """Heuristic token adherence for HTML/CSS artifacts."""
    issues: list[TokenIssue] = []
    if not system.tokens and not system.hex_palette:
        issues.append(
            TokenIssue(
                kind="system-empty",
                message=f"Design system '{system.name}' has no tokens.css / DESIGN.md palette",
            )
        )
        return issues

    hexes = {h.lower() for h in _HEX_RE.findall(artifact_text)}
    if system.hex_palette:
        unknown = sorted(h for h in hexes if h not in system.hex_palette)
        # allow pure black/white/near-neutrals
        neutrals = {
            "#000",
            "#000000",
            "#fff",
            "#ffffff",
            "#fff5e9",
            "#12160f",
            "#1e241d",
            "#ecebe2",
        }
        unknown = [u for u in unknown if u not in neutrals]
        if unknown:
            issues.append(
                TokenIssue(
                    kind="off-palette-hex",
                    message=(
                        f"{len(unknown)} hex color(s) not in design system "
                        f"'{system.name}' palette"
                    ),
                    value=", ".join(unknown[:12]),
                )
            )

    used_vars = set(_VAR_USE_RE.findall(artifact_text))
    if system.tokens:
        missing = sorted(v for v in used_vars if v not in system.tokens)
        if missing:
            issues.append(
                TokenIssue(
                    kind="unknown-css-var",
                    message="CSS vars used that are not in tokens.css",
                    value=", ".join(missing[:12]),
                )
            )
        declared_root = set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", artifact_text))
        if declared_root and system.tokens:
            local_only = sorted(
                v
                for v in declared_root
                if v.startswith("--") and v not in system.tokens and "--tw" not in v
            )
            # only flag brand-looking tokens
            brandish = [v for v in local_only if any(k in v for k in ("color", "brand", "accent", "font", "bg", "text"))]
            if brandish:
                issues.append(
                    TokenIssue(
                        kind="local-token-override",
                        message="Artifact defines brand-like tokens not in the design system",
                        value=", ".join(brandish[:12]),
                    )
                )
    return issues


def bind_snippet(system: DesignSystem, max_chars: int = 4000) -> str:
    """Short prompt-safe bind block for skills / MCP."""
    lines = [
        f"### Active design system: {system.name}",
        f"Package path: `{system.root}`",
        "",
        "Bind these tokens to `:root` (or use them consistently):",
        "```css",
        (system.tokens_css or "/* no tokens.css */")[:max_chars],
        "```",
    ]
    if system.design_md:
        lines += ["", "#### Brand contract (DESIGN.md excerpt)", "", system.design_md[:max_chars]]
    return "\n".join(lines)
