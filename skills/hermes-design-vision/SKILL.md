---
name: hermes-design-vision
description: L4 vision gate — screenshot the artifact, score visually, fix MUST_FIX before ship
version: 0.1.0
author: Drafthouse
license: MIT
metadata:
  hermes:
    pairs_with: [hermes-design-verify, hermes-design-references]
---

# Vision gate (L4)

Optional closed loop on Hermes: **render → screenshot → score → fix → re-check**.
Use when `drafthouse.vision_gate: true` or the human explicitly asks for visual QA.

Does **not** replace L1–L3. Vision can pass while lint fails — lint still wins on P0.

## Tools on Hermes

| Step | Tool |
|------|------|
| Open artifact | `desktop_preview` (or `open_preview`) with the HTML file/URL |
| Capture | screenshot via preview/browser tools if available; else ask human for a screenshot path |
| Score | `vision_analyze` on the image with the rubric below |
| Log | write JSON via project notes or MCP after parse |

MCP helpers:

- `drafthouse_vision_rubric` — full rubric text
- `drafthouse_vision_parse` — parse model output → gate JSON
- `drafthouse_references_search` — if craft issues are structural, look up the pattern

## Drafthouse runner (recommended)

```bash
bash bin/drafthouse vision gate plan path/to/artifact.html
bash bin/drafthouse vision gate parse --artifact path/to/artifact.html \
  --screenshot path/to/shot.png --text-file path/to/vision-output.txt
bash bin/drafthouse vision gate rounds path/to/artifact.html
```

Exit codes: `0` ship · `1` fix · `2` max rounds exceeded.
Logs: `DRAFTHOUSE_GATE_DIR` or `~/.drafthouse/gates/*.jsonl`.

MCP: `drafthouse_vision_rubric` / `drafthouse_vision_parse`.

## Rubric (send to vision_analyze)

```
You are a strict design reviewer scoring a SCREENSHOT of a rendered UI artifact.
Score only what you can SEE.

0–10 each: philosophy, hierarchy, execution, specificity, restraint, accessibility, craft
Also list MUST_FIX items (screenshot-verifiable).

Return only:

```drafthouse-vision
philosophy: N
hierarchy: N
execution: N
specificity: N
restraint: N
accessibility: N
craft: N
MUST_FIX: ...
notes: <evidence-based>
```
```

Exact text: MCP `drafthouse_vision_rubric` or `python3 -m drafthouse.vision_cli rubric`.

## Ship gate

| Check | Rule |
|-------|------|
| Floor | every dimension ≥ 5/10 |
| Ship | composite ≥ **8.0** AND `MUST_FIX` empty |
| Rounds | max **3** correct loops, then surface honestly to the human |

Composite = mean of scored dims.

## Loop

```
1. Ensure L1–L3 passed (lint + tokens)
2. desktop_preview(artifact)
3. vision_analyze(screenshot, rubric)
4. drafthouse_vision_parse(text)
5. if not passes_ship and round < 3:
     fix MUST_FIX + lowest dims
     re-render → goto 2
6. Present with gate line:
   Vision SHIP · composite=8.4 · min=7 · MUST_FIX=0 · round=2
```

## Reference-assisted fixes

If hierarchy/craft fail:

1. Identify pattern (hero, pricing, navbar…)
2. `drafthouse_references_search query=hero`
3. Restate structure in DESIGN.md tokens
4. Re-generate that section only
5. Re-run lint + vision

## Do not

- Hallucinate scores without a real screenshot
- Average up weak pages because the hero looks fine
- Treat vision pass as license to skip P0 lint
- Spend unbounded rounds — after 3, ask the human
