# P0 / P1 / P2 checklist — hermes-design-verify

Read this **after writing** the artifact file. Every **P0** must pass before handoff.

## P0 — block ship

- [ ] No purple/violet/indigo gradient hero or section backgrounds
- [ ] No default AI indigo hex (`#6366f1`, `#4f46e5`, `#4338ca`) without brand justification
- [ ] No emoji used as feature icons
- [ ] No invented metrics or unsourced superlatives
- [ ] No filler copy (Feature One, lorem ipsum, Your text here)
- [ ] No designer/demo chrome in product UI (viewport pickers, “AI generated”, token inspectors)
- [ ] Active design system tokens bound when a system is required
- [ ] Artifact opens/renders as standalone HTML when claimed as HTML
- [ ] Contrast: body text readable against background (aim ≥ 4.5:1)
- [ ] Interactive elements have hover + focus-visible states if clickable
- [ ] File has a real title/headline specific to the brief

## P1 — fix before calling it polished

- [ ] Inter/Roboto/Arial not used as the **display** face
- [ ] Gradients not on every section
- [ ] No rounded-card + thick-left-border cliché stacks
- [ ] Icons not attached to every heading
- [ ] Warm beige/cream backgrounds only if brand/direction requires
- [ ] Layout holds at ~375px (no horizontal overflow)
- [ ] One accent color rule followed (at most twice per screen, unless system says otherwise)

## P2 — quick wins

- [ ] No triple `<br>` spacing hacks
- [ ] Consistent mono letter-spacing on labels
- [ ] Honest placeholders instead of invented numbers
- [ ] Prefers-reduced-motion respected if animation exists

## Gate

```
P0 == 0  →  run L2 5-dim  →  run L3 lint  →  then present
P0 > 0   →  FIX, do not present as done
```
