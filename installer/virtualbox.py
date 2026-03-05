from __future__ import annotations

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import run_command


def prepare_virtualbox_user(ctx: InstallerContext) -> None:
    group_check = run_command(ctx, ["getent", "group", "vboxsf"], check=False, capture_output=True)
    if group_check.returncode != 0:
        raise RuntimeError("VirtualBox Guest Additions not detected: missing vboxsf group")
    run_command(ctx, ["usermod", "-aG", "vboxsf", ctx.real_user])
    record_note(ctx, "The target user was added to vboxsf. Log out or reboot before using host shares.")
