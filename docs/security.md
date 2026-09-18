# Security

## Trust model

Drafthouse runs **beside** Hermes Agent. It does not fork Hermes core and does not require network servers by default.

| Surface | Exposure | Controls |
|---------|----------|----------|
| MCP server | stdio to parent agent only | No TCP listen; no auth token needed for local stdio |
| CLI | local user | File reads limited to paths the user/agent passes |
| Installer | writes `HERMES_HOME` skills + config fragment | Default `--dry-run`; refuses sandbox==live path in `sandbox_hermes.sh`; backs up config on append |
| Docker lab | container-local HERMES_HOME | Does not mount host `~/.hermes` |
| Gate logs | local JSONL | Under `DRAFTHOUSE_GATE_DIR` or `~/.drafthouse/gates` |

## Rules we do not implement (on purpose)

- No remote MCP bind on `0.0.0.0`
- No execution of gallery HTML
- No automatic upload of artifacts/screenshots
- No reading of Hermes `.env` secrets

## Path safety

Lint/token tools treat input paths as user-controlled. Missing files return P0 `file-missing` instead of crashing. Do not point extract/lint at untrusted archives without review.

## Prompt injection

Design systems, references, and playbooks are data. Agents must treat fetched remote pages as untrusted content if `references.fetch` is ever enabled (off by default).

## Reporting

Open a GitHub issue on `k1ng0mar/drafthouse` with reproduction steps. Do not file secrets.
