from __future__ import annotations

from pathlib import Path

from installer import firefox
from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import write_json


CHROME_POLICY_PATH = Path("/etc/opt/chrome/policies/managed/beans-bookmarks.json")


def _managed_bookmarks(ctx: InstallerContext) -> list[dict[str, object]]:
    nested = firefox._managed_bookmarks(ctx)
    quick_links = [
        {"name": entry["Title"], "url": entry["URL"]}
        for entry in firefox._policy_bookmarks(ctx)
    ]
    nested_items = nested[1:] if nested else []
    if not quick_links and not nested_items:
        return []
    return [
        {"toplevel_name": firefox.MANAGED_BOOKMARKS_ROOT},
        *quick_links,
        *nested_items,
    ]


def _policy_payload(ctx: InstallerContext) -> dict[str, object]:
    return {
        "BookmarkBarEnabled": True,
        "ManagedBookmarks": _managed_bookmarks(ctx),
    }


def seed_chrome(ctx: InstallerContext) -> None:
    if not ctx.dry_run:
        write_json(CHROME_POLICY_PATH, _policy_payload(ctx))
    record_note(ctx, "Chrome received the Beans-managed PAI bookmark tree and visible bookmark bar policy.")
