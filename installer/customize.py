from __future__ import annotations

import json
import os
from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import chown_path, copy_path, ensure_directory_for_user, read_json, run_command, write_text

try:
    import pwd
except ImportError:  # pragma: no cover - only relevant off Linux
    pwd = None


PANEL_SLOTS = [
    ("Firefox", ["firefox.desktop"]),
    ("Brave", ["brave-browser.desktop"]),
    ("Chrome", ["google-chrome.desktop"]),
    ("Tor Browser", ["torbrowser.desktop"]),
    ("Calculator", ["org.gnome.Calculator.desktop", "libreoffice-calc.desktop"]),
    ("Obsidian", ["obsidian.desktop"]),
    ("KeePassXC", ["org.keepassxc.KeePassXC.desktop", "keepassxc.desktop"]),
    ("VS Code", ["code.desktop"]),
    ("VLC", ["vlc.desktop"]),
    ("Notes", ["xed.desktop", "org.x.editor.desktop"]),
]
PANEL_APPLET_ID = 100
PANEL_APPLET_ENTRY = f"panel1:left:2:panel-launchers@cinnamon.org:{PANEL_APPLET_ID}"


def _user_env(ctx: InstallerContext) -> dict[str, str]:
    user_id = os.getuid() if hasattr(os, "getuid") else 0
    if pwd is not None:
        user_id = pwd.getpwnam(ctx.real_user).pw_uid
    return {
        "HOME": str(ctx.user_home),
        "USER": ctx.real_user,
        "LOGNAME": ctx.real_user,
        "DISPLAY": os.environ.get("DISPLAY", ":0"),
        "XDG_RUNTIME_DIR": f"/run/user/{user_id}",
    }


def _append_banner(ctx: InstallerContext) -> None:
    bashrc = ctx.user_home / ".bashrc"
    marker = "Beans Terminal Banner"
    banner = '\n# Beans Terminal Banner\nprintf "\\nWith great power comes great responsibility.\\n\\n"\n'
    if ctx.dry_run:
        record_note(ctx, "Dry run: would append the Beans terminal banner to .bashrc.")
        return
    content = bashrc.read_text(encoding="utf-8") if bashrc.exists() else ""
    if marker in content:
        return
    bashrc.write_text(content + banner, encoding="utf-8")
    run_command(ctx, ["chown", f"{ctx.real_user}:{ctx.real_user}", str(bashrc)])


def _apply_wallpaper(ctx: InstallerContext) -> None:
    wallpaper_src = ctx.assets_dir / "desktop" / "beans-wallpaper.jpg"
    if not wallpaper_src.exists():
        record_note(ctx, "No Beans wallpaper asset was present, so wallpaper customization was skipped.")
        return
    wallpaper_dst = Path("/usr/share/backgrounds/beans-wallpaper.jpg")
    if ctx.dry_run:
        record_note(ctx, "Dry run: would install the Beans wallpaper and set the Cinnamon background.")
        return
    copy_path(wallpaper_src, wallpaper_dst)
    run_command(ctx, ["chmod", "644", str(wallpaper_dst)])
    env = _user_env(ctx)
    run_command(
        ctx,
        ["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", f"file://{wallpaper_dst}"],
        user=ctx.real_user,
        env=env,
        check=False,
    )
    run_command(
        ctx,
        ["gsettings", "set", "org.cinnamon.desktop.background", "picture-options", "zoom"],
        user=ctx.real_user,
        env=env,
        check=False,
    )


def _favorite_apps() -> tuple[list[str], list[str]]:
    launchers: list[str] = []
    missing: list[str] = []
    applications_dir = Path("/usr/share/applications")
    for label, candidates in PANEL_SLOTS:
        selected = next((candidate for candidate in candidates if (applications_dir / candidate).exists()), None)
        if selected:
            launchers.append(selected)
        else:
            missing.append(label)
    return launchers, missing


def _configure_panel_launchers(ctx: InstallerContext) -> None:
    launchers, missing = _favorite_apps()
    if not launchers:
        record_note(ctx, "No requested Cinnamon launcher desktop files were found for panel pinning.")
        return
    if ctx.dry_run:
        record_note(ctx, "Dry run: would pin the tightened Cinnamon launcher set to the panel.")
        return

    config_dir = ctx.user_home / ".cinnamon" / "configs" / "panel-launchers@cinnamon.org"
    ensure_directory_for_user(ctx, config_dir)
    config_path = config_dir / f"{PANEL_APPLET_ID}.json"
    config_payload = read_json(config_path, default={})
    config_payload["launcherList"] = {
        "type": "list",
        "default": [],
        "value": launchers,
    }
    write_text(config_path, json.dumps(config_payload, indent=2, sort_keys=True) + "\n")
    chown_path(ctx, config_path)

    env = _user_env(ctx)
    enabled = run_command(
        ctx,
        ["gsettings", "get", "org.cinnamon", "enabled-applets"],
        user=ctx.real_user,
        env=env,
        check=False,
        capture_output=True,
    )
    if enabled.returncode == 0:
        current = enabled.stdout.strip()
        if PANEL_APPLET_ENTRY not in current:
            if current.startswith("[") and current.endswith("]"):
                inner = current[1:-1].strip()
                updated = f"[{inner}, '{PANEL_APPLET_ENTRY}']" if inner else f"['{PANEL_APPLET_ENTRY}']"
                run_command(
                    ctx,
                    ["gsettings", "set", "org.cinnamon", "enabled-applets", updated],
                    user=ctx.real_user,
                    env=env,
                    check=False,
                )
    if missing:
        record_note(ctx, f"Some requested panel launchers were not found and were skipped: {', '.join(missing)}.")
    record_note(ctx, "Pinned Cinnamon panel launchers were configured. A logout or Cinnamon restart may be required.")


def _apply_dark_mode(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would switch Cinnamon to Mint-Y-Dark.")
        return
    env = _user_env(ctx)
    for command in (
        ["gsettings", "set", "org.cinnamon.desktop.interface", "gtk-theme", "Mint-Y-Dark"],
        ["gsettings", "set", "org.cinnamon.desktop.interface", "icon-theme", "Mint-Y"],
        ["gsettings", "set", "org.cinnamon.theme", "name", "Mint-Y-Dark"],
        ["gsettings", "set", "org.cinnamon.desktop.wm.preferences", "theme", "Mint-Y-Dark"],
    ):
        run_command(ctx, command, user=ctx.real_user, env=env, check=False)


def apply_desktop_customizations(ctx: InstallerContext) -> None:
    _append_banner(ctx)
    _apply_wallpaper(ctx)
    _apply_dark_mode(ctx)
    _configure_panel_launchers(ctx)
    record_note(ctx, "Desktop customizations applied: banner, wallpaper, dark mode, and Cinnamon panel launchers.")
