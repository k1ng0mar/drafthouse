# Drafthouse lab — isolated from host Hermes
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/lab \
    HERMES_HOME=/opt/drafthouse/.hermes-sandbox \
    DRAFTHOUSE_ROOT=/opt/drafthouse \
    PYTHONPATH=/opt/drafthouse/src \
    PATH=/opt/drafthouse/bin:$PATH

WORKDIR /opt/drafthouse
COPY . /opt/drafthouse
RUN chmod +x /opt/drafthouse/bin/* /opt/drafthouse/scripts/*.sh \
    && mkdir -p /home/lab/.hermes

# Default: health + tests inside the container (never host ~/.hermes)
CMD ["bash", "-lc", "scripts/sandbox_hermes.sh init && python3 -m drafthouse.doctor && bash scripts/ci.sh"]
