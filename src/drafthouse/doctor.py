"""Doctor — environment and install health checks (smoothness)."""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Check:
    id: str
    status: str  # ok | warn | fail
    message: str
    fix: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class DoctorReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.status != "fail" for c in self.checks)

    @property
    def summary(self) -> str:
        counts = {"ok": 0, "warn": 0, "fail": 0}
        for c in self.checks:
            counts[c.status] = counts.get(c.status, 0) + 1
        return f"ok={counts['ok']} warn={counts['warn']} fail={counts['fail']}"

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "summary": self.summary,
            "checks": [c.to_dict() for c in self.checks],
        }

    def to_text(self) -> str:
        lines = [f"drafthouse doctor — {self.summary}", ""]
        for c in self.checks:
            mark = {"ok": "OK  ", "warn": "WARN", "fail": "FAIL"}[c.status]
            lines.append(f"[{mark}] {c.id}: {c.message}")
            if c.fix and c.status != "ok":
                lines.append(f"       fix: {c.fix}")
        return "\n".join(lines)


def product_root() -> Path:
    env = os.environ.get("DRAFTHOUSE_ROOT")
    if env:
        return Path(env).expanduser()
    return Path(__file__).resolve().parents[2]


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes").expanduser()


def run_doctor() -> DoctorReport:
    report = DoctorReport()
    root = product_root()

    # Python
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        report.checks.append(Check("python", "ok", f"Python {major}.{minor} ({sys.executable})"))
    else:
        report.checks.append(
            Check("python", "fail", f"Python {major}.{minor} < 3.10", "Use Python 3.10+")
        )

    # Product layout
    required = [
        root / "src" / "drafthouse" / "cli.py",
        root / "src" / "drafthouse" / "mcp_server.py",
        root / "src" / "drafthouse" / "lint.py",
        root / "src" / "drafthouse" / "vision.py",
        root / "src" / "drafthouse" / "references.py",
        root / "design-systems" / "default" / "tokens.css",
        root / "design-systems" / "default" / "DESIGN.md",
        root / "references" / "catalog.json",
        root / "bin" / "drafthouse",
        root / "bin" / "drafthouse-mcp",
    ]
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    if missing:
        report.checks.append(
            Check("layout", "fail", f"missing files: {', '.join(missing)}", "Reclone or restore product files")
        )
    else:
        report.checks.append(Check("layout", "ok", f"product tree complete under {root}"))

    # Importability
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        import drafthouse  # noqa: F401

        report.checks.append(Check("import", "ok", f"drafthouse {drafthouse.__version__} importable via {src}"))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(
            Check(
                "import",
                "fail",
                f"cannot import drafthouse: {exc}",
                "export PYTHONPATH=<product>/src or run via bin/drafthouse",
            )
        )

    # Catalog
    try:
        from drafthouse.references import load_catalog

        n = len(load_catalog())
        if n >= 20:
            report.checks.append(Check("references", "ok", f"catalog has {n} entries"))
        else:
            report.checks.append(
                Check("references", "warn", f"catalog only {n} entries", "Run scripts/generate_references.py")
            )
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("references", "fail", str(exc), "Regenerate catalog"))

    # Design system
    tokens = root / "design-systems" / "default" / "tokens.css"
    try:
        from drafthouse.tokens import DesignSystem

        system = DesignSystem.load(root / "design-systems" / "default")
        if system.tokens:
            report.checks.append(
                Check("design-system", "ok", f"'{system.name}' with {len(system.tokens)} tokens")
            )
        else:
            report.checks.append(Check("design-system", "warn", "default system has no tokens parsed"))
    except Exception as exc:  # noqa: BLE001
        report.checks.append(Check("design-system", "fail", str(exc)))

    # Hermes binary (optional — sandbox may not need live agent)
    hermes_bin = shutil.which("hermes")
    if hermes_bin:
        report.checks.append(Check("hermes-bin", "ok", f"hermes on PATH: {hermes_bin}"))
    else:
        report.checks.append(
            Check(
                "hermes-bin",
                "warn",
                "hermes CLI not on PATH",
                "Install Hermes or use Docker/sandbox image",
            )
        )

    # HERMES_HOME isolation
    home = hermes_home()
    live = Path.home() / ".hermes"
    isolated = home.resolve() != live.resolve()
    if home.exists():
        status = "ok"
        msg = f"HERMES_HOME={home} (exists)"
        if not isolated:
            msg += " — LIVE install"
            status = "warn"
        else:
            msg += " — isolated sandbox"
        report.checks.append(Check("hermes-home", status, msg))
    else:
        report.checks.append(
            Check(
                "hermes-home",
                "warn",
                f"HERMES_HOME={home} does not exist",
                "Create sandbox: scripts/sandbox_hermes.sh init",
            )
        )

    # Skills presence in target home
    skills_dir = home / "skills"
    verify = skills_dir / "hermes-design-verify" / "SKILL.md"
    if verify.exists():
        report.checks.append(Check("skills-installed", "ok", f"verify skill present in {skills_dir}"))
    else:
        report.checks.append(
            Check(
                "skills-installed",
                "warn",
                "drafthouse skills not installed in HERMES_HOME",
                "python3 -m drafthouse.install_hermes --hermes-home <sandbox>",
            )
        )

    # MCP config fragment
    config = home / "config.yaml"
    if config.exists() and "drafthouse" in config.read_text(encoding="utf-8", errors="replace"):
        report.checks.append(Check("mcp-config", "ok", "drafthouse block present in config.yaml"))
    else:
        report.checks.append(
            Check(
                "mcp-config",
                "warn",
                "no drafthouse MCP block in HERMES_HOME config",
                "python3 -m drafthouse.install_hermes (writes MCP + verify config)",
            )
        )

    # Exec bits / noexec awareness
    wrapper = root / "bin" / "drafthouse"
    if wrapper.exists():
        if os.access(wrapper, os.X_OK):
            # try execute via env shebang path issues on noexec
            try:
                proc = os.popen(f"bash {wrapper} --version 2>&1").read()
                if "drafthouse" in proc.lower() or "usage" in proc.lower() or proc:
                    report.checks.append(Check("cli-wrapper", "ok", "bin/drafthouse usable via bash"))
            except Exception as exc:  # noqa: BLE001
                report.checks.append(Check("cli-wrapper", "warn", f"wrapper issue: {exc}"))
        else:
            report.checks.append(
                Check("cli-wrapper", "warn", "bin/drafthouse not executable", "chmod +x bin/drafthouse")
            )

    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="drafthouse doctor")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run_doctor()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_text())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
