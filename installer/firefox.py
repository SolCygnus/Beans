from __future__ import annotations

import configparser
from html import unescape
from html.parser import HTMLParser
import re
from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import chown_path, copy_path, ensure_directory_for_user, read_json, run_command, write_json


BOOKMARK_PATTERN = re.compile(r'<A[^>]*HREF="([^"]+)"[^>]*>(.*?)</A>', re.IGNORECASE)
BOOKMARK_TITLES = {
    "bookmarks.html": None,
}
MANAGED_BOOKMARKS_ROOT = "PAI"
MANAGED_BOOKMARKS_FILE = "PAI_bookmarks_2026.html"
BOOKMARK_TOOLBAR_NAMES = {"Bookmarks Toolbar", "Bookmarks bar"}
UBLOCK_ORIGIN_EXTENSION_ID = "uBlock0@raymondhill.net"
UBLOCK_ORIGIN_INSTALL_URL = (
    "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
)
BLOCKED_PERMISSION_REQUESTS = ("Camera", "Microphone", "Location")


class _NetscapeBookmarkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tree: list[dict[str, object]] = []
        self._containers = [self.tree]
        self._dl_stack: list[bool] = []
        self._capture: str | None = None
        self._text: list[str] = []
        self._href = ""
        self._pending_folder: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "h3":
            self._capture = "folder"
            self._text = []
        elif tag == "a":
            self._capture = "bookmark"
            self._text = []
            self._href = dict(attrs).get("href") or ""
        elif tag == "dl":
            if self._pending_folder is None:
                self._dl_stack.append(False)
                return
            self._containers[-1].append(self._pending_folder)
            children = self._pending_folder["children"]
            if not isinstance(children, list):
                raise TypeError("Bookmark folder children must be a list.")
            self._containers.append(children)
            self._pending_folder = None
            self._dl_stack.append(True)

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "h3" and self._capture == "folder":
            name = "".join(self._text).strip()
            self._pending_folder = {"name": name, "children": []}
            self._capture = None
        elif tag == "a" and self._capture == "bookmark":
            name = "".join(self._text).strip() or self._href
            if self._href:
                self._containers[-1].append({"name": name, "url": self._href.strip()})
            self._capture = None
        elif tag == "dl" and self._dl_stack:
            if self._dl_stack.pop():
                self._containers.pop()


def _netscape_bookmark_tree(html_path: Path) -> list[dict[str, object]]:
    if not html_path.exists():
        return []
    parser = _NetscapeBookmarkParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    tree = parser.tree
    if len(tree) == 1 and tree[0].get("name") in BOOKMARK_TOOLBAR_NAMES:
        children = tree[0].get("children")
        if isinstance(children, list):
            return children
    return tree


def _bookmark_candidates(html_path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    if not html_path.exists():
        return entries
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    for url, title in BOOKMARK_PATTERN.findall(html):
        label = re.sub(r"<[^>]+>", "", unescape(title)).strip() or url
        entries.append((url.strip(), label))
    return entries


def _folder_children(
    entries: list[dict[str, object]], folder_name: str
) -> list[dict[str, object]] | None:
    for entry in entries:
        if entry.get("name") != folder_name:
            continue
        children = entry.get("children")
        if isinstance(children, list):
            return children
    return None


def _managed_pai_tree(html_path: Path) -> list[dict[str, object]]:
    tree = _netscape_bookmark_tree(html_path)
    direct_pai = _folder_children(tree, MANAGED_BOOKMARKS_ROOT)
    if direct_pai is not None:
        return direct_pai
    for toolbar_name in BOOKMARK_TOOLBAR_NAMES:
        toolbar_children = _folder_children(tree, toolbar_name)
        if toolbar_children is None:
            continue
        pai_children = _folder_children(toolbar_children, MANAGED_BOOKMARKS_ROOT)
        if pai_children is not None:
            return pai_children
    return []


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


def _managed_bookmarks(ctx: InstallerContext) -> list[dict[str, object]]:
    bookmarks_dir = ctx.assets_dir / "firefox" / "bookmarks"
    managed: list[dict[str, object]] = [{"toplevel_name": MANAGED_BOOKMARKS_ROOT}]

    managed.extend(_managed_pai_tree(bookmarks_dir / MANAGED_BOOKMARKS_FILE))

    return managed if len(managed) > 1 else []


def _firefox_extension_settings() -> dict[str, dict[str, str]]:
    return {
        UBLOCK_ORIGIN_EXTENSION_ID: {
            "installation_mode": "force_installed",
            "install_url": UBLOCK_ORIGIN_INSTALL_URL,
        }
    }


def _firefox_permission_settings() -> dict[str, dict[str, bool]]:
    return {
        permission: {
            "BlockNewRequests": True,
            "Locked": True,
        }
        for permission in BLOCKED_PERMISSION_REQUESTS
    }


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
    managed_bookmarks = _managed_bookmarks(ctx)
    if managed_bookmarks:
        policies["ManagedBookmarks"] = managed_bookmarks
    elif "ManagedBookmarks" in policies:
        del policies["ManagedBookmarks"]
    extension_settings = policies.get("ExtensionSettings")
    if not isinstance(extension_settings, dict):
        extension_settings = {}
        policies["ExtensionSettings"] = extension_settings
    extension_settings.update(_firefox_extension_settings())
    permissions = policies.get("Permissions")
    if not isinstance(permissions, dict):
        permissions = {}
        policies["Permissions"] = permissions
    for permission, settings in _firefox_permission_settings().items():
        existing = permissions.get(permission)
        if not isinstance(existing, dict):
            existing = {}
            permissions[permission] = existing
        existing.update(settings)
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
