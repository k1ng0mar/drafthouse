---
name: hermes-design-systems
description: Bind portable DESIGN.md + tokens.css packages into Hermes design work
version: 0.1.0
author: Drafthouse
license: MIT
metadata:
  hermes:
    pairs_with: [hermes-design-verify, design-md, claude-design]
---

# Design systems (Drafthouse packages)

Portable brand packages the agent must bind **before** generating visuals.

## Package layout

```
design-systems/<name>/
  DESIGN.md       # brand contract
  tokens.css      # :root custom properties
  manifest.json   # optional { "name": "...", "version": "..." }
```

Installed copies live at:

- Product repo: `products/drafthouse/design-systems/`
- Hermes home (after installer): `~/.hermes/design-systems/drafthouse/`

## How to bind

1. Prefer project-local `design-systems/<name>/` if present.
2. Else `~/.hermes/design-systems/drafthouse/<name>/`.
3. Else product default package.

MCP: `drafthouse_bind` with `system` id or path.
CLI: `drafthouse bind --system default`

Put the bind block into the artifact’s `:root` (or equivalent) and follow DESIGN.md rules.

## Authoring

Use `creative/design-md` for Google-style token authoring/validation.
Export/copy into a Drafthouse package folder, then run:

```bash
drafthouse tokens check some.html --system design-systems/<name>
```

## Admin lock

Pin one system for a profile via Hermes config:

```yaml
drafthouse:
  design_system: drafthouse   # package name
```

Do not silently invent a second source of truth.
