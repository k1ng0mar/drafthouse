#!/usr/bin/env bash
# Claude-Code compatible shell hook: block "ship" tools when lint P0 > 0.
# Wire in Hermes config under hooks → pre_tool_call, or copy into a plugin.
#
# stdin JSON: {hook_event_name, tool_name, tool_input, session_id, cwd, extra}
# exit 2 blocks the tool call (Hermes shell_hooks contract).

set -euo pipefail

payload="$(cat)"
tool="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_name",""))' 2>/dev/null || true)"
input="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin).get("tool_input") or {}))' 2>/dev/null || echo '{}')"

# Only gate ship-like tools
case "$tool" in
  web_extract|image_generate) exit 0 ;;
esac

# Heuristic: if tool writes/exports an html artifact path, lint it
path="$(printf '%s' "$input" | python3 -c '
import json,sys
d=json.loads(sys.stdin.read() or "{}")
for k in ("path","file","filename","output","dest","destination"):
    v=d.get(k)
    if isinstance(v,str) and v.endswith((".html",".htm",".css")):
        print(v); break
' 2>/dev/null || true)"

if [[ -z "${path}" || ! -f "${path}" ]]; then
  exit 0
fi

if command -v drafthouse >/dev/null 2>&1; then
  if ! drafthouse lint "$path" >/dev/null 2>&1; then
    echo '{"decision":"block","reason":"drafthouse lint failed (P0 present) — fix artifact before this tool"}'
    exit 2
  fi
fi

exit 0
