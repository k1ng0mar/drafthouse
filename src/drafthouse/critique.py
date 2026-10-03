"""5-dim pre-emit self-check helpers (L2) + optional scoring scaffold (L4).

The model performs the critique inside the skill prompt; this module defines
the contract, parses score blocks, and enforces the ship gate locally.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

PREEMIT_DIMENSIONS = (
    "philosophy",
    "hierarchy",
    "execution",
    "specificity",
    "restraint",
)

DEEP_DIMENSIONS = (
    "philosophy",
    "hierarchy",
    "detail",
    "functionality",
    "innovation",
)

# OpenDesign system-prompt Step 8 (verbatim intent)
PREEMIT_PROMPT = """\
After the checklist passes, score yourself silently across five dimensions on a 1–5 scale:

1. **Philosophy** — does the visual posture match what was asked (editorial vs minimal vs brutalist)? Or did you drift back to your favourite default?
2. **Hierarchy** — does the eye land in one obvious place per screen? Or is everything competing?
3. **Execution** — typography, spacing, alignment, contrast — are they right or just close?
4. **Specificity** — is every word, number, image specific to *this* brief? Or did filler / generic stat-slop creep in?
5. **Restraint** — one accent used at most twice, one decisive flourish — or three competing flourishes?

Any dimension under 3/5 is a regression. Go back, fix the weakest, re-score. Two passes is normal. Then finish with a concise file summary.
"""

_SCORE_BLOCK = re.compile(
    r"```drafthouse-critique\s*(?P<body>[\s\S]*?)```",
    re.I,
)
_SCORE_LINE = re.compile(
    r"^\s*(?P<dim>philosophy|hierarchy|execution|specificity|restraint|detail|functionality|innovation)\s*[:=]\s*(?P<score>[1-9]|10)\s*$",
    re.I | re.M,
)
_MUST_FIX = re.compile(r"^\s*(?:[-*]\s*)?(?:MUST_FIX|must_fix)\s*[:=-]\s*(?P<msg>.+)$", re.I | re.M)


@dataclass(slots=True)
class CritiqueScores:
    scores: dict[str, int] = field(default_factory=dict)
    must_fix: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def min_score(self) -> int | None:
        if not self.scores:
            return None
        return min(self.scores.values())

    @property
    def passes_preemit(self) -> bool:
        """Pre-emit gate: every scored dim >= 3/5."""
        if not self.scores:
            return False
        return all(s >= 3 for s in self.scores.values())

    @property
    def composite_deep(self) -> float | None:
        if not self.scores:
            return None
        return sum(self.scores.values()) / len(self.scores)

    @property
    def passes_deep_ship(self) -> bool:
        """Optional L4: composite scaled to 10 >= 8.0 AND no open MUST_FIX."""
        if not self.scores:
            return False
        composite = (sum(self.scores.values()) / len(self.scores)) * 2.0
        return composite >= 8.0 and not self.must_fix

    def to_dict(self) -> dict:
        return {
            "scores": self.scores,
            "must_fix": self.must_fix,
            "min_score": self.min_score,
            "passes_preemit": self.passes_preemit,
            "passes_deep_ship": self.passes_deep_ship,
        }


def parse_critique(text: str) -> CritiqueScores:
    """Parse a ```drafthouse-critique block, or score lines anywhere."""
    result = CritiqueScores()
    body = text
    block = _SCORE_BLOCK.search(text)
    if block:
        body = block.group("body")
        result.notes = body.strip()[:500]
    for m in _SCORE_LINE.finditer(body):
        result.scores[m.group("dim").lower()] = int(m.group("score"))
    for m in _MUST_FIX.finditer(body):
        msg = m.group("msg").strip()
        if msg and msg.lower() not in {"none", "n/a", "-"}:
            result.must_fix.append(msg)
    return result


# Close-margin threshold on the 1-5 composite. A 0.2 gap is one average step
# on the 5-dim scale, i.e. the two candidates are one point apart across the
# five dimensions.
JUDGE_CLOSE_MARGIN = 0.2


@dataclass(slots=True)
class JudgeDecision:
    candidates: list[dict] = field(default_factory=list)
    winner: str | None = None
    close: bool = False

    def to_dict(self) -> dict:
        return {
            "candidates": self.candidates,
            "winner": self.winner,
            "close": self.close,
        }


def judge_candidates(blocks: dict[str, str]) -> JudgeDecision:
    """Rank candidate critique blocks.

    A candidate ranks when it passes pre-emit (every dim >= 3). Winner is the
    highest composite among passing candidates. A top-two gap within
    JUDGE_CLOSE_MARGIN sets close=True: show the human the choice instead of
    picking silently.
    """
    ranked = []
    for name, text in blocks.items():
        scores = parse_critique(text)
        ranked.append(
            {
                "name": name,
                "scores": scores.scores,
                "composite": scores.composite_deep,
                "min_dim": scores.min_score,
                "passes_preemit": scores.passes_preemit,
                "must_fix": scores.must_fix,
            }
        )
    passing = [r for r in ranked if r["passes_preemit"]]
    decision = JudgeDecision(candidates=ranked)
    if not passing:
        return decision
    passing.sort(key=lambda r: r["composite"], reverse=True)
    decision.winner = passing[0]["name"]
    if len(passing) > 1:
        # round to 2dp before comparing: composites are averages of ints on a
        # 1-5 scale, and 4.0 - 3.8 is 0.20000000000000018 in float.
        gap = round(passing[0]["composite"] - passing[1]["composite"], 2)
        decision.close = gap <= JUDGE_CLOSE_MARGIN
    return decision


def format_score_block(scores: dict[str, int], must_fix: list[str] | None = None) -> str:
    lines = ["```drafthouse-critique"]
    for dim in PREEMIT_DIMENSIONS:
        if dim in scores:
            lines.append(f"{dim}: {scores[dim]}")
    for dim, value in scores.items():
        if dim not in PREEMIT_DIMENSIONS:
            lines.append(f"{dim}: {value}")
    for item in must_fix or []:
        lines.append(f"MUST_FIX: {item}")
    lines.append("```")
    return "\n".join(lines)
