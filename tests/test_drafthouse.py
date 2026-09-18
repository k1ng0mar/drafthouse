from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drafthouse.critique import format_score_block, parse_critique  # noqa: E402
from drafthouse.lint import lint_text  # noqa: E402
from drafthouse.tokens import DesignSystem, check_artifact_tokens  # noqa: E402


class LintTests(unittest.TestCase):
    def test_flags_purple_gradient(self) -> None:
        html = "<div style=\"background:linear-gradient(90deg,#7c3aed,#a855f7)\">Hi</div>"
        result = lint_text(html, path="mem")
        self.assertFalse(result.pass_gate)
        self.assertTrue(any(i.rule_id == "purple-gradient" for i in result.p0))

    def test_flags_invented_metric(self) -> None:
        result = lint_text("<p>Ship 10× faster with 99.9% uptime</p>")
        self.assertFalse(result.pass_gate)

    def test_flags_emoji_icons(self) -> None:
        result = lint_text("<h2>Features ✨🚀</h2>")
        self.assertTrue(any(i.rule_id == "emoji-feature-icons" for i in result.p0))

    def test_clean_plate_passes(self) -> None:
        html = (
            "<!doctype html><html><head><title>Hermes verify notes</title>"
            "<style>body{font-family:Georgia,serif;color:#1e241d;background:#ecebe2}"
            "h1{font-family:Georgia,serif}</style></head>"
            "<body><h1>Verify loop</h1><p>Gate summary for plate 02.</p></body></html>"
        )
        result = lint_text(html)
        self.assertEqual(result.p0, [], msg=result.to_markdown())
        self.assertTrue(result.pass_gate)


class CritiqueTests(unittest.TestCase):
    def test_parse_block(self) -> None:
        block = format_score_block(
            {"philosophy": 4, "hierarchy": 3, "execution": 4, "specificity": 5, "restraint": 3},
            ["none"],
        )
        parsed = parse_critique(block)
        self.assertTrue(parsed.passes_preemit)
        self.assertEqual(parsed.min_score, 3)

    def test_fail_when_dim_low(self) -> None:
        block = format_score_block({"philosophy": 2, "hierarchy": 4, "execution": 4, "specificity": 4, "restraint": 4})
        parsed = parse_critique(block)
        self.assertFalse(parsed.passes_preemit)

    def test_must_fix_blocks_deep_ship(self) -> None:
        block = format_score_block(
            {"philosophy": 5, "hierarchy": 5, "detail": 5, "functionality": 5, "innovation": 5},
            ["contrast fails on hero"],
        )
        parsed = parse_critique(block)
        self.assertFalse(parsed.passes_deep_ship)


class TokenTests(unittest.TestCase):
    def test_default_system_and_off_palette(self) -> None:
        system = DesignSystem.load(ROOT / "design-systems" / "default")
        self.assertIn("--dt-rust", system.tokens)
        good = "<style>:root{color:var(--dt-ink)}</style><p style=\"color:#e65b35\">ok</p>"
        self.assertEqual(check_artifact_tokens(good, system), [])
        bad = "<style>h1{color:#6366f1}</style>"
        issues = check_artifact_tokens(bad, system)
        self.assertTrue(any(i.kind == "off-palette-hex" for i in issues))


class McpSmokeTests(unittest.TestCase):
    def test_initialize_and_lint_tool(self) -> None:
        script = ROOT / "src" / "drafthouse" / "mcp_server.py"
        env = {"DRAFTHOUSE_ROOT": str(ROOT), "PYTHONPATH": str(ROOT / "src")}
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "drafthouse_lint",
                    "arguments": {"text": "<p>10× faster unlock your potential</p>"},
                },
            },
        ]
        stdin = "\n".join(json.dumps(m) for m in messages) + "\n"
        proc = subprocess.run(
            [sys.executable, str(script)],
            input=stdin,
            text=True,
            capture_output=True,
            env={**env, **dict(**{k: v for k, v in __import__("os").environ.items()})},
            check=False,
        )
        lines = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 2)
        self.assertEqual(lines[0]["result"]["serverInfo"]["name"], "drafthouse")
        lint_payload = json.loads(lines[1]["result"]["content"][0]["text"])
        self.assertFalse(lint_payload["pass"])


if __name__ == "__main__":
    unittest.main()
