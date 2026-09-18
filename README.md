# Drafthouse

**Open-source Claude Design–class harness for [Hermes Agent](https://github.com/NousResearch/hermes-agent).**

Hermes already has the agent core (tools, skills, MCP, hooks). Drafthouse does **not** fork it.
We ship the missing piece Claude Design is known for: a **hidden check-and-correct loop** so
design/code artifacts are linted, scored, and fixed *before* they look finished.

```
generate → P0 checklist → 5-dim self-check → artifact lint → (optional vision) → human
```

## Why

| Layer | Claude Design | Hermes today | Drafthouse |
|-------|---------------|--------------|------------|
| Agent loop | Anthropic | ✅ Hermes | use Hermes |
| Design process skill | closed | ✅ `skills/creative/claude-design` | extend, don’t replace |
| Brand tokens / DESIGN.md | proprietary systems | partial (`design-md`, `popular-web-designs`) | portable packages |
| **Self-check before user sees work** | ✅ product-private | ❌ taste checklist only | ✅ **always-on gates** |
| MCP design tools | artifacts + connectors | conversation bridge only | `drafthouse` stdio MCP |

## Install (Hermes)

```bash
cd products/drafthouse
# preview, then install skills + design systems + MCP config into ~/.hermes
python3 -m drafthouse.install_hermes --dry-run
python3 -m drafthouse.install_hermes

# zero-install lint (no pip)
bash bin/drafthouse lint path/to/artifact.html --system design-systems/default
```

Requires Hermes already on PATH (`~/.local/bin/hermes`). Does **not** rewrite Hermes core.
MCP is registered as `python3 -m drafthouse.mcp_server` with `PYTHONPATH=<repo>/src` (no pip needed).

## Layout

```
skills/           # verify + systems + references + vision skill packs
src/drafthouse/   # lint, tokens, critique, vision, references, MCP, installer
references/       # 50+ design gallery catalog (catalog.json + by-category/)
design-systems/   # DESIGN.md + tokens.css packages
hooks/            # Claude-Code-compatible exit-2 ship guard
scripts/          # generate_references.py
```

## Verify stack

1. **L0** Bind `DESIGN.md` / `tokens.css`
2. **L3.5** Pattern lookup — `drafthouse_references_search` (navbar, hero, pricing…)
3. **L1** P0 checklist
4. **L2** Silent 5-dim self-check (any dim &lt; 3/5 → fix)
5. **L3** Deterministic lint + token checks
6. **L4** Optional **vision gate** — screenshot → score → MUST_FIX → max 3 rounds
7. **L5** Human sees verified work (private/local by default)

## Design references (L3.5)

**57 galleries / 33 categories** — all of your core set plus adjacent craft refs
(Godly, pricing.page, Mobbin, Geist, type/color tools, …).

```bash
bash bin/drafthouse refs search navbar
bash bin/drafthouse refs category heroes
# MCP: drafthouse_references_search / _list / _get
```

Files: `references/catalog.json`, `references/by-category/*.md`  
Skill: `skills/hermes-design-references/SKILL.md`

Rule: **structure in, pixels out** — always re-skin through tokens; lint still applies.

## Vision gate (L4)

Uses Hermes `desktop_preview` + `vision_analyze` (no model calls inside Drafthouse core).

| Gate | Rule |
|------|------|
| Floor | every dim ≥ 5/10 |
| Ship | composite ≥ 8.0 AND `MUST_FIX` empty |
| Rounds | max 3 |

```bash
bash bin/drafthouse vision rubric
bash bin/drafthouse vision parse path/to/vision-output.txt
# MCP: drafthouse_vision_rubric / drafthouse_vision_parse
```

Skill: `skills/hermes-design-vision/SKILL.md`  
Set `drafthouse.verify.vision_gate: true` when you want it default-on.

## Config

```yaml
# ~/.hermes/config.yaml
drafthouse:
  design_system: default
  verify:
    enabled: true
    preemit_5dim: true
    lint_on_write: true
    max_correct_rounds: 3
    ship_requires_p0_clear: true
    vision_gate: false
  references:
    enabled: true
```

## Research

- `../docs/SPECS.md`
- `../docs/research/HERMES_CLAUDE_CODE_ALTERNATIVE.md`
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT

