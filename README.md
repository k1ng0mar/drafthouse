# Drafthouse

Agents generate interfaces quickly and sloppily. The results are usually coherent and almost always generic: the same dark hero, the same three cards, the same safe choices. Nobody has time to art-direct every page by hand, so the slop ships.

Drafthouse is the check-and-correct loop that sits between the agent and the human. The agent makes the thing. Drafthouse inspects it, judges it, sends it back for fixes, verifies the fixes, and only then puts it in front of a person. What reaches you has earned its way there.

## What it believes

Slop is a systems problem. A model asked to "make a landing page" produces the most probable landing page, and no amount of prompt polish changes the odds. The fix is structural: give the agent references worth stealing from, pin it to real design tokens, check its work three different ways, and make correction mandatory instead of optional.

The loop separates powers on purpose. A judge ranks variants, but the judge cannot overrule the gates. A beautiful page that fails a blocking check does not ship. The human steers at the points where judgment matters and is spared everything else.

## How a run goes

You hand the agent a brief. It looks up real designs for the patterns it needs, binds your design system, and generates the design. On open briefs it can generate three different directions instead of one safe guess, and the judge ranks them; when the top two land within a step of each other, it hands you the choice instead of picking for you. Each direction goes through the checks: a deterministic lint for known defects, token compliance against your system, a design judgment scored on five dimensions, and a visual verification against the actual render. Failures go back to the agent with notes. It tries again, up to three rounds. What survives comes to you with a gate report, and the judge decision log carries the winner, every score, and the reasons.

## What's in the box

- Four skills: verify, design systems, references, vision
- Deterministic gates: P0/P1/P2 lint, token checks, five-dimension rubric
- 104 design references across 33 categories, plus 10 playbooks
- Five built-in design systems to start from or steal structure from
- MCP server (12 tools), pre-ship hook, doctor, sandbox installer, Docker lab
- Golden plates: canonical examples the judge is calibrated against

## Quick start

```bash
export PYTHONPATH="$PWD/src" DRAFTHOUSE_ROOT="$PWD"
python3 -m drafthouse.doctor
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default
```

## Install into Hermes

Simplest-to-install is three lines. Clone, install the skills, register the MCP server:

```bash
git clone https://github.com/k1ng0mar/drafthouse && cd drafthouse
python3 -m drafthouse.install_hermes          # copies skills + writes the drafthouse: admin block
hermes mcp add drafthouse --command "$PWD/bin/drafthouse-mcp" --env DRAFTHOUSE_ROOT="$PWD" --env PYTHONPATH="$PWD/src"
```

The installer prints the exact `hermes mcp add` command for your paths. It does not hand-edit your `mcp_servers:` map; the MCP registration goes through the native `hermes mcp` command, and `hermes mcp remove drafthouse` is the matching uninstall. To remove the installed skills later:

```bash
python3 -m drafthouse.install_hermes --uninstall
hermes mcp remove drafthouse
```

For a fully isolated run that leaves your live `~/.hermes` untouched, the Docker lab works the same way:

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

## Docs

- [CHANGELOG](CHANGELOG.md), [CONTRIBUTING](CONTRIBUTING.md), [Security](docs/security.md), [Onboarding](docs/onboarding.md)
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/

## License

MIT
