from __future__ import annotations

import json
from pathlib import Path
import time
import urllib.request

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import download_to_file, package_installed, run_command, write_text


def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def _refresh_desktop_database(ctx: InstallerContext) -> None:
    run_command(ctx, ["update-desktop-database", "/usr/share/applications"], check=False)


def _install_vscode_repo(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        return
    key_path = Path("/usr/share/keyrings/microsoft.gpg")
    list_path = Path("/etc/apt/sources.list.d/vscode.list")
    if not key_path.exists():
        run_command(ctx, ["bash", "-lc", "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg"])
    if not list_path.exists():
        write_text(
            list_path,
            "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main\n",
        )


def _install_brave_repo(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        return
    key_path = Path("/usr/share/keyrings/brave-browser-archive-keyring.gpg")
    list_path = Path("/etc/apt/sources.list.d/brave-browser-release.list")
    if not key_path.exists():
        run_command(
            ctx,
            [
                "curl",
                "-fsSLo",
                str(key_path),
                "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg",
            ],
        )
    if not list_path.exists():
        write_text(
            list_path,
            "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main\n",
        )


def install_browsers(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install Brave and Google Chrome.")
        return
    _install_brave_repo(ctx)
    _install_vscode_repo(ctx)
    run_command(ctx, ["apt-get", "update"])
    if not package_installed(ctx, "brave-browser"):
        run_command(ctx, ["apt-get", "install", "-y", "brave-browser"])
    if not package_installed(ctx, "google-chrome-stable"):
        deb_path = Path("/tmp/google-chrome-stable_current_amd64.deb")
        download_to_file(ctx, "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", deb_path)
        run_command(ctx, ["apt-get", "install", "-y", str(deb_path)])
    record_note(ctx, "Firefox remains the research browser. Brave and Chrome are installed unmodified.")


def install_vscode(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install VS Code.")
        return
    _install_vscode_repo(ctx)
    run_command(ctx, ["apt-get", "update"])
    if not package_installed(ctx, "code"):
        run_command(ctx, ["apt-get", "install", "-y", "code"])
    record_note(ctx, "VS Code installed from Microsoft's official Linux repository.")


def install_obsidian(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install Obsidian.")
        return
    obsidian_dir = Path("/opt/beans/obsidian")
    appimage_path = obsidian_dir / "Obsidian.AppImage"
    if not appimage_path.exists():
        release = _fetch_json("https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest")
        asset = next(
            item
            for item in release.get("assets", [])
            if item.get("name", "").endswith("AppImage") and "arm64" not in item.get("name", "").lower()
        )
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        download_to_file(ctx, asset["browser_download_url"], appimage_path, mode=0o755)
    write_text(
        Path("/usr/local/bin/obsidian"),
        "#!/bin/sh\nexec /opt/beans/obsidian/Obsidian.AppImage \"$@\"\n",
        mode=0o755,
    )
    write_text(
        Path("/usr/share/applications/obsidian.desktop"),
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                "Name=Obsidian",
                "Exec=/usr/local/bin/obsidian",
                "Icon=obsidian",
                "Terminal=false",
                "Categories=Office;Utility;",
                "",
            ]
        ),
    )
    _refresh_desktop_database(ctx)
    record_note(ctx, "Obsidian installed as a managed AppImage.")


def install_desktop_assets(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install Beans desktop assets and hash-check wrapper.")
        return
    readme_src = ctx.assets_dir / "desktop" / "README.txt"
    readme_dst = ctx.desktop_dir / "Beans-README.txt"
    if readme_src.exists() and not ctx.dry_run:
        readme_dst.parent.mkdir(parents=True, exist_ok=True)
        readme_dst.write_text(readme_src.read_text(encoding="utf-8"), encoding="utf-8")
        run_command(ctx, ["chown", f"{ctx.real_user}:{ctx.real_user}", str(readme_dst)])

    hash_check_target = ctx.repo_root / "installer" / "hash_check.py"
    write_text(
        Path("/usr/local/bin/beans-hash-check"),
        f"#!/bin/sh\nexec python3 {hash_check_target} \"$@\"\n",
        mode=0o755,
    )
    timestamp = int(time.time())
    _refresh_desktop_database(ctx)
    record_note(ctx, f"Desktop assets refreshed at {timestamp}.")
