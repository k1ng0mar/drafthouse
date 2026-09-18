# Changelog

## 1.0.0 — 2026-09-18

First stable Drafthouse release: Claude Design–class verify harness for Hermes Agent.

### Added
- **Verify stack:** L0 token bind · L1 P0 checklist · L2 5-dim self-check · L3 deterministic lint + tokens · L3.5 pattern references · L4 vision gate runner
- **Skills:** `hermes-design-verify`, `hermes-design-systems`, `hermes-design-references`, `hermes-design-vision`
- **MCP stdio server:** lint, tokens, bind, selfcheck, critique parse, refs search/list/get, vision rubric/parse
- **Design systems:** `default` (Drafthouse Field), `editorial-field`, `saas-minimal`, `developer-docs`, `dark-product`
- **References:** 57+ gallery catalog + 10 pattern playbooks
- **Vision gate CLI:** `drafthouse vision gate plan|parse|rounds|demo` — JSONL logs, max 3 rounds
- **Evals:** golden plates (landing, 404, pricing, honesty-stub, docs-sidebar) + `scripts/eval_plate.py`
- **Ops:** `drafthouse doctor`, installer with idempotent MCP block, HERMES_HOME sandbox, Docker lab
- **Extract MVP:** `drafthouse extract-system` (draft tokens; human review required)

### Performance (Docker lab, warm)
- Lint 50KB p95 ≤ 150ms · refs search p95 ≪ 20ms · MCP initialize p50 ≈ 100ms after warmup

### Security
- Stdio MCP only; no daemon bind by default
- Installer never writes host `~/.hermes` unless explicitly targeted
- Artifact reads are local paths; reject missing files with P0
- See `docs/security.md`

### Notes
- Hermes core is never forked — capability via skills + MCP + hooks
- Live-agent install is optional and out of band from Docker lab CI
