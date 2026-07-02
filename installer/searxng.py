from __future__ import annotations

import secrets
from pathlib import Path

from installer import apt as apt_installer
from installer.catalog import SEARXNG_APT_PACKAGES
from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import (
    chown_path,
    ensure_directory,
    package_installed,
    run_command,
    write_text,
)


SEARXNG_ROOT = Path("/opt/beans/searxng")
SEARXNG_APP = SEARXNG_ROOT / "app"
SEARXNG_VENV = SEARXNG_ROOT / "venv"
SEARXNG_SETTINGS = SEARXNG_ROOT / "settings.yml"
INSECURE_SECRET_KEYS = {"ultrasecretkey", "beans-searxng-local-only"}


def _settings_content(secret_key: str) -> str:
    return "\n".join(
        [
            "use_default_settings: true",
            "general:",
            "  debug: false",
            '  instance_name: "Beans SearXNG"',
            "search:",
            "  safe_search: 0",
            "  formats:",
            "    - html",
            "server:",
            '  bind_address: "127.0.0.1"',
            "  port: 8888",
            f'  secret_key: "{secret_key}"',
            "  limiter: false",
            "  image_proxy: true",
            "",
        ]
    )


def _settings_need_secret_rotation(content: str) -> bool:
    return any(secret_key in content for secret_key in INSECURE_SECRET_KEYS)


def _rotate_insecure_secret(content: str, replacement: str) -> str:
    for secret_key in INSECURE_SECRET_KEYS:
        content = content.replace(secret_key, replacement)
    return content


def _start_script() -> str:
    return "\n".join(
        [
            "#!/bin/sh",
            'ROOT="/opt/beans/searxng"',
            'PYTHON="$ROOT/venv/bin/python"',
            'SETTINGS="$ROOT/settings.yml"',
            'STATE_DIR="$HOME/.local/state/beans"',
            'PID_FILE="$STATE_DIR/searxng.pid"',
            'LOG_FILE="$STATE_DIR/searxng.log"',
            'URL="http://127.0.0.1:8888"',
            'mkdir -p "$STATE_DIR"',
            'if [ ! -x "$PYTHON" ] || [ ! -f "$SETTINGS" ]; then',
            '  echo "SearXNG is not installed correctly. Re-run the Beans installer."',
            "  exit 1",
            "fi",
            'if [ -f "$PID_FILE" ]; then',
            '  PID=$(cat "$PID_FILE")',
            '  if kill -0 "$PID" 2>/dev/null; then',
            '    echo "SearXNG is already running at $URL"',
            "    exit 0",
            "  fi",
            '  rm -f "$PID_FILE"',
            "fi",
            'cd "$ROOT/app" || exit 1',
            'nohup env SEARXNG_SETTINGS_PATH="$SETTINGS" "$PYTHON" -m searx.webapp >>"$LOG_FILE" 2>&1 &',
            "PID=$!",
            'echo "$PID" >"$PID_FILE"',
            "ATTEMPT=0",
            'while [ "$ATTEMPT" -lt 15 ]; do',
            '  if ! kill -0 "$PID" 2>/dev/null; then',
            '    echo "SearXNG failed to start. Recent log output:"',
            '    tail -n 20 "$LOG_FILE" 2>/dev/null',
            '    rm -f "$PID_FILE"',
            "    exit 1",
            "  fi",
            '  if curl --silent --fail --head --max-time 2 "$URL" >/dev/null; then',
            '    echo "SearXNG is running at $URL"',
            "    if command -v xdg-open >/dev/null 2>&1; then",
            '      nohup xdg-open "$URL" >/dev/null 2>&1 &',
            "    fi",
            "    exit 0",
            "  fi",
            "  ATTEMPT=$((ATTEMPT + 1))",
            "  sleep 1",
            "done",
            'echo "SearXNG did not become ready. Recent log output:"',
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
            'PID_FILE="$HOME/.local/state/beans/searxng.pid"',
            'if [ ! -f "$PID_FILE" ]; then',
            '  echo "SearXNG is not running."',
            "  exit 0",
            "fi",
            'PID=$(cat "$PID_FILE")',
            'if ! kill -0 "$PID" 2>/dev/null; then',
            '  rm -f "$PID_FILE"',
            '  echo "Removed a stale SearXNG process record."',
            "  exit 0",
            "fi",
            'kill "$PID"',
            "ATTEMPT=0",
            'while kill -0 "$PID" 2>/dev/null && [ "$ATTEMPT" -lt 10 ]; do',
            "  ATTEMPT=$((ATTEMPT + 1))",
            "  sleep 1",
            "done",
            'if kill -0 "$PID" 2>/dev/null; then',
            '  echo "SearXNG did not stop cleanly. Process ID: $PID"',
            "  exit 1",
            "fi",
            'rm -f "$PID_FILE"',
            'echo "SearXNG stopped."',
            "",
        ]
    )


def _status_script() -> str:
    return "\n".join(
        [
            "#!/bin/sh",
            'PID_FILE="$HOME/.local/state/beans/searxng.pid"',
            'LOG_FILE="$HOME/.local/state/beans/searxng.log"',
            'URL="http://127.0.0.1:8888"',
            'if [ ! -f "$PID_FILE" ]; then',
            '  echo "SearXNG is not running. Log: $LOG_FILE"',
            "  exit 1",
            "fi",
            'PID=$(cat "$PID_FILE")',
            'if ! kill -0 "$PID" 2>/dev/null; then',
            '  echo "SearXNG is not running; its process record is stale. Log: $LOG_FILE"',
            "  exit 1",
            "fi",
            'if curl --silent --fail --head --max-time 2 "$URL" >/dev/null; then',
            '  echo "SearXNG is running at $URL (PID $PID)"',
            "  exit 0",
            "fi",
            'echo "SearXNG process $PID is running but the web interface is not responding. Log: $LOG_FILE"',
            "exit 1",
            "",
        ]
    )


def _write_settings(ctx: InstallerContext) -> None:
    if SEARXNG_SETTINGS.exists():
        current = SEARXNG_SETTINGS.read_text(encoding="utf-8")
        if not _settings_need_secret_rotation(current):
            chown_path(ctx, SEARXNG_SETTINGS)
            SEARXNG_SETTINGS.chmod(0o600)
            return
        content = _rotate_insecure_secret(current, secrets.token_hex(32))
    else:
        content = _settings_content(secrets.token_hex(32))
    write_text(SEARXNG_SETTINGS, content, mode=0o600)
    chown_path(ctx, SEARXNG_SETTINGS)


def install_searxng(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install SearXNG in a virtual environment and create launcher scripts.")
        return
    missing_packages = [package for package in SEARXNG_APT_PACKAGES if not package_installed(ctx, package)]
    if missing_packages:
        apt_installer.apt_update(ctx)
        apt_installer.apt_install(ctx, missing_packages)
    if not SEARXNG_APP.exists():
        ensure_directory(SEARXNG_ROOT)
        run_command(ctx, ["git", "clone", "--depth", "1", "https://github.com/searxng/searxng.git", str(SEARXNG_APP)])
    elif not (SEARXNG_APP / ".git").exists():
        raise RuntimeError(f"Existing SearXNG application directory is not a Git checkout: {SEARXNG_APP}")
    python_path = SEARXNG_VENV / "bin" / "python"
    if not python_path.exists():
        run_command(ctx, ["python3", "-m", "venv", str(SEARXNG_VENV)])
    run_command(ctx, [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run_command(
        ctx,
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pyyaml",
            "msgspec",
            "typing-extensions",
            "pybind11",
        ],
    )
    run_command(
        ctx,
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--use-pep517",
            "--no-build-isolation",
            "--editable",
            str(SEARXNG_APP),
        ],
    )
    run_command(ctx, [str(python_path), "-m", "pip", "check"])
    _write_settings(ctx)
    run_command(
        ctx,
        [str(python_path), "-c", "import searx; import searx.webapp"],
        user=ctx.real_user,
        env={"SEARXNG_SETTINGS_PATH": str(SEARXNG_SETTINGS)},
    )
    write_text(Path("/usr/local/bin/beans-searxng-start"), _start_script(), mode=0o755)
    write_text(Path("/usr/local/bin/beans-searxng-stop"), _stop_script(), mode=0o755)
    write_text(Path("/usr/local/bin/beans-searxng-status"), _status_script(), mode=0o755)
    write_text(
        Path("/usr/share/applications/beans-searxng.desktop"),
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                "Name=Beans SearXNG",
                "Comment=Start the local privacy-respecting metasearch engine",
                "Exec=beans-searxng-start",
                "Icon=web-browser",
                "Terminal=true",
                "Categories=Network;WebBrowser;",
                "",
            ]
        ),
    )
    run_command(ctx, ["update-desktop-database", "/usr/share/applications"], check=False)
    record_note(ctx, "SearXNG installed locally. Start it with beans-searxng-start.")
