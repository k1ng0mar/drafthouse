# Lint rule reference (L3)

Deterministic rules implemented in `src/drafthouse/lint.py`.
Keep this file in sync when adding rules.

| Rule ID | Severity | Detects |
|---------|----------|---------|
| `purple-gradient` | P0 | Purple/violet/indigo gradients |
| `ai-default-indigo` | P0 | Default AI indigo hexes |
| `emoji-feature-icons` | P0 | Emoji as UI icons |
| `invented-metric` | P0 | 10× faster, 99.9% uptime, world-class… |
| `filler-copy` | P0 | Feature One, lorem ipsum, TBD |
| `designer-chrome-leak` | P0 | Design-mode/demo chrome in UI |
| `display-ui-default-font` | P1 | Inter/Roboto/Arial/Helvetica in font-family |
| `gradient-on-every-bg` | P1 | Any linear-gradient (context check) |
| `left-border-card-cliche` | P1 | Rounded card + thick left accent |
| `icon-every-heading` | P1 | Icon/svg inside h1–h6 |
| `warm-ai-beige-bg` | P1 | Cream/beige page backgrounds |
| `orphan-br` | P2 | Stacked `<br>` |
| `file-missing` | P0 | Path does not exist |
| token checks | P0 (gate) | Off-palette hex, unknown CSS vars (via `--system`) |

## Output contract

JSON:

```json
{
  "path": "...",
  "pass": false,
  "counts": {"p0": 1, "p1": 2, "p2": 0},
  "issues": [{"rule_id": "purple-gradient", "severity": "P0", "message": "...", "line": 12}]
}
```

## Ship rule

`pass == false` when any P0 exists **or** token check fails when `--system` is set.
