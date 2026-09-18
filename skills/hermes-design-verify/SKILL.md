---
name: hermes-design-verify
description: Always-on design quality gate — lint, 5-dim self-check, token bind before you show work
version: 0.1.0
author: Drafthouse
license: MIT
metadata:
  hermes:
    pairs_with: [claude-design, design-md, popular-web-designs]
---

# Hermes design verify

You are about to produce or revise a **visual artifact** (HTML page, deck slide,
one-pager, email, mockup). Claude Design-grade quality means **check and correct
before the human treats it as done**.

Process taste and layout live in `creative/claude-design`. Brand systems live in
`creative/popular-web-designs` / `creative/design-md`. **This skill owns the gate.**

## Binding order

1. If `~/.hermes/design-systems/drafthouse/<name>/` or project `design-systems/` has a package, bind `tokens.css` + `DESIGN.md` first.
2. Else use `drafthouse bind --system default` via MCP tool `drafthouse_bind`.
3. Else pick a coherent direction yourself and declare it in a `:root` comment.

## Mandatory loop (do not skip)

```
Plan → Write file → L1 checklist → L2 5-dim → L3 lint → fix → re-check → THEN show human
```

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
drafthouse lint path/to/artifact.html --system default
# or MCP tool: drafthouse_lint
```

If **any P0** appears → fix and re-run. Do not hand off with failing P0.
Token off-palette colors also fail the gate when a design system is active.

### L4 — Optional vision (config `vision_gate: true`)

Only if enabled: `desktop_preview` + `vision_analyze` with the same 5 dims.
Max 3 correct rounds, then surface honestly to the human.

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

> Gate: P0=0 · 5-dim min=4 · tokens=pass · system=`default`

If they ask to see work mid-loop, label it **unverified** until L1–L3 pass.

## Commands

| Intent | Call |
|--------|------|
| Bind system | MCP `drafthouse_bind` or `drafthouse bind --system default` |
| Lint file | MCP `drafthouse_lint` / `drafthouse lint <file>` |
| Tokens | MCP `drafthouse_tokens_check` |
| Pre-emit prompt | MCP `drafthouse_selfcheck` |
| Parse scores | MCP `drafthouse_critique_parse` |

## Out of scope

- Rewriting Hermes core tools
- Figma pixel-perfect replication (best-effort on-brand only)
- Shipping public links (local/private by default)
