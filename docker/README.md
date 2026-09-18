# Docker lab

Isolated Drafthouse verification — **never mounts host `~/.hermes`**.

## Build & run CI

```bash
# Prefer copying off FUSE if compose permission errors on gdrive:
rsync -a --exclude .git --exclude '.hermes-*' products/drafthouse/ /tmp/drafthouse-lab/
cd /tmp/drafthouse-lab
sudo docker compose -f docker/docker-compose.yml build
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-lab
```

Expected: `UNIT:0` … `== CI OK ==` … `LAB_OK`

## Interactive shell

```bash
sudo docker compose -f docker/docker-compose.yml run --rm drafthouse-shell
```

## Image contents

- Python 3.12 + product at `/opt/drafthouse`
- `HERMES_HOME=/opt/drafthouse/.hermes-sandbox` (container-local)
- Skills + catalog installed via `scripts/sandbox_hermes.sh init`
- CLI: `bash bin/drafthouse …`
- Benchmarks strict (`DRAFTHOUSE_BENCH_STRICT=1`)

## Host isolation (no Docker)

```bash
bash scripts/sandbox_hermes.sh init
bash scripts/sandbox_hermes.sh env
```
