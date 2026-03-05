from __future__ import annotations

from installer.context import ComponentSpec


APT_PACKAGES = [
    "curl",
    "wget",
    "git",
    "ffmpeg",
    "gpg",
    "python3-pip",
    "python3-venv",
    "pipx",
    "terminator",
    "steghide",
    "libimage-exiftool-perl",
    "vlc",
    "keepassxc",
    "tor",
    "torbrowser-launcher",
    "sqlitebrowser",
    "proxychains4",
    "zbar-tools",
    "clamav",
    "clamav-daemon",
    "ufw",
    "xdg-utils",
]

DEFAULT_COMPONENTS = [
    ComponentSpec("base-system", "Install apt-native packages"),
    ComponentSpec("research-browsers", "Install and configure Firefox, Brave, and Chrome", fatal=False),
    ComponentSpec("vscode", "Install Visual Studio Code", fatal=False),
    ComponentSpec("obsidian", "Install Obsidian and seed vault content", fatal=False),
    ComponentSpec("spiderfoot", "Install SpiderFoot", fatal=False),
    ComponentSpec("whisper", "Install Whisper with GPU fallback", fatal=False),
    ComponentSpec("searxng", "Deferred for Beans 2.0", default_enabled=False, fatal=False),
    ComponentSpec("sherlock", "Install Sherlock", fatal=False),
    ComponentSpec("shodan-cli", "Install the Shodan CLI", fatal=False),
    ComponentSpec("theharvester", "Install theHarvester", fatal=False),
    ComponentSpec("recon-ng", "Install recon-ng", fatal=False),
    ComponentSpec("security-baseline", "Configure UFW and ClamAV", fatal=False),
    ComponentSpec("virtualbox-prep", "Add the target user to vboxsf", fatal=False),
    ComponentSpec("desktop-assets", "Install utilities and desktop notes", fatal=False),
]


def default_component_ids() -> list[str]:
    return [component.id for component in DEFAULT_COMPONENTS if component.default_enabled]
