from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import subprocess
import sys

from installer import apt as apt_installer
from installer import customize
from installer import firefox
from installer import obsidian
from installer import pipx_tools
from installer import security
from installer import spiderfoot
from installer import vendor_apps
from installer import virtualbox
from installer import whisper
from installer.catalog import DEFAULT_COMPONENTS, default_component_ids
from installer.context import InstallerContext
from installer.summary import record_note, record_result, write_summary
from installer.system import ensure_directory, ensure_directory_for_user, format_process_error


def configure_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("beans")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stream_handler)
    return logger


def require_root() -> None:
    if os.name != "posix":
        raise SystemExit("Beans is intended to run on Linux.")
    if os.geteuid() != 0:
        raise SystemExit("Run Beans with sudo.")


def detect_real_user() -> tuple[str, Path]:
    sudo_user = os.environ.get("SUDO_USER")
    if not sudo_user:
        raise SystemExit("Beans must be run with sudo from a normal user account.")
    home = Path(os.path.expanduser(f"~{sudo_user}"))
    if not home.exists():
        raise SystemExit(f"Could not resolve home directory for {sudo_user}.")
    return sudo_user, home


def validate_environment(ctx: InstallerContext) -> None:
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        raise SystemExit("/etc/os-release not found.")
    data = {}
    for line in os_release.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value.strip('"')
    distro = data.get("ID", "")
    version = data.get("VERSION_ID", "")
    if distro != "linuxmint":
        raise SystemExit(f"Unsupported distro: {distro or 'unknown'}")
    if not version.startswith("22.3"):
        raise SystemExit(f"Unsupported Linux Mint version: {version or 'unknown'}")


def create_context(args: argparse.Namespace) -> InstallerContext:
    require_root()
    real_user, user_home = detect_real_user()
    repo_root = Path(__file__).resolve().parents[1]
    log_dir = Path(args.log_file).parent if args.log_file else Path("/var/log/beans")
    log_path = Path(args.log_file) if args.log_file else log_dir / "install.log"
    logger = configure_logger(log_path)
    ctx = InstallerContext(
        repo_root=repo_root,
        assets_dir=repo_root / "assets",
        profile=args.profile,
        dry_run=args.dry_run,
        refresh_targets=args.refresh_assets or [],
        real_user=real_user,
        user_home=user_home,
        logger=logger,
        log_dir=log_dir,
    )
    if not ctx.dry_run:
        ensure_directory(ctx.log_dir)
        ensure_directory_for_user(ctx, ctx.user_state_dir)
        ensure_directory_for_user(ctx, ctx.user_local_share_dir)
    return ctx


def refresh_assets(ctx: InstallerContext) -> int:
    targets = set(ctx.refresh_targets)
    if "all" in targets:
        targets = {"firefox", "obsidian", "desktop"}
    if "firefox" in targets:
        firefox.seed_firefox(ctx)
        record_result(ctx, "refresh-firefox", "ok", "Reapplied Firefox assets")
    if "obsidian" in targets:
        obsidian.seed_obsidian_assets(ctx)
        record_result(ctx, "refresh-obsidian", "ok", "Reapplied Obsidian assets")
    if "desktop" in targets:
        customize.apply_desktop_customizations(ctx)
        record_result(ctx, "refresh-desktop", "ok", "Reapplied desktop customizations")
    write_summary(ctx)
    return 0


def execute_component(ctx: InstallerContext, component_id: str) -> None:
    if component_id == "base-system":
        apt_installer.install_base_system(ctx)
    elif component_id == "research-browsers":
        vendor_apps.install_browsers(ctx)
        firefox.seed_firefox(ctx)
    elif component_id == "vscode":
        vendor_apps.install_vscode(ctx)
    elif component_id == "obsidian":
        vendor_apps.install_obsidian(ctx)
        obsidian.seed_obsidian_assets(ctx)
    elif component_id == "spiderfoot":
        spiderfoot.install_spiderfoot(ctx)
    elif component_id == "whisper":
        whisper.install_whisper(ctx)
    elif component_id == "searxng":
        record_note(ctx, "SearXNG is deferred for Beans 2.0 and is not installed by this release.")
    elif component_id == "sherlock":
        pipx_tools.install_sherlock(ctx)
    elif component_id == "shodan-cli":
        pipx_tools.install_shodan(ctx)
    elif component_id == "theharvester":
        pipx_tools.install_theharvester(ctx)
    elif component_id == "recon-ng":
        pipx_tools.install_recon_ng(ctx)
    elif component_id == "security-baseline":
        security.configure_security_baseline(ctx)
    elif component_id == "virtualbox-prep":
        virtualbox.prepare_virtualbox_user(ctx)
    elif component_id == "desktop-assets":
        vendor_apps.install_desktop_assets(ctx)
        customize.apply_desktop_customizations(ctx)
    else:
        raise ValueError(f"Unknown component: {component_id}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Beans Linux Mint OSR VM bootstrap")
    parser.add_argument("--profile", default="default")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-file")
    parser.add_argument("--refresh-assets", nargs="+", choices=["firefox", "obsidian", "desktop", "all"])
    parser.add_argument("--with", dest="with_components", action="append", default=[])
    parser.add_argument("--without", dest="without_components", action="append", default=[])
    return parser.parse_args(argv)


def resolve_components(args: argparse.Namespace) -> list[str]:
    component_ids = default_component_ids()
    for component in args.with_components:
        if component not in component_ids:
            component_ids.append(component)
    component_ids = [component for component in component_ids if component not in set(args.without_components)]
    return component_ids


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    ctx = create_context(args)
    validate_environment(ctx)
    if args.refresh_assets:
        return refresh_assets(ctx)

    components = resolve_components(args)
    record_note(ctx, f"Running components: {', '.join(components)}")
    for component in DEFAULT_COMPONENTS:
        if component.id not in components:
            continue
        try:
            execute_component(ctx, component.id)
            record_result(ctx, component.id, "ok", component.description)
        except subprocess.CalledProcessError as exc:
            message = format_process_error(exc)
            record_result(ctx, component.id, "failed", message, fatal=component.fatal)
            if component.fatal:
                break
        except Exception as exc:  # pragma: no cover - best effort logging
            ctx.logger.exception("Component %s failed", component.id)
            record_result(ctx, component.id, "failed", str(exc), fatal=component.fatal)
            if component.fatal:
                break

    summary_path = write_summary(ctx)
    print(f"Beans summary written to {summary_path}")
    return 0 if not any(result.fatal and result.status == 'failed' for result in ctx.results) else 1
