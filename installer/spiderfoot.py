from __future__ import annotations

from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import ensure_directory, run_command, write_text


def install_spiderfoot(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install SpiderFoot.")
        return
    root = Path("/opt/beans/spiderfoot")
    app_dir = root / "app"
    venv_dir = root / "venv"
    if not app_dir.exists():
        ensure_directory(root)
        run_command(ctx, ["git", "clone", "--depth", "1", "https://github.com/smicallef/spiderfoot.git", str(app_dir)])
    if not venv_dir.exists():
        run_command(ctx, ["python3", "-m", "venv", str(venv_dir)])
    run_command(ctx, [str(venv_dir / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    requirements = app_dir / "requirements.txt"
    if requirements.exists():
        run_command(ctx, [str(venv_dir / "bin" / "python"), "-m", "pip", "install", "-r", str(requirements)])
    write_text(
        Path("/usr/local/bin/spiderfoot"),
        "#!/bin/sh\nexec /opt/beans/spiderfoot/venv/bin/python /opt/beans/spiderfoot/app/sf.py -l 127.0.0.1:5001 \"$@\"\n",
        mode=0o755,
    )
    write_text(
        Path("/usr/share/applications/spiderfoot.desktop"),
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                "Name=SpiderFoot",
                "Exec=spiderfoot",
                "Icon=utilities-terminal",
                "Terminal=true",
                "Categories=Network;Security;",
                "",
            ]
        ),
    )
    run_command(ctx, ["update-desktop-database", "/usr/share/applications"], check=False)
    record_note(ctx, "SpiderFoot installed in /opt/beans/spiderfoot and exposed via a launcher.")
