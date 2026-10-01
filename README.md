# Drafthouse

v1.0.0. An open-source Claude Design-style verify harness for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

Hermes already has the agent core. Drafthouse ships the check-and-correct loop around it:

```
refs → bind tokens → generate → P0 checklist → 5-dim → lint → vision → human
```

## Quick start

```bash
export PYTHONPATH="$PWD/src" DRAFTHOUSE_ROOT="$PWD"
python3 -m drafthouse.doctor
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default
python3 scripts/eval_plate.py
```

The Docker lab leaves your live `~/.hermes` untouched:

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

For a live install, run `python3 -m drafthouse.install_hermes --dry-run` first and read what it plans to write.

## What's in the box

| Area | Contents |
|------|----------|
| Skills | verify, systems, references, vision |
| Gates | lint P0, tokens, 5-dim, vision (max 3 rounds) |
| MCP | 11 stdio tools (lint, bind, refs, vision, doctor) |
| Systems | default, editorial-field, saas-minimal, developer-docs, dark-product |
| Refs | 57 galleries + 10 playbooks |
| Evals | golden plates + honesty stub |
| Ops | doctor, sandbox installer, Docker CI |

## Docs

- [CHANGELOG](CHANGELOG.md), [CONTRIBUTING](CONTRIBUTING.md), [Security](docs/security.md), [Onboarding](docs/onboarding.md)
- Performance targets: `scripts/bench.py` (run with `PYTHONPATH=src python3 scripts/bench.py`)
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT
