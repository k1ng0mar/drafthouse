#!/usr/bin/env bash
# Isolated Hermes home for Drafthouse work — NEVER the live ~/.hermes
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="${DRAFTHOUSE_SANDBOX:-$ROOT/.hermes-sandbox}"
LIVE="${HOME}/.hermes"

usage() {
  cat <<EOF
Usage: $0 <command>

Commands:
  init        Create sandbox HERMES_HOME + install drafthouse skills/MCP (safe)
  doctor      Run drafthouse doctor against the sandbox
  env         Print exports to use the sandbox
  shell       Open a shell with sandbox env
  reset       Wipe sandbox (not live Hermes)
  path        Print sandbox path
  ensure-live Untouched live path (for reference)

Live Hermes ($LIVE) is never modified by init/doctor/reset.
EOF
}

guard() {
  if [[ "$SANDBOX" == "$LIVE" || "$SANDBOX" == "${HOME}/.hermes" ]]; then
    echo "REFUSING: sandbox path equals live Hermes home" >&2
    exit 2
  fi
}

cmd="${1:-}"
case "$cmd" in
  init)
    guard
    mkdir -p "$SANDBOX"
    export HERMES_HOME="$SANDBOX"
    export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
    export DRAFTHOUSE_ROOT="$ROOT"
    echo "Installing Drafthouse into SANDBOX: $SANDBOX"
    python3 -m drafthouse.install_hermes --hermes-home "$SANDBOX" --force
    echo
    echo "Sandbox ready. Use:"
    echo "  export HERMES_HOME=$SANDBOX"
    echo "  export PYTHONPATH=$ROOT/src"
    ;;
  doctor)
    guard
    export HERMES_HOME="$SANDBOX"
    export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
    export DRAFTHOUSE_ROOT="$ROOT"
    python3 -m drafthouse.doctor
    ;;
  env)
    guard
    echo "export HERMES_HOME=\"$SANDBOX\""
    echo "export PYTHONPATH=\"${ROOT}/src\${PYTHONPATH:+:\$PYTHONPATH}\""
    echo "export DRAFTHOUSE_ROOT=\"$ROOT\""
    echo "export PATH=\"${ROOT}/bin:\$PATH\""
    ;;
  shell)
    guard
    export HERMES_HOME="$SANDBOX"
    export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
    export DRAFTHOUSE_ROOT="$ROOT"
    export PATH="${ROOT}/bin:$PATH"
    echo "HERMES_HOME=$HERMES_HOME"
    exec "${SHELL:-bash}"
    ;;
  reset)
    guard
    rm -rf "$SANDBOX"
    echo "Removed $SANDBOX"
    ;;
  path)
    echo "$SANDBOX"
    ;;
  ensure-live)
    echo "$LIVE"
    ;;
  *)
    usage
    exit 1
    ;;
esac
