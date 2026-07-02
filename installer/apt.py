from __future__ import annotations

from installer.catalog import APT_PACKAGES
from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import package_installed, run_command


def apt_update(ctx: InstallerContext) -> None:
    run_command(ctx, ["apt-get", "update"])


def apt_install(ctx: InstallerContext, packages: list[str]) -> None:
    pending = [package for package in packages if not package_installed(ctx, package)]
    if not pending:
        return
    run_command(ctx, ["apt-get", "install", "-y", *pending])


def install_base_system(ctx: InstallerContext) -> None:
    apt_update(ctx)
    apt_install(ctx, APT_PACKAGES)
    verify = run_command(ctx, ["zbarimg", "--help"], check=False, capture_output=True)
    if verify.returncode != 0:
        raise RuntimeError("zbar-tools verification failed: zbarimg not available")
    record_note(ctx, "Base packages installed. QR decoding is provided by zbar-tools.")
