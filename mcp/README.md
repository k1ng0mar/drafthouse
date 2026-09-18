# Example MCP / verify notes for Hermes (do not commit secrets)
# Copy relevant keys into ~/.hermes/config.yaml via:
#   python3 -m drafthouse.install_hermes

drafthouse:
  design_system: default
  verify:
    enabled: true
    preemit_5dim: true
    lint_on_write: true
    max_correct_rounds: 3
    ship_requires_p0_clear: true
    vision_gate: false
    jury: false
