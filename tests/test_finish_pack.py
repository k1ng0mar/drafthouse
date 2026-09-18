from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["DRAFTHOUSE_ROOT"] = str(ROOT)
os.environ["PYTHONPATH"] = str(ROOT / "src")

from drafthouse.lint import lint_file, lint_text  # noqa: E402
from drafthouse.tokens import DesignSystem  # noqa: E402

GOLDEN = ROOT / "evals" / "golden"

INVENTED = re.compile(r"\b\d+\s*[×x]\s*faster\b|99\.9\s*%\s*uptime|world-class", re.I)


class HonestyTests(unittest.TestCase):
    def test_honesty_plate_has_no_invented_metrics(self) -> None:
        html = (GOLDEN / "honesty-stub" / "artifact.html").read_text(encoding="utf-8")
        self.assertIsNone(INVENTED.search(html))
        self.assertIn("—", html)
        self.assertTrue(lint_file(GOLDEN / "honesty-stub" / "artifact.html").pass_gate)

    def test_invented_metric_still_fails_lint(self) -> None:
        self.assertFalse(lint_text("<p>10× faster, world-class AI</p>").pass_gate)


class DesignSystemPackTests(unittest.TestCase):
    def test_five_systems_load_with_tokens(self) -> None:
        names = ["default", "editorial-field", "saas-minimal", "developer-docs", "dark-product"]
        for name in names:
            system = DesignSystem.load(ROOT / "design-systems" / name)
            self.assertTrue(system.tokens, msg=name)
            self.assertTrue(system.design_md.strip(), msg=name)


class ExtractSystemTests(unittest.TestCase):
    def test_extract_writes_draft_package(self) -> None:
        css = ".a{color:#0f766e;font-family:Georgia,serif}.b{color:#111827}"
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "sample.css"
            src.write_text(css, encoding="utf-8")
            out = Path(tmp) / "pkg"
            proc = subprocess.run(
                [sys.executable, "-m", "drafthouse.extract_system", str(src), "--out", str(out), "--name", "sample"],
                env={**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue((out / "tokens.css").exists())
            self.assertTrue((out / "DESIGN.md").exists())
            self.assertIn("#0f766e", (out / "tokens.css").read_text(encoding="utf-8"))


class PlaybookTests(unittest.TestCase):
    def test_core_playbooks_exist(self) -> None:
        pb = ROOT / "references" / "playbooks"
        required = {
            "hero.md",
            "navbar.md",
            "footer.md",
            "cta.md",
            "pricing.md",
            "404.md",
            "dashboard-shell.md",
            "bento-features.md",
            "docs-sidebar.md",
            "empty-state.md",
        }
        have = {p.name for p in pb.glob("*.md")}
        missing = required - have
        self.assertEqual(missing, set(), msg=missing)


class GoldenBatchTests(unittest.TestCase):
    def test_eval_all_plates(self) -> None:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "DRAFTHOUSE_ROOT": str(ROOT)}
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "eval_plate.py"), "--json"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
