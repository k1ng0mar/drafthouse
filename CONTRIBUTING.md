# Contributing

Thanks for helping Drafthouse stay sharp.

## Ground rules

1. **Do not fork Hermes core.** New capability → skill → MCP tool → plugin; core last.
2. **Fail-closed quality:** new lint rules need must-fail fixtures; goldens must pass `scripts/eval_plate.py`.
3. **Stdlib-only default path** — no hard dependency on heavy ML libs in `src/drafthouse`.
4. **Never commit secrets** or live `~/.hermes` configs.
5. **Test in Docker** when touching install/MCP: `sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab`.

## Dev loop

```bash
export PYTHONPATH="$PWD/src" DRAFTHOUSE_ROOT="$PWD"
python3 -m unittest discover -s tests
bash scripts/ci.sh
```

## Adding a lint rule

1. Implement in `src/drafthouse/lint.py` with rule id + severity
2. Document in `skills/hermes-design-verify/references/lint-rules.md`
3. Add `tests/fixtures/slop-*.html` that **must** fail
4. Keep rules deterministic (no model calls)

## Adding a reference

1. `src/drafthouse/references.py` → `REFERENCES` entry
2. `python3 scripts/generate_references.py`
3. Prefer pattern clarity over logo walls; note license risks

## Adding a design system

```
design-systems/<name>/{DESIGN.md,tokens.css,manifest.json}
```

Tokens must cover colors used in DESIGN.md. Run a golden plate or lint sample.

## Playbooks

Keep each `references/playbooks/*.md` under ~80 lines: IA ascii, do/don’t, token hooks, structure checks.

## PR checklist

- [ ] `unittest` green
- [ ] `scripts/eval_plate.py` green
- [ ] Docker lab CI green (if install/MCP/lint touched)
- [ ] CHANGELOG note for user-visible changes
- [ ] No live Hermes paths in tests (use temp/HERMES_HOME)
