from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["DRAFTHOUSE_ROOT"] = str(ROOT)
os.environ["PYTHONPATH"] = str(ROOT / "src")

from drafthouse.doctor import run_doctor  # noqa: E402
from drafthouse.install_hermes import merge_hermes_config, render_yaml_snippet  # noqa: E402


class InstallerIdempotencyTests(unittest.TestCase):
    def test_merge_twice_single_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = home / "config.yaml"
            config.write_text("model: default\n", encoding="utf-8")
            product = ROOT
            first = merge_hermes_config(config, sys.executable, product, dry_run=False)
            self.assertIn("appended", first.lower())
            text1 = config.read_text(encoding="utf-8")
            self.assertEqual(text1.count("drafthouse.mcp_server"), 1)
            second = merge_hermes_config(config, sys.executable, product, dry_run=False)
            self.assertIn("skip", second.lower())
            text2 = config.read_text(encoding="utf-8")
            self.assertEqual(text2.count("drafthouse.mcp_server"), 1)
            self.assertEqual(text2.count("DRAFTHOUSE_ROOT"), 1)

    def test_create_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            note = merge_hermes_config(config, sys.executable, ROOT, dry_run=False)
            self.assertTrue(config.exists())
            self.assertIn("drafthouse", config.read_text(encoding="utf-8"))
            self.assertIn("create", note.lower())

    def test_insert_under_existing_mcp_servers_map(self) -> None:
        # A config that already has an mcp_servers map must have drafthouse
        # inserted into it, not a second top-level mcp_servers: key.
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            config.write_text(
                "model: default\n"
                "mcp_servers:\n"
                "  aws-mcp:\n"
                "    command: /usr/bin/uvx\n"
                "  cloudflare-docs:\n"
                "    url: https://example/mcp\n"
                "platform_toolsets:\n"
                "  cli:\n"
                "    - hermes-cli\n",
                encoding="utf-8",
            )
            note = merge_hermes_config(config, sys.executable, ROOT, dry_run=False)
            self.assertIn("insert", note.lower())
            text = config.read_text(encoding="utf-8")
            self.assertEqual(len(re.findall(r"^mcp_servers:", text, re.M)), 1)
            mcp_body = text.split("mcp_servers:", 1)[1].split("\nplatform_toolsets:")[0]
            self.assertIn("\n  drafthouse:", mcp_body)
            self.assertIn("aws-mcp", text)
            self.assertIn("platform_toolsets", text)
            self.assertEqual(text.count("drafthouse.mcp_server"), 1)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            note = merge_hermes_config(config, sys.executable, ROOT, dry_run=True)
            self.assertFalse(config.exists())
            self.assertIn("would", note.lower())

    def test_yaml_snippet_contains_pythonpath(self) -> None:
        snippet = render_yaml_snippet(sys.executable, ROOT)
        self.assertIn("PYTHONPATH", snippet)
        self.assertIn("drafthouse.mcp_server", snippet)
        self.assertIn("vision_gate", snippet)


class DoctorTests(unittest.TestCase):
    def test_doctor_runs_and_reports_layout(self) -> None:
        os.environ["HERMES_HOME"] = str(ROOT / ".hermes-ci-sandbox-doctor")
        report = run_doctor()
        ids = {c.id for c in report.checks}
        self.assertIn("python", ids)
        self.assertIn("layout", ids)
        self.assertIn("import", ids)
        self.assertIn("references", ids)
        self.assertFalse(any(c.id == "layout" and c.status == "fail" for c in report.checks))
        text = report.to_text()
        self.assertIn("drafthouse doctor", text)


if __name__ == "__main__":
    unittest.main()
