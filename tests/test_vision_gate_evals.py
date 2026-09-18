from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["DRAFTHOUSE_ROOT"] = str(ROOT)
os.environ["PYTHONPATH"] = str(ROOT / "src")

from drafthouse.lint import lint_file  # noqa: E402
from drafthouse.vision_gate import capture_plan, run_parse  # noqa: E402

GOLDEN = ROOT / "evals" / "golden"
FIXTURES = ROOT / "tests" / "fixtures"


class FailFixtureTests(unittest.TestCase):
    def test_all_slop_fixtures_fail_p0(self) -> None:
        slop_files = sorted(FIXTURES.glob("slop*.html"))
        self.assertGreaterEqual(len(slop_files), 3)
        for path in slop_files:
            result = lint_file(path)
            self.assertFalse(result.pass_gate, msg=f"{path.name} should fail P0")


class VisionGateTests(unittest.TestCase):
    def test_plan_includes_steps_and_rubric(self) -> None:
        artifact = GOLDEN / "saas-landing" / "artifact.html"
        plan = capture_plan(artifact)
        self.assertEqual(plan["max_rounds"], 3)
        self.assertTrue(any("desktop_preview" in s for s in plan["steps"]))
        self.assertIn("philosophy", plan["rubric"].lower())

    def test_parse_logs_and_blocks_round4(self) -> None:
        artifact = GOLDEN / "404-state" / "artifact.html"
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["DRAFTHOUSE_GATE_DIR"] = tmp
            try:
                ship_block = (
                    "```drafthouse-vision\n"
                    "philosophy: 8\nhierarchy: 8\nexecution: 8\nspecificity: 8\n"
                    "restraint: 8\naccessibility: 8\ncraft: 8\nMUST_FIX: none\n```"
                )
                report, payload = run_parse(ship_block, artifact=artifact, screenshot=None, round_no=1)
                self.assertTrue(report.passes_ship)
                self.assertFalse(payload.get("blocked"))
                report2, payload2 = run_parse(ship_block, artifact=artifact, screenshot=None, round_no=4)
                self.assertTrue(payload2.get("blocked"))
                self.assertEqual(payload2.get("reason"), "max_rounds_exceeded")
            finally:
                os.environ.pop("DRAFTHOUSE_GATE_DIR", None)


class GoldenPlateTests(unittest.TestCase):
    def test_eval_golden_plates_pass(self) -> None:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)}
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "eval_plate.py"), "--json"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["failed"], 0, msg=proc.stdout)
        names = {r["plate"] for r in data["results"]}
        self.assertIn("saas-landing", names)
        self.assertIn("404-state", names)
        self.assertIn("pricing", names)

    def test_cli_vision_gate_demo(self) -> None:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)}
        proc = subprocess.run(
            [sys.executable, "-m", "drafthouse.cli", "vision", "gate", "demo"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout)
        self.assertIn("passes_ship", proc.stdout)


if __name__ == "__main__":
    unittest.main()
