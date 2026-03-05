from __future__ import annotations

import configparser
from html import unescape
import re
from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import chown_path, copy_path, ensure_directory_for_user, read_json, run_command, write_json


BOOKMARK_PATTERN = re.compile(r'<A[^>]*HREF="([^"]+)"[^>]*>(.*?)</A>', re.IGNORECASE)
BOOKMARK_TITLES = {
    "bookmarks.html": None,
    "LINKS_2024.html": "LINKS",
    "OSINT_Combine_bookmarks_11_12_25.html": "OSINT Combine",
}


def _bookmark_candidates(html_path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    if not html_path.exists():
        return entries
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    for url, title in BOOKMARK_PATTERN.findall(html):
        label = re.sub(r"<[^>]+>", "", unescape(title)).strip() or url
        entries.append((url.strip(), label))
    return entries


def _dedupe_bookmarks(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[tuple[str, str]] = []
    for entry in entries:
        if entry in seen:
            continue
        deduped.append(entry)
        seen.add(entry)
    return deduped


def _profiles_ini_path(ctx: InstallerContext) -> Path:
    return ctx.user_home / ".mozilla" / "firefox" / "profiles.ini"


def _load_profiles(ctx: InstallerContext) -> tuple[configparser.RawConfigParser, Path]:
    profiles_ini = _profiles_ini_path(ctx)
    config = configparser.RawConfigParser()
    config.optionxform = str
    if profiles_ini.exists():
        config.read(profiles_ini)
    return config, profiles_ini


def _profile_section_path(profile_root: Path, config: configparser.RawConfigParser, section: str) -> Path | None:
    path_value = config.get(section, "Path", fallback="")
    if not path_value:
        return None
    is_relative = config.get(section, "IsRelative", fallback="1") == "1"
    return (profile_root / path_value) if is_relative else Path(path_value)


def _find_existing_profile(ctx: InstallerContext) -> tuple[str, Path] | None:
    config, _ = _load_profiles(ctx)
    profile_root = ctx.user_home / ".mozilla" / "firefox"
    for section in config.sections():
        if section.startswith("Profile") and config.get(section, "Default", fallback="0") == "1":
            path = _profile_section_path(profile_root, config, section)
            if path is not None:
                return config.get(section, "Name", fallback=path.name), path
    for section in config.sections():
        if section.startswith("Profile"):
            path = _profile_section_path(profile_root, config, section)
            if path is not None:
                return config.get(section, "Name", fallback=path.name), path
    return None


def _bootstrap_profile(ctx: InstallerContext) -> None:
    run_command(
        ctx,
        ["timeout", "20", "firefox", "--headless", "about:blank"],
        user=ctx.real_user,
        check=False,
    )


def _ensure_default_profile(ctx: InstallerContext) -> tuple[str, Path]:
    profile_root = ctx.user_home / ".mozilla" / "firefox"
    ensure_directory_for_user(ctx, profile_root)

    existing = _find_existing_profile(ctx)
    if existing is None:
        _bootstrap_profile(ctx)
        existing = _find_existing_profile(ctx)
    if existing is None:
        run_command(ctx, ["firefox", "-CreateProfile", "beans-default"], user=ctx.real_user)
        config, profiles_ini = _load_profiles(ctx)
        if not config.has_section("General"):
            config.add_section("General")
        config.set("General", "StartWithLastProfile", "1")
        for section in config.sections():
            if section.startswith("Profile") and config.get(section, "Name", fallback="") == "beans-default":
                config.set(section, "Default", "1")
                break
        if not ctx.dry_run:
            with profiles_ini.open("w", encoding="utf-8") as handle:
                config.write(handle)
            chown_path(ctx, profiles_ini)
        _bootstrap_profile(ctx)
        existing = _find_existing_profile(ctx)
    if existing is None:
        raise RuntimeError("Firefox default profile could not be created automatically.")

    name, profile_dir = existing
    ensure_directory_for_user(ctx, profile_dir)
    return name, profile_dir


def _policy_bookmarks(ctx: InstallerContext) -> list[dict[str, str]]:
    bookmarks_dir = ctx.assets_dir / "firefox" / "bookmarks"
    policies: list[dict[str, str]] = []
    for filename, folder_name in BOOKMARK_TITLES.items():
        html_path = bookmarks_dir / filename
        for url, title in _dedupe_bookmarks(_bookmark_candidates(html_path)):
            entry = {
                "Title": title,
                "URL": url,
                "Placement": "toolbar",
            }
            if folder_name:
                entry["Folder"] = folder_name
            policies.append(entry)
    return policies


def _write_firefox_policies(ctx: InstallerContext) -> None:
    policies_path = Path("/etc/firefox/policies/policies.json")
    payload = read_json(policies_path, default={})
    policies = payload.setdefault("policies", {})
    policies["DisplayBookmarksToolbar"] = True
    bookmarks = _policy_bookmarks(ctx)
    if bookmarks:
        policies["Bookmarks"] = bookmarks
    elif "Bookmarks" in policies:
        del policies["Bookmarks"]
    if "ManagedBookmarks" in policies:
        del policies["ManagedBookmarks"]
    write_json(policies_path, payload)


def seed_firefox(ctx: InstallerContext) -> None:
    profile_name, profile_dir = _ensure_default_profile(ctx)
    user_js = ctx.assets_dir / "firefox" / "user.js"
    if user_js.exists() and not ctx.dry_run:
        copy_path(user_js, profile_dir / "user.js")
        chown_path(ctx, profile_dir / "user.js")
    extensions_dir = ctx.assets_dir / "firefox" / "extensions"
    if extensions_dir.exists() and not ctx.dry_run:
        ensure_directory_for_user(ctx, profile_dir / "extensions")
        for extension in extensions_dir.iterdir():
            if extension.is_file():
                copy_path(extension, profile_dir / "extensions" / extension.name)
                chown_path(ctx, profile_dir / "extensions" / extension.name)
    if not ctx.dry_run:
        _write_firefox_policies(ctx)
        chown_path(ctx, profile_dir, recursive=True)
    record_note(ctx, f"Firefox research profile assets were applied to the default profile '{profile_name}', with toolbar bookmarks sourced from all Beans bookmark assets.")
