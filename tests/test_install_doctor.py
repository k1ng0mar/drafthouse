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
from drafthouse.install_hermes import (  # noqa: E402
    ADMIN_BLOCK,
    mcp_add_command,
    uninstall_skills,
    write_admin_block,
)


class InstallerTests(unittest.TestCase):
    def test_admin_block_written_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            config.write_text("model: default\n", encoding="utf-8")
            first = write_admin_block(config, dry_run=False)
            self.assertIn("wrote", first)
            self.assertIn("drafthouse:", config.read_text(encoding="utf-8"))
            second = write_admin_block(config, dry_run=False)
            self.assertIn("already has", second)
            self.assertEqual(config.read_text(encoding="utf-8").count("\ndrafthouse:"), 1)

    def test_admin_block_does_not_touch_mcp_servers(self) -> None:
        # The installer must never mutate an existing mcp_servers map.
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            config.write_text(
                "model: default\n"
                "mcp_servers:\n"
                "  aws-mcp:\n"
                "    command: /usr/bin/uvx\n"
                "platform_toolsets:\n"
                "  cli:\n"
                "    - hermes-cli\n",
                encoding="utf-8",
            )
            write_admin_block(config, dry_run=False)
            text = config.read_text(encoding="utf-8")
            self.assertEqual(len(re.findall(r"^mcp_servers:", text, re.M)), 1)
            self.assertIn("aws-mcp", text)
            self.assertIn("platform_toolsets", text)
            self.assertNotIn("drafthouse.mcp_server", text)

    def test_admin_block_creates_config_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            write_admin_block(config, dry_run=False)
            self.assertTrue(config.exists())
            self.assertIn("drafthouse:", config.read_text(encoding="utf-8"))

    def test_admin_block_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            note = write_admin_block(config, dry_run=True)
            self.assertFalse(config.exists())
            self.assertIn("would", note)

    def test_mcp_add_command_points_at_shim(self) -> None:
        cmd = mcp_add_command(ROOT)
        self.assertIn(f"{ROOT / 'bin' / 'drafthouse-mcp'}", cmd)
        self.assertIn("DRAFTHOUSE_ROOT", cmd)
        self.assertIn("PYTHONPATH", cmd)

    def test_admin_block_has_expected_keys(self) -> None:
        self.assertIn("design_system: default", ADMIN_BLOCK)
        self.assertIn("vision_gate", ADMIN_BLOCK)
        self.assertIn("catalog: auto", ADMIN_BLOCK)

    def test_uninstall_removes_drafthouse_skills_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for name in (
                "drafthouse-design-verify",
                "drafthouse-design-systems",
                "other-skill",
            ):
                (home / "skills" / name).mkdir(parents=True)
            notes = uninstall_skills(home, dry_run=False)
            self.assertFalse((home / "skills" / "drafthouse-design-verify").exists())
            self.assertFalse((home / "skills" / "drafthouse-design-systems").exists())
            self.assertTrue((home / "skills" / "other-skill").exists())
            self.assertTrue(any("hermes mcp remove drafthouse" in n for n in notes))


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
