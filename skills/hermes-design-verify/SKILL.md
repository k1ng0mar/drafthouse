---
name: hermes-design-verify
description: Always-on design quality gate — lint, 5-dim self-check, token bind before you show work
version: 0.2.0
author: Drafthouse
license: MIT
metadata:
  hermes:
    pairs_with: [claude-design, design-md, popular-web-designs, hermes-design-references, hermes-design-vision]
---

# Hermes design verify

You are about to produce or revise a **visual artifact** (HTML page, deck slide,
one-pager, email, mockup). Claude Design-grade quality means **check and correct
before the human treats it as done**.

Process taste and layout live in `creative/claude-design`. Brand systems live in
`creative/popular-web-designs` / `creative/design-md`. Pattern galleries live in
`hermes-design-references`. **This skill owns the gate.**

## Binding order

1. If `~/.hermes/design-systems/drafthouse/<name>/` or project `design-systems/` has a package, bind `tokens.css` + `DESIGN.md` first.
2. Else use MCP `drafthouse_bind` / `drafthouse bind --system default`.
3. Else pick a coherent direction yourself and declare it in a `:root` comment.

## Mandatory loop (do not skip)

```
Lookup refs (if pattern UI) → Plan → Write file → L1 checklist → L2 5-dim
→ L3 lint → fix → re-check → (optional L4 vision) → THEN show human
```

### L3.5 — Pattern references (before generate)

For nav / heroes / sections / pricing / dashboards / footers / CTAs, look up structure first:

```
MCP: drafthouse_references_search  query=hero|navbar|footer|cta|pricing|bento
CLI: bash bin/drafthouse refs search hero
```

Catalog: `references/catalog.json` + `references/by-category/*.md`.
Steal **structure**, not pixels. Re-skin via tokens.

### L1 — P0 checklist

Read `references/checklist.md`. **Every P0 must pass** before you present the artifact.
If a P0 fails, fix the file, then re-read the checklist.

### L2 — Silent 5-dim self-check

After L1 passes, score yourself silently (1–5):

1. **Philosophy** — posture matches the brief? (editorial / minimal / brutalist…)
2. **Hierarchy** — one obvious place for the eye per screen?
3. **Execution** — type, spacing, alignment, contrast — right, not “close”?
4. **Specificity** — every word/number/image specific to *this* brief?
5. **Restraint** — one accent at most twice; no competing flourishes?

**Any dimension &lt; 3/5 is a regression.** Fix the weakest, re-score. Two passes is normal.

When you must persist scores (debug or jury mode), emit:

```drafthouse-critique
philosophy: 4
hierarchy: 3
execution: 4
specificity: 5
restraint: 3
MUST_FIX: none
```

### L3 — Deterministic lint

```bash
bash bin/drafthouse lint path/to/artifact.html --system design-systems/default
# or MCP tool: drafthouse_lint
```

If **any P0** appears → fix and re-run. Do not hand off with failing P0.
Token off-palette colors also fail the gate when a design system is active.

### L4 — Optional vision (config `vision_gate: true`)

Use skill **`hermes-design-vision`** when enabled or when the human asks for visual QA:

1. `desktop_preview` the artifact  
2. `vision_analyze` screenshot with MCP `drafthouse_vision_rubric`  
3. MCP `drafthouse_vision_parse` → ship if composite ≥ 8.0 and no MUST_FIX  
4. Max **3** correct rounds, then surface honestly  

Lint P0 still wins over a pretty screenshot.

## Anti-slop (must fix when lint flags)

- Purple/violet gradients; default AI indigo
- Emoji-as-icons (✨🚀🎯)
- Invented metrics (“10× faster”, “99.9% uptime”)
- Filler copy (Feature One, lorem ipsum)
- Inter/Roboto/Arial as *display* faces
- Designer/demo chrome leaking into product UI

When you lack a real value, use an honest stub (`—`, grey block, labelled placeholder).

## Presentation rule

Default: show the human **verified** work, with a one-line gate summary:

> Gate: P0=0 · 5-dim min=4 · tokens=pass · system=`default` · refs=hero,navbar

With vision on, append: `Vision SHIP · composite=8.4 · MUST_FIX=0 · round=2`

If they ask to see work mid-loop, label it **unverified** until gates pass.

## Commands

| Intent | Call |
|--------|------|
| Bind system | MCP `drafthouse_bind` |
| Lint file | MCP `drafthouse_lint` / `bash bin/drafthouse lint <file>` |
| Tokens | MCP `drafthouse_tokens_check` |
| Pre-emit prompt | MCP `drafthouse_selfcheck` |
| Parse scores | MCP `drafthouse_critique_parse` |
| Pattern refs | MCP `drafthouse_references_search` |
| Vision rubric/parse | MCP `drafthouse_vision_rubric` / `drafthouse_vision_parse` |

## Out of scope

- Rewriting Hermes core tools
- Figma pixel-perfect replication (best-effort on-brand only)
- Shipping public links (local/private by default)
- Cloning gallery layouts without token re-skin
