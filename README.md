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
skills/           # SKILL.md packs for ~/.hermes/skills/
src/drafthouse/   # Python package: lint, tokens, critique helpers
mcp/              # stdio MCP server entry
design-systems/   # example DESIGN.md + tokens.css packages
hooks/            # shell-hook snippets (Claude-Code compatible exit 2)
```

## Verify stack

1. **L0** Bind `DESIGN.md` / `tokens.css` into the skill + project context  
2. **L1** P0 checklist (`skills/hermes-design-verify/references/checklist.md`)  
3. **L2** Silent 5-dim self-check (philosophy / hierarchy / execution / specificity / restraint) — any dim &lt; 3/5 → fix and re-score  
4. **L3** Deterministic `drafthouse lint` (anti-slop + token violations)  
5. **L4** Optional scored jury / vision gate (config)  
6. **L5** Human sees work (share stays private/local by default)

## Config

```yaml
# ~/.hermes/config.yaml
drafthouse:
  design_system: default   # or path to a package dir
  verify:
    enabled: true
    preemit_5dim: true
    lint_on_write: true
    max_correct_rounds: 3
    ship_requires_p0_clear: true
    vision_gate: false
```

## Research

Product specs and code studies live in the parent monorepo:

- `../docs/SPECS.md`
- `../docs/research/HERMES_CLAUDE_CODE_ALTERNATIVE.md`
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT
