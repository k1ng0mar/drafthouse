# 5-dim self-check (L2)

## Pre-emit (always-on, 1–5)

Score silently after L1 checklist passes:

| Dim | Question |
|-----|----------|
| Philosophy | Visual posture match the brief, or default drift? |
| Hierarchy | One obvious place for the eye per screen? |
| Execution | Type, spacing, alignment, contrast — right or close? |
| Specificity | Every word/number/image specific to this brief? |
| Restraint | One accent at most twice; no competing flourishes? |

**Any dim &lt; 3/5 → fix weakest → re-score.** Two passes is normal.

## Deep review skill (optional, 0–10)

For expert review artifacts only (not every generate):

| Dim | Question |
|-----|----------|
| Philosophy | One direction or three styles in a trench coat? |
| Visual hierarchy | Stranger knows read order without being told? |
| Detail | Alignment, leading, framing, chrome polish |
| Functionality | Does it *work* for the job? |
| Innovation | One earned memorable move vs agency median |

Rules: cite evidence; score is **worst sustained band**; don’t grade-inflate;
always 5 scores; don’t critique your own artifact in the generation turn unless asked.

## Optional L4 ship gate (jury)

Composite (deep dims ×2 to 10-scale) ≥ **8.0** AND `MUST_FIX == 0`.
Off by default (`verify.jury: false`).

## Score block

```drafthouse-critique
philosophy: 4
hierarchy: 3
execution: 4
specificity: 5
restraint: 3
MUST_FIX: none
```
