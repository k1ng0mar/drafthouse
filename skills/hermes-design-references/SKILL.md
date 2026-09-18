---
name: hermes-design-references
description: Look up real-world design galleries by pattern — navbars, heroes, CTAs, pricing, product UI
version: 0.1.0
author: Drafthouse
license: MIT
metadata:
  hermes:
    pairs_with: [hermes-design-verify, hermes-design-systems, claude-design]
---

# Design references

When generating **navbars, heroes, sections, footers, CTAs, pricing, dashboards,
landing pages, or motion**, look up pattern references **before** inventing layout.

Do **not** clone pixel-for-pixel. Use references for:
- information architecture
- density and hierarchy
- state coverage (empty, hover, mobile)
- restraint cues (what *not* to add)

Always re-skin through the active design system (`hermes-design-systems` / `drafthouse bind`).

## How to search

**MCP (preferred):**

| Tool | Purpose |
|------|---------|
| `drafthouse_references_search` | query / category / tag → sites |
| `drafthouse_references_list` | categories + sample ids |
| `drafthouse_reference_get` | one site by id |

**CLI:**

```bash
bash bin/drafthouse refs search navbar
bash bin/drafthouse refs category heroes
bash bin/drafthouse refs list
```

**On disk:**

- Machine catalog: `references/catalog.json`
- Human/agent notes: `references/by-category/*.md`
- Installed copy: `~/.hermes/design-systems/drafthouse/references/` or product repo path via MCP `DRAFTHOUSE_ROOT`

## Category map (high signal)

| Need | Category | Starter refs |
|------|----------|----------------|
| Site chrome / menus | `navbars` | navbar.gallery |
| Above-the-fold impact | `heroes` | supahero.io |
| Dead ends | `error-pages` | 404s.design |
| Bottom IA | `footers` | footer.design |
| Conversion blocks | `ctas` | cta.gallery |
| Modular content | `sections`, `bento` | unsection.com, bentogrids.com |
| Motion | `animation`, `microinteractions` | 60fps.design, designspells.com |
| SaaS marketing | `saas-sites`, `landing-pages` | saaspo.com, landing.love |
| App UI | `product-ui` | styles.refero.design, refero.design |
| Pricing | `pricing` | pricing.page |
| Buttons / controls | `buttons`, `ui-components` | simply-buttons.vercel.app, vantaui.com |
| Type / color systems | `type`, `color` | fonts.google.com, typescale.com, realtimecolors.com |
| Design systems | `design-systems` | ui.shadcn.com/examples, Vercel Geist |

## Workflow

1. Identify the **pattern** (hero, pricing table, dashboard sidebar…).
2. `drafthouse_references_search` with that word + optional `tag`.
3. Open 1–3 gallery URLs only if you can fetch them; otherwise read `best_for` notes and known craft rules.
4. Sketch structure in tokens from the active DESIGN.md.
5. Generate → `hermes-design-verify` gates (L1–L3, optional L4 vision).

## Anti-usage

- Do not paste third-party marketing copy or logos from galleries.
- Do not ship layout that fights your design system “because the gallery looked cool.”
- Skip 3D/WebGL refs unless the brief explicitly asks (`mesh3d.gallery` is opt-in).
- Prefer **specific structure** over decorative gradients/emoji called out by lint.

## License note

Galleries are inspiration indexes. Component libraries and fonts have their own licenses — check before shipping.
