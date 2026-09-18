"""Vision gate (L4) — structured visual scoring contract for Hermes.

Hermes tools: `desktop_preview` + `vision_analyze`.
This module does not call models; it:
  - builds the vision rubric prompt
  - defines the score JSON schema
  - parses vision output into CritiqueScores
  - applies the ship gate + round limits
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from drafthouse.critique import CritiqueScores, PREEMIT_DIMENSIONS, format_score_block

VISION_DIMENSIONS = (
    "philosophy",
    "hierarchy",
    "execution",
    "specificity",
    "restraint",
    "accessibility",
    "craft",
)

VISION_RUBRIC = """You are a strict design reviewer scoring a SCREENSHOT of a rendered UI artifact.
Score only what you can SEE. Do not invent brand context.

Dimensions (0–10 integers):
1. philosophy — Does the visual posture match an intentional direction, or generic AI default?
2. hierarchy — Is there one obvious primary focus per viewport? Clear type/size tiers?
3. execution — Alignment, spacing rhythm, contrast, crop, baseline consistency.
4. specificity — Does copy/imagery feel specific to this product/brief (not stock lorem vibes)?
5. restraint — Accent discipline; no competing flourishes; chrome stays out of the way.
6. accessibility — Text contrast, target size, focus visibility if inferable.
7. craft — The 10% polish: edge alignment, consistent radii, honest empty space.

Also list concrete MUST_FIX items (0–8), each one screenshot-verifiable.

Return ONLY a fenced block:

```drafthouse-vision
philosophy: <0-10>
hierarchy: <0-10>
execution: <0-10>
specificity: <0-10>
restraint: <0-10>
accessibility: <0-10>
craft: <0-10>
MUST_FIX: <one item>
MUST_FIX: <optional more>
notes: <one short paragraph>
```

Scoring discipline:
- Cite visual evidence in notes (layout region, not feelings).
- Score the WORST sustained band when quality is uneven — do not average up.
- A 7 means strong, not acceptable. If every score is 8+, you are not reviewing.
- Innovation is not required for production plates; craft + hierarchy matter more.
"""

_VISION_BLOCK = re.compile(r"```drafthouse-vision\s*(?P<body>[\s\S]*?)```", re.I)
_SCORE_LINE = re.compile(
    r"^\s*(?P<dim>philosophy|hierarchy|execution|specificity|restraint|accessibility|craft)\s*[:=]\s*(?P<score>\d{1,2})\s*$",
    re.I | re.M,
)
_MUST_FIX = re.compile(r"^\s*(?:[-*]\s*)?MUST_FIX\s*[:=-]\s*(?P<msg>.+)$", re.I | re.M)
_NOTES = re.compile(r"^\s*notes\s*[:=-]\s*(?P<msg>.+)$", re.I | re.M)


@dataclass(slots=True)
class VisionReport:
    scores: dict[str, int] = field(default_factory=dict)
    must_fix: list[str] = field(default_factory=list)
    notes: str = ""
    screenshot_path: str | None = None
    round: int = 1

    @property
    def composite(self) -> float | None:
        if not self.scores:
            return None
        return sum(self.scores.values()) / len(self.scores)

    @property
    def min_score(self) -> int | None:
        if not self.scores:
            return None
        return min(self.scores.values())

    @property
    def passes_ship(self) -> bool:
        """Default L4: composite >= 8.0 AND no open MUST_FIX."""
        if not self.scores:
            return False
        c = self.composite or 0.0
        return c >= 8.0 and not self.must_fix

    @property
    def passes_floor(self) -> bool:
        """Hard floor: no dimension below 5/10."""
        if not self.scores:
            return False
        return all(s >= 5 for s in self.scores.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": self.scores,
            "must_fix": self.must_fix,
            "notes": self.notes,
            "composite": self.composite,
            "min_score": self.min_score,
            "passes_floor": self.passes_floor,
            "passes_ship": self.passes_ship,
            "screenshot_path": self.screenshot_path,
            "round": self.round,
        }

    def gate_summary(self) -> str:
        c = self.composite
        c_s = f"{c:.1f}" if c is not None else "n/a"
        mf = len(self.must_fix)
        status = "SHIP" if self.passes_ship else "FIX"
        return (
            f"Vision {status} · composite={c_s} · min={self.min_score} · "
            f"MUST_FIX={mf} · round={self.round}"
        )


def vision_prompt(artifact_hint: str = "") -> str:
    header = VISION_RUBRIC
    if artifact_hint:
        header += f"\n\nArtifact context: {artifact_hint}\n"
    return header


def parse_vision(text: str, screenshot_path: str | None = None, round_no: int = 1) -> VisionReport:
    report = VisionReport(screenshot_path=screenshot_path, round=round_no)
    body = text
    block = _VISION_BLOCK.search(text)
    if block:
        body = block.group("body")
    for m in _SCORE_LINE.finditer(body):
        dim = m.group("dim").lower()
        score = int(m.group("score"))
        report.scores[dim] = max(0, min(10, score))
    for m in _MUST_FIX.finditer(body):
        msg = m.group("msg").strip()
        if msg and msg.lower() not in {"none", "n/a", "-"}:
            report.must_fix.append(msg)
    notes = _NOTES.search(body)
    if notes:
        report.notes = notes.group("msg").strip()
    return report


def format_vision_block(
    scores: dict[str, int],
    must_fix: list[str] | None = None,
    notes: str = "",
) -> str:
    lines = ["```drafthouse-vision"]
    for dim in VISION_DIMENSIONS:
        if dim in scores:
            lines.append(f"{dim}: {scores[dim]}")
    for dim, value in scores.items():
        if dim not in VISION_DIMENSIONS:
            lines.append(f"{dim}: {value}")
    for item in must_fix or []:
        lines.append(f"MUST_FIX: {item}")
    if notes:
        lines.append(f"notes: {notes}")
    lines.append("```")
    return "\n".join(lines)


def preemit_from_vision(report: VisionReport) -> CritiqueScores:
    """Map vision scores (0–10) onto pre-emit (1–5) for a unified gate log."""
    mapped: dict[str, int] = {}
    for dim in PREEMIT_DIMENSIONS:
        if dim in report.scores:
            mapped[dim] = max(1, min(5, round(report.scores[dim] / 2)))
    return CritiqueScores(scores=mapped, must_fix=list(report.must_fix), notes=report.notes)


def write_gate_log(path: str | Path, payload: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing: list[Any] = []
    if p.exists():
        try:
            existing = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = [existing]
        except json.JSONDecodeError:
            existing = []
    existing.append(payload)
    p.write_text(json.dumps(existing, indent=2), encoding="utf-8")
