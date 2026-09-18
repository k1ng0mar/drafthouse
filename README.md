# Drafthouse

**v1.0.0** — Open-source Claude Design–class verify harness for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

Hermes already has the agent core. Drafthouse ships the **hidden check-and-correct loop**:

```
refs → bind tokens → generate → P0 checklist → 5-dim → lint → vision → human
```

## Quick start (safe)

```bash
export PYTHONPATH="$PWD/src" DRAFTHOUSE_ROOT="$PWD"
python3 -m drafthouse.doctor
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default
python3 scripts/eval_plate.py
```

Docker lab (does **not** touch live `~/.hermes`):

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

Optional live install: `python3 -m drafthouse.install_hermes --dry-run` first.

## What’s in the box

| Area | Contents |
|------|----------|
| Skills | verify · systems · references · vision |
| Gates | lint P0 · tokens · 5-dim · vision (max 3 rounds) |
| MCP | 10 stdio tools (lint/bind/refs/vision/…) |
| Systems | default · editorial-field · saas-minimal · developer-docs · dark-product |
| Refs | 57+ galleries + 10 playbooks |
| Evals | golden plates + honesty stub |
| Ops | doctor · sandbox installer · Docker CI |

## Docs

- [CHANGELOG](CHANGELOG.md) · [CONTRIBUTING](CONTRIBUTING.md) · [Security](docs/security.md) · [Onboarding](docs/onboarding.md)
- Monorepo finish plan: `../docs/DRAFTHOUSE_FINISH_PLAN.md`
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT
