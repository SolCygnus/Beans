from __future__ import annotations

from pathlib import Path

from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import copy_path, run_command, write_text


def _configure_ufw(ctx: InstallerContext) -> None:
    run_command(ctx, ["ufw", "default", "deny", "incoming"])
    run_command(ctx, ["ufw", "default", "deny", "outgoing"])
    run_command(ctx, ["ufw", "allow", "in", "on", "lo"])
    run_command(ctx, ["ufw", "allow", "out", "on", "lo"])
    for rule in ["53/tcp", "53/udp", "80/tcp", "443/tcp", "443/udp", "123/udp"]:
        run_command(ctx, ["ufw", "allow", "out", rule], check=False)
    run_command(ctx, ["ufw", "logging", "on"])
    run_command(ctx, ["ufw", "--force", "enable"])


def _install_clamav_scan(ctx: InstallerContext) -> None:
    scan_script = Path("/usr/local/bin/beans-clamav-scan")
    write_text(
        scan_script,
        "\n".join(
            [
                "#!/bin/sh",
                "mkdir -p /var/log/beans",
                "/usr/bin/clamscan -ri /tmp /var/tmp /dev/shm /home /media /run/user \\",
                "  --exclude-dir='^/home/[^/]+/.cache' \\",
                "  --exclude-dir='^/home/[^/]+/.local/share/Trash' \\",
                "  --log=/var/log/beans/clamav-scan.log",
                "",
            ]
        ),
        mode=0o755,
    )
    service_src = ctx.assets_dir / "systemd" / "beans-clamav-scan.service"
    timer_src = ctx.assets_dir / "systemd" / "beans-clamav-scan.timer"
    service_dst = Path("/etc/systemd/system/beans-clamav-scan.service")
    timer_dst = Path("/etc/systemd/system/beans-clamav-scan.timer")
    if service_src.exists():
        copy_path(service_src, service_dst)
    else:
        write_text(
            service_dst,
            "[Unit]\nDescription=Beans weekly ClamAV scan\nAfter=network-online.target\n\n[Service]\nType=oneshot\nExecStart=/usr/local/bin/beans-clamav-scan\n",
        )
    if timer_src.exists():
        copy_path(timer_src, timer_dst)
    else:
        write_text(
            timer_dst,
            "[Unit]\nDescription=Run the Beans ClamAV scan weekly\n\n[Timer]\nOnCalendar=Sun *-*-* 03:00:00\nPersistent=true\nUnit=beans-clamav-scan.service\n\n[Install]\nWantedBy=timers.target\n",
        )
    run_command(ctx, ["systemctl", "daemon-reload"])
    run_command(ctx, ["systemctl", "enable", "--now", "beans-clamav-scan.timer"])


def configure_security_baseline(ctx: InstallerContext) -> None:
    if ctx.dry_run:
        record_note(ctx, "Dry run: would configure UFW and install the Beans ClamAV timer.")
        return
    _configure_ufw(ctx)
    _install_clamav_scan(ctx)
    record_note(ctx, "Security baseline applied: UFW enabled and weekly ClamAV scans configured.")
