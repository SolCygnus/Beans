import logging
from pathlib import Path
import subprocess

from installer.context import InstallerContext
from installer.system import run_command


def _context(tmp_path: Path) -> InstallerContext:
    return InstallerContext(
        repo_root=tmp_path,
        assets_dir=tmp_path / "assets",
        profile="default",
        dry_run=False,
        refresh_targets=[],
        real_user="beans-user",
        user_home=tmp_path / "home",
        logger=logging.getLogger("beans-test"),
        log_dir=tmp_path / "logs",
    )


def test_user_command_preserves_requested_environment(monkeypatch, tmp_path: Path) -> None:
    captured = []

    def fake_run(command, **kwargs):
        captured.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_command(
        _context(tmp_path),
        ["python3", "-c", "print('ok')"],
        user="beans-user",
        env={"SEARXNG_SETTINGS_PATH": "/opt/beans/searxng/settings.yml"},
    )

    assert captured[0][0] == [
        "sudo",
        "-H",
        "-u",
        "beans-user",
        "env",
        "SEARXNG_SETTINGS_PATH=/opt/beans/searxng/settings.yml",
        "python3",
        "-c",
        "print('ok')",
    ]
