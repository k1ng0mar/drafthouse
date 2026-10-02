# Drafthouse

Agents generate interfaces quickly and sloppily. The results are usually coherent and almost always generic: the same dark hero, the same three cards, the same safe choices. Nobody has time to art-direct every page by hand, so the slop ships.

Drafthouse is the check-and-correct loop that sits between the agent and the human. The agent makes the thing. Drafthouse inspects it, judges it, sends it back for fixes, verifies the fixes, and only then puts it in front of a person. What reaches you has earned its way there.

## What it believes

Slop is a systems problem. A model asked to "make a landing page" produces the most probable landing page, and no amount of prompt polish changes the odds. The fix is structural: give the agent references worth stealing from, pin it to real design tokens, check its work three different ways, and make correction mandatory instead of optional.

The loop separates powers on purpose. A judge picks between variants, but the judge cannot overrule the gates. A beautiful page that fails a blocking check does not ship. The human steers at the points where judgment matters and is spared everything else.

## How a run goes

You hand the agent a brief. It looks up real designs for the patterns it needs, binds your design system, and generates three different directions instead of one safe guess. Each one goes through the checks: a deterministic lint for known defects, token compliance against your system, a design judgment scored on five dimensions, and a visual verification against the actual render. Failures go back to the agent with notes. It tries again, up to three rounds. What survives comes to you with a gate report, and the handoff bundle carries everything an implementer needs: the artifact, the tokens, the screenshots, the report.

## What's in the box

- Four skills: verify, design systems, references, vision
- Deterministic gates: P0/P1/P2 lint, token checks, five-dimension rubric
- 104 design references across 33 categories, plus 10 playbooks
- Five built-in design systems to start from or steal structure from
- MCP server (11 tools), pre-ship hook, doctor, sandbox installer, Docker lab
- Golden plates: canonical examples the judge is calibrated against

## Quick start

```bash
export PYTHONPATH="$PWD/src" DRAFTHOUSE_ROOT="$PWD"
python3 -m drafthouse.doctor
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default
```

For a live install, run `python3 -m drafthouse.install_hermes --dry-run` first and read what it plans to write. The Docker lab leaves your live `~/.hermes` untouched:

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

## Docs

- [CHANGELOG](CHANGELOG.md), [CONTRIBUTING](CONTRIBUTING.md), [Security](docs/security.md), [Onboarding](docs/onboarding.md)
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT
