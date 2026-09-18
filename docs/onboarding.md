# Onboarding (≤ 5 minutes)

Goal: gates on without touching a live Hermes install.

## 1. Get the product

```bash
git clone https://github.com/k1ng0mar/drafthouse.git
cd drafthouse
```

## 2. Doctor

```bash
export PYTHONPATH="$PWD/src"
export DRAFTHOUSE_ROOT="$PWD"
python3 -m drafthouse.doctor
```

Expect layout/import/references/design-system **OK**.

## 3. Lint a plate

```bash
bash bin/drafthouse lint tests/fixtures/slop.html --system design-systems/default
bash bin/drafthouse lint tests/fixtures/clean.html --system design-systems/default
```

Slop must FAIL; clean must PASS.

## 4. Golden evals

```bash
python3 scripts/eval_plate.py
```

## 5. Isolated Hermes skills (optional, not live)

```bash
bash scripts/sandbox_hermes.sh init
bash scripts/sandbox_hermes.sh doctor
export "$(bash scripts/sandbox_hermes.sh env | tr '\n' ' ' | sed 's/export //g')"  # or eval
```

Never run installer against `~/.hermes` unless you intend to.

## 6. Docker lab (recommended CI)

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

## 7. Hermes integration (explicit)

Only when you want skills on the agent you actually use:

```bash
python3 -m drafthouse.install_hermes --dry-run   # read the plan
python3 -m drafthouse.install_hermes             # writes HERMES_HOME
# restart Hermes / new conversation
```

## Learn more

- Finish plan: monorepo `docs/DRAFTHOUSE_FINISH_PLAN.md`
- Handbook: https://k1ng0mar.github.io/drafthouse-hermes-handbook/
- Product README: `README.md`
