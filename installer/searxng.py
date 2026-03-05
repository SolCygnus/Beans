from __future__ import annotations

from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import ensure_directory, run_command, write_text


def install_searxng(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install SearXNG and create manual launcher scripts.")
        return
    root = Path("/opt/beans/searxng")
    app_dir = root / "app"
    venv_dir = root / "venv"
    if not app_dir.exists():
        ensure_directory(root)
        run_command(ctx, ["git", "clone", "--depth", "1", "https://github.com/searxng/searxng.git", str(app_dir)])
    if not venv_dir.exists():
        run_command(ctx, ["python3", "-m", "venv", str(venv_dir)])
    run_command(ctx, [str(venv_dir / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run_command(ctx, [str(venv_dir / "bin" / "python"), "-m", "pip", "install", "-e", str(app_dir)])
    write_text(
        root / "settings.yml",
        "\n".join(
            [
                "server:",
                "  bind_address: \"127.0.0.1\"",
                "  port: 8888",
                "  secret_key: \"beans-searxng-local-only\"",
                "search:",
                "  safe_search: 0",
                "",
            ]
        ),
    )
    write_text(
        Path("/usr/local/bin/beans-searxng-start"),
        "\n".join(
            [
                "#!/bin/sh",
                "STATE_DIR=\"$HOME/.local/state/beans\"",
                "mkdir -p \"$STATE_DIR\"",
                "PID_FILE=\"$STATE_DIR/searxng.pid\"",
                "LOG_FILE=\"$STATE_DIR/searxng.log\"",
                "if [ -f \"$PID_FILE\" ] && kill -0 \"$(cat \"$PID_FILE\")\" 2>/dev/null; then",
                "  echo \"SearXNG is already running.\"",
                "  exit 0",
                "fi",
                "export SEARXNG_SETTINGS_PATH=/opt/beans/searxng/settings.yml",
                "nohup /opt/beans/searxng/venv/bin/python -m searx.webapp >>\"$LOG_FILE\" 2>&1 &",
                "echo $! >\"$PID_FILE\"",
                "sleep 2",
                "command -v xdg-open >/dev/null 2>&1 && xdg-open http://127.0.0.1:8888 >/dev/null 2>&1",
                "",
            ]
        ),
        mode=0o755,
    )
    write_text(
        Path("/usr/local/bin/beans-searxng-stop"),
        "\n".join(
            [
                "#!/bin/sh",
                "PID_FILE=\"$HOME/.local/state/beans/searxng.pid\"",
                "if [ ! -f \"$PID_FILE\" ]; then",
                "  echo \"SearXNG is not running.\"",
                "  exit 0",
                "fi",
                "kill \"$(cat \"$PID_FILE\")\" 2>/dev/null || true",
                "rm -f \"$PID_FILE\"",
                "",
            ]
        ),
        mode=0o755,
    )
    record_note(ctx, "SearXNG was installed locally and is started manually with beans-searxng-start.")
