from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class LintIssue:
    rule_id: str
    severity: str  # P0 | P1 | P2
    message: str
    line: int | None = None
    excerpt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LintResult:
    path: str
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def p0(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "P0"]

    @property
    def p1(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "P1"]

    @property
    def p2(self) -> list[LintIssue]:
        return [i for i in self.issues if i.severity == "P2"]

    @property
    def pass_gate(self) -> bool:
        return not self.p0

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "pass": self.pass_gate,
            "counts": {
                "p0": len(self.p0),
                "p1": len(self.p1),
                "p2": len(self.p2),
            },
            "issues": [i.to_dict() for i in self.issues],
        }

    def to_markdown(self) -> str:
        lines = [
            f"### drafthouse lint — `{self.path}`",
            "",
            f"**Gate:** {'PASS' if self.pass_gate else 'FAIL (P0 present)'}",
            f"P0={len(self.p0)} · P1={len(self.p1)} · P2={len(self.p2)}",
            "",
        ]
        if not self.issues:
            lines.append("_No issues._")
            return "\n".join(lines)
        for sev in ("P0", "P1", "P2"):
            group = [i for i in self.issues if i.severity == sev]
            if not group:
                continue
            lines.append(f"#### {sev}")
            for issue in group:
                loc = f"L{issue.line}: " if issue.line else ""
                lines.append(f"- `{issue.rule_id}` — {loc}{issue.message}")
            lines.append("")
        return "\n".join(lines)
