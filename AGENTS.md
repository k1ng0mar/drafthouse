# Drafthouse development

## Invariants

1. **Never fork Hermes core.** Capability climbs the Footprint Ladder: skill → MCP → plugin → core tool last.
2. **Prompt-cache safety.** Do not inject design-system text mid-turn via core mutations; bind via skill body / CWD context files / MCP tool reads.
3. **Gates before polish.** Ship lint + 5-dim pre-emit before jury/vision extras.
4. **Honest placeholders.** Never invent metrics; lint P0 blocks fake stats.

## Layout

| Path | Role |
|------|------|
| `src/drafthouse/` | lint, tokens, critique, MCP, installer |
| `skills/` | copy targets for `~/.hermes/skills/` |
| `design-systems/` | `DESIGN.md` + `tokens.css` packages |
| `hooks/` | shell-hook exit-2 ship guards |
| `docs/` (parent monorepo) | SPECS + research, not runtime |

## Commands

```bash
python3 -m pip install -e .
drafthouse lint <file.html>
drafthouse tokens check <css-or-html> --system design-systems/default
python3 -m drafthouse.install_hermes --dry-run
python3 -m drafthouse.mcp_server   # stdio MCP
```

## Adding a lint rule

1. Add a regex/heuristic in `src/drafthouse/lint.py` with `severity` P0/P1/P2.
2. Mirror the rule in `skills/hermes-design-verify/references/lint-rules.md`.
3. Add a fixture under `tests/fixtures/` and a unit test.
4. Keep rules **deterministic** — no model calls in L3.
