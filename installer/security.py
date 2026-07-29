from __future__ import annotations

from pathlib import Path

from installer import apt as apt_installer
from installer.context import InstallerContext
from installer.summary import record_note
from installer.system import copy_path, package_installed, run_command, write_text


UFW_BEFORE_RULES = Path("/etc/ufw/before.rules")
ICMP_RULES = [
    "-A ufw-before-output -p icmp --icmp-type echo-request -j ACCEPT",
    "-A ufw-before-input -p icmp --icmp-type echo-reply -j ACCEPT",
]
BASELINE_UFW_RULES = [
    ["allow", "in", "on", "lo"],
    ["allow", "out", "on", "lo"],
    ["allow", "out", "53/udp"],
    ["allow", "out", "53/tcp"],
    ["allow", "out", "80/tcp"],
    ["allow", "out", "443/tcp"],
    ["allow", "out", "443/udp"],
    ["allow", "out", "123/udp"],
    ["allow", "out", "67/udp"],
    ["allow", "in", "68/udp"],
]


def _ensure_ufw_installed(ctx: InstallerContext) -> None:
    if package_installed(ctx, "ufw"):
        return
    apt_installer.apt_update(ctx)
    apt_installer.apt_install(ctx, ["ufw"])


def _filter_bounds(lines: list[str]) -> tuple[int, int]:
    try:
        filter_start = lines.index("*filter")
    except ValueError as exc:
        raise RuntimeError(f"Could not find the *filter section in {UFW_BEFORE_RULES}.") from exc
    for index in range(filter_start + 1, len(lines)):
        if lines[index] == "COMMIT":
            return filter_start, index
    raise RuntimeError(f"Could not find the *filter COMMIT in {UFW_BEFORE_RULES}.")


def _ensure_icmp_before_rules(ctx: InstallerContext) -> None:
    lines = UFW_BEFORE_RULES.read_text(encoding="utf-8").splitlines()
    filter_start, filter_commit = _filter_bounds(lines)
    filter_rules = lines[filter_start:filter_commit]
    missing_rules = [rule for rule in ICMP_RULES if rule not in filter_rules]
    if not missing_rules:
        return
    lines[filter_commit:filter_commit] = missing_rules
    UFW_BEFORE_RULES.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.logger.info("Added required IPv4 ICMP rules to %s.", UFW_BEFORE_RULES)


def _configure_ufw(ctx: InstallerContext) -> None:
    _ensure_ufw_installed(ctx)
    _ensure_icmp_before_rules(ctx)
    for rule in BASELINE_UFW_RULES:
        run_command(ctx, ["ufw", *rule])
    run_command(ctx, ["ufw", "default", "deny", "incoming"])
    run_command(ctx, ["ufw", "default", "deny", "outgoing"])
    run_command(ctx, ["ufw", "default", "deny", "routed"])
    run_command(ctx, ["ufw", "logging", "on"])
    status = run_command(ctx, ["ufw", "status"], capture_output=True)
    if "Status: active" in status.stdout:
        run_command(ctx, ["ufw", "reload"])
    else:
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
