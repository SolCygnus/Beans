from __future__ import annotations

import time
from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import chown_path, copy_path, ensure_directory_for_user, read_json, write_json


VAULT_NAME = "Study Vault"


def _register_vault(config_path: Path, vault_path: Path) -> None:
    payload = read_json(config_path, default={"vaults": {}})
    vaults = payload.setdefault("vaults", {})
    entry_id = "beans-study-vault"
    vaults[entry_id] = {
        "path": str(vault_path),
        "ts": int(time.time() * 1000),
        "open": False,
    }
    write_json(config_path, payload)


def seed_obsidian_assets(ctx: InstallerContext) -> None:
    src = ctx.assets_dir / "obsidian" / "vaults" / VAULT_NAME
    dst = ctx.user_home / "Documents" / "Obsidian Vaults" / VAULT_NAME
    if not src.exists():
        record_note(ctx, "No Obsidian seed vault was present in assets.")
        return
    if not ctx.dry_run:
        ensure_directory_for_user(ctx, dst.parent)
        copy_path(src, dst)
        config_path = ctx.user_home / ".config" / "obsidian" / "obsidian.json"
        ensure_directory_for_user(ctx, config_path.parent)
        _register_vault(config_path, dst)
        chown_path(ctx, dst, recursive=True)
        chown_path(ctx, config_path)
    record_note(ctx, "Study Vault content was seeded into Obsidian.")
