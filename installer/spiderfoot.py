from __future__ import annotations

from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import ensure_directory, run_command, write_text


SPIDERFOOT_ROOT = Path("/opt/beans/spiderfoot")
SPIDERFOOT_APP = SPIDERFOOT_ROOT / "app"
SPIDERFOOT_VENV = SPIDERFOOT_ROOT / "venv"
SPIDERFOOT_RELEASE = "v4.0"
SPIDERFOOT_REQUIREMENTS = SPIDERFOOT_ROOT / "requirements-beans.txt"


def _requirements_content(content: str) -> str:
    return content.replace("pyyaml>=5.4.1,<6", "pyyaml>=6,<7")


def _start_script() -> str:
    return "\n".join(
        [
            "#!/bin/sh",
            'ROOT="/opt/beans/spiderfoot"',
            'APP="$ROOT/app"',
            'PYTHON="$ROOT/venv/bin/python"',
            'STATE_DIR="$HOME/.local/state/beans"',
            'PID_FILE="$STATE_DIR/spiderfoot.pid"',
            'LOG_FILE="$STATE_DIR/spiderfoot.log"',
            'URL="http://127.0.0.1:5001"',
            'mkdir -p "$STATE_DIR"',
            'if [ ! -x "$PYTHON" ] || [ ! -f "$APP/sf.py" ]; then',
            '  echo "SpiderFoot is not installed correctly. Re-run the Beans installer."',
            "  exit 1",
            "fi",
            'if [ -f "$PID_FILE" ]; then',
            '  PID=$(cat "$PID_FILE")',
            '  if kill -0 "$PID" 2>/dev/null; then',
            '    echo "SpiderFoot is already running at $URL"',
            "    exit 0",
            "  fi",
            '  rm -f "$PID_FILE"',
            "fi",
            'cd "$APP" || exit 1',
            'nohup "$PYTHON" "$APP/sf.py" -l 127.0.0.1:5001 >>"$LOG_FILE" 2>&1 &',
            "PID=$!",
            'echo "$PID" >"$PID_FILE"',
            "ATTEMPT=0",
            'while [ "$ATTEMPT" -lt 15 ]; do',
            '  if ! kill -0 "$PID" 2>/dev/null; then',
            '    echo "SpiderFoot failed to start. Recent log output:"',
            '    tail -n 20 "$LOG_FILE" 2>/dev/null',
            '    rm -f "$PID_FILE"',
            "    exit 1",
            "  fi",
            '  if curl --silent --fail --max-time 2 "$URL" >/dev/null; then',
            '    echo "SpiderFoot is running at $URL"',
            "    if command -v xdg-open >/dev/null 2>&1; then",
            '      nohup xdg-open "$URL" >/dev/null 2>&1 &',
            "    fi",
            "    exit 0",
            "  fi",
            "  ATTEMPT=$((ATTEMPT + 1))",
            "  sleep 1",
            "done",
            'echo "SpiderFoot did not become ready. Recent log output:"',
            'tail -n 20 "$LOG_FILE" 2>/dev/null',
            'kill "$PID" 2>/dev/null || true',
            'rm -f "$PID_FILE"',
            "exit 1",
            "",
        ]
    )


def _stop_script() -> str:
    return "\n".join(
        [
            "#!/bin/sh",
            'PID_FILE="$HOME/.local/state/beans/spiderfoot.pid"',
            'if [ ! -f "$PID_FILE" ]; then',
            '  echo "SpiderFoot is not running."',
            "  exit 0",
            "fi",
            'PID=$(cat "$PID_FILE")',
            'if ! kill -0 "$PID" 2>/dev/null; then',
            '  rm -f "$PID_FILE"',
            '  echo "Removed a stale SpiderFoot process record."',
            "  exit 0",
            "fi",
            'kill "$PID"',
            "ATTEMPT=0",
            'while kill -0 "$PID" 2>/dev/null && [ "$ATTEMPT" -lt 10 ]; do',
            "  ATTEMPT=$((ATTEMPT + 1))",
            "  sleep 1",
            "done",
            'if kill -0 "$PID" 2>/dev/null; then',
            '  echo "SpiderFoot did not stop cleanly. Process ID: $PID"',
            "  exit 1",
            "fi",
            'rm -f "$PID_FILE"',
            'echo "SpiderFoot stopped."',
            "",
        ]
    )


def _status_script() -> str:
    return "\n".join(
        [
            "#!/bin/sh",
            'PID_FILE="$HOME/.local/state/beans/spiderfoot.pid"',
            'LOG_FILE="$HOME/.local/state/beans/spiderfoot.log"',
            'URL="http://127.0.0.1:5001"',
            'if [ ! -f "$PID_FILE" ]; then',
            '  echo "SpiderFoot is not running. Log: $LOG_FILE"',
            "  exit 1",
            "fi",
            'PID=$(cat "$PID_FILE")',
            'if ! kill -0 "$PID" 2>/dev/null; then',
            '  echo "SpiderFoot is not running; its process record is stale. Log: $LOG_FILE"',
            "  exit 1",
            "fi",
            'if curl --silent --fail --max-time 2 "$URL" >/dev/null; then',
            '  echo "SpiderFoot is running at $URL (PID $PID)"',
            "  exit 0",
            "fi",
            'echo "SpiderFoot process $PID is running but the web interface is not responding. Log: $LOG_FILE"',
            "exit 1",
            "",
        ]
    )


def install_spiderfoot(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install SpiderFoot and create launcher scripts.")
        return
    if not SPIDERFOOT_APP.exists():
        ensure_directory(SPIDERFOOT_ROOT)
        run_command(
            ctx,
            [
                "git",
                "clone",
                "--branch",
                SPIDERFOOT_RELEASE,
                "--depth",
                "1",
                "https://github.com/smicallef/spiderfoot.git",
                str(SPIDERFOOT_APP),
            ],
        )
    elif not (SPIDERFOOT_APP / ".git").exists():
        raise RuntimeError(f"Existing SpiderFoot application directory is not a Git checkout: {SPIDERFOOT_APP}")
    else:
        run_command(ctx, ["git", "-C", str(SPIDERFOOT_APP), "fetch", "--depth", "1", "origin", "tag", SPIDERFOOT_RELEASE])
        run_command(ctx, ["git", "-C", str(SPIDERFOOT_APP), "checkout", "--detach", "FETCH_HEAD"])
    python_path = SPIDERFOOT_VENV / "bin" / "python"
    if not python_path.exists():
        run_command(ctx, ["python3", "-m", "venv", str(SPIDERFOOT_VENV)])
    run_command(ctx, [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    requirements = SPIDERFOOT_APP / "requirements.txt"
    if requirements.exists():
        write_text(SPIDERFOOT_REQUIREMENTS, _requirements_content(requirements.read_text(encoding="utf-8")))
        run_command(ctx, [str(python_path), "-m", "pip", "install", "-r", str(SPIDERFOOT_REQUIREMENTS)])
    run_command(ctx, [str(python_path), "-m", "pip", "check"])
    run_command(ctx, [str(python_path), str(SPIDERFOOT_APP / "sf.py"), "--version"], cwd=SPIDERFOOT_APP, user=ctx.real_user)
    write_text(Path("/usr/local/bin/spiderfoot"), _start_script(), mode=0o755)
    write_text(Path("/usr/local/bin/beans-spiderfoot-start"), _start_script(), mode=0o755)
    write_text(Path("/usr/local/bin/beans-spiderfoot-stop"), _stop_script(), mode=0o755)
    write_text(Path("/usr/local/bin/beans-spiderfoot-status"), _status_script(), mode=0o755)
    write_text(
        Path("/usr/share/applications/spiderfoot.desktop"),
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                "Name=SpiderFoot",
                "Exec=beans-spiderfoot-start",
                "Icon=utilities-terminal",
                "Terminal=true",
                "Categories=Network;Security;",
                "",
            ]
        ),
    )
    run_command(ctx, ["update-desktop-database", "/usr/share/applications"], check=False)
    record_note(ctx, "SpiderFoot installed locally. Start it with beans-spiderfoot-start.")
