from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drafthouse.references import REFERENCES, search_references, write_catalog  # noqa: E402
from drafthouse.vision import format_vision_block, parse_vision, vision_prompt  # noqa: E402


class ReferenceTests(unittest.TestCase):
    def test_user_core_galleries_present(self) -> None:
        urls = {r.url.rstrip("/") for r in REFERENCES}
        required = {
            "https://navbar.gallery",
            "https://supahero.io",
            "https://404s.design",
            "https://footer.design",
            "https://cta.gallery",
            "https://unsection.com",
            "https://60fps.design",
            "https://designspells.com",
            "https://bentogrids.com",
            "https://rebrand.gallery",
            "https://gridddy.framer.website",
            "https://onepagelove.com/og",
            "https://saaspo.com",
            "https://landing.love",
            "https://styles.refero.design",
            "https://saasframe.io",
            "https://recent.design",
            "https://curated.design",
            "https://webinspoo.com",
            "https://vantaui.com",
            "https://mesh3d.gallery",
            "https://simply-buttons.vercel.app",
        }
        missing = required - urls
        self.assertEqual(missing, set(), msg=f"missing: {missing}")

    def test_search_by_query_and_category(self) -> None:
        heroes = search_references(query="hero")
        self.assertTrue(any(h["id"] == "supahero" for h in heroes))
        nav = search_references(category="navbars")
        self.assertTrue(any(n["id"] == "navbar-gallery" for n in nav))

    def test_write_catalog(self) -> None:
        path = write_catalog()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["count"], 40)
        self.assertIn("navbars", data["categories"])


class VisionTests(unittest.TestCase):
    def test_parse_ship(self) -> None:
        block = format_vision_block(
            {
                "philosophy": 8,
                "hierarchy": 8,
                "execution": 8,
                "specificity": 9,
                "restraint": 8,
                "accessibility": 8,
                "craft": 8,
            },
            must_fix=[],
            notes="clear hierarchy",
        )
        report = parse_vision(block)
        self.assertTrue(report.passes_ship)
        self.assertGreaterEqual(report.composite or 0, 8.0)

    def test_must_fix_blocks_ship(self) -> None:
        block = format_vision_block(
            {
                "philosophy": 9,
                "hierarchy": 9,
                "execution": 9,
                "specificity": 9,
                "restraint": 9,
                "accessibility": 9,
                "craft": 9,
            },
            must_fix=["CTA clipped on mobile"],
        )
        report = parse_vision(block)
        self.assertFalse(report.passes_ship)

    def test_floor_fails_low_dim(self) -> None:
        block = format_vision_block(
            {
                "philosophy": 7,
                "hierarchy": 4,
                "execution": 7,
                "specificity": 7,
                "restraint": 7,
                "accessibility": 7,
                "craft": 7,
            },
            must_fix=[],
        )
        report = parse_vision(block)
        self.assertFalse(report.passes_floor)

    def test_rubric_mentions_dimensions(self) -> None:
        text = vision_prompt("landing hero")
        for dim in ("philosophy", "hierarchy", "craft", "accessibility"):
            self.assertIn(dim, text)


class McpVisionRefTests(unittest.TestCase):
    def test_mcp_tools_include_refs_and_vision(self) -> None:
        script = ROOT / "src" / "drafthouse" / "mcp_server.py"
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "drafthouse_references_search", "arguments": {"query": "navbar"}},
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "drafthouse_vision_parse",
                    "arguments": {
                        "text": "```drafthouse-vision\nphilosophy: 8\nhierarchy: 8\nexecution: 8\nspecificity: 8\nrestraint: 8\naccessibility: 8\ncraft: 8\n```"
                    },
                },
            },
        ]
        stdin = "\n".join(json.dumps(m) for m in messages) + "\n"
        env = {
            **__import__("os").environ,
            "PYTHONPATH": str(ROOT / "src"),
            "DRAFTHOUSE_ROOT": str(ROOT),
        }
        proc = subprocess.run(
            [sys.executable, str(script)],
            input=stdin,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        lines = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 4)
        tool_names = {t["name"] for t in lines[1]["result"]["tools"]}
        self.assertIn("drafthouse_references_search", tool_names)
        self.assertIn("drafthouse_vision_parse", tool_names)
        refs = json.loads(lines[2]["result"]["content"][0]["text"])
        self.assertTrue(refs)
        vision = json.loads(lines[3]["result"]["content"][0]["text"])
        self.assertTrue(vision["passes_ship"])


class CliRefsTests(unittest.TestCase):
    def test_cli_refs_search(self) -> None:
        env = {
            **__import__("os").environ,
            "PYTHONPATH": str(ROOT / "src"),
            "DRAFTHOUSE_ROOT": str(ROOT),
        }
        proc = subprocess.run(
            [sys.executable, "-m", "drafthouse.cli", "refs", "search", "bento", "--json"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        data = json.loads(proc.stdout)
        self.assertTrue(any("bento" in json.dumps(x).lower() for x in data))


if __name__ == "__main__":
    unittest.main()
