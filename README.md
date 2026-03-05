# Beans

Beans is a Linux Mint 22.3 Cinnamon bootstrap for Open Source Research VMs in VirtualBox. It targets a fresh guest and installs a research-ready baseline with security defaults and desktop customizations.

## Quick Start

### Requirements

- Linux Mint Cinnamon 22.3
- VirtualBox Guest Additions installed before running Beans
- Internet connectivity during install
- A normal user account with `sudo` access

### Recommended VM Sizing

- Minimum RAM: `8 GB`
- Practical middle ground: `12 GB`
- Recommended for heavier concurrent Firefox + Chrome use: `16 GB`
- Recommended CPU allocation: `4 vCPUs`
- Disk: enough space for browsers, SpiderFoot, Whisper, logs, and Obsidian vault assets

These are Beans recommendations based on the default toolset, not official Linux Mint minimums.

### Pre-Install (Recommended, Not Required)

Recommended before cloning or running Beans:

```bash
sudo apt update && sudo apt upgrade -y
reboot
```

This is recommended, not required. Beans runs `apt-get update` and installs required packages, but it does not perform a full OS upgrade.

### Install

Clone and run:

```bash
git clone <YOUR_BEANS_REPO_URL>
cd beans
sudo python3 main.py --profile default
```

### Other Commands

```bash
sudo python3 main.py --dry-run
sudo python3 main.py --refresh-assets firefox
sudo python3 main.py --refresh-assets obsidian
sudo python3 main.py --refresh-assets desktop
sudo python3 main.py --refresh-assets all
```

## Post-Install Validation Checklist

- `ufw status verbose` shows enabled with expected outbound allow rules
- `systemctl list-timers --all | grep -i beans-clamav-scan` shows the ClamAV timer
- `zbarimg --help` works
- `sherlock --help` works
- `theHarvester --help` works
- `shodan --help` works
- `recon-ng -h` works
- Firefox opens with visible bookmarks toolbar and imported bookmarks
- Wallpaper and Cinnamon pinned launchers are applied
- User is in `vboxsf` group (`id <user>`; change takes effect after logout/reboot)

## What Beans Installs

### Default Browsers

- Firefox: configured as the research browser with Beans-managed `user.js`, a default profile, visible bookmarks toolbar, and imported toolbar bookmark assets
- Brave: installed and otherwise unmodified
- Google Chrome: installed and otherwise unmodified
- Tor Browser: installed via `torbrowser-launcher`; first-run setup is user-completed

### Default Applications and Tools

- VS Code
- Obsidian
- SpiderFoot
- Whisper
- Sherlock
- theHarvester
- Shodan CLI
- recon-ng
- zbar-tools
- KeePassXC
- VLC
- Terminator
- steghide
- exiftool
- sqlitebrowser
- proxychains4

### Security Baseline

- UFW with default deny for inbound and outbound traffic
- Explicit outbound allow rules for `53/tcp`, `53/udp`, `80/tcp`, `443/tcp`, `443/udp`, and `123/udp`
- Weekly ClamAV scans of `/tmp`, `/var/tmp`, `/dev/shm`, `/home`, `/media`, and `/run/user`

### Desktop Customizations

- `xdg-utils`
- Beans wallpaper
- Terminal banner in `.bashrc`
- Mint dark mode via `Mint-Y-Dark`
- Cinnamon taskbar favorites in fixed order: Firefox, Brave, Chrome, Tor Browser, calculator, Obsidian, KeePassXC, VS Code, VLC, and notes

## Operational Notes

- Beans is intended for a fresh VM
- Reboot after install is recommended
- Reboot or logout is required for new `vboxsf` group membership to take effect
- Beans does not auto-mount or link host shares
- `shodan` still requires later API-key configuration
- SearXNG is deferred to Beans 2.0 and is not installed by this release
- Whisper prefers GPU acceleration when `nvidia-smi` is present and a compatible PyTorch CUDA wheel validates; if validation fails, Beans falls back to CPU mode automatically
- Beans does not automatically install `nvidia-utils-*`; in most VirtualBox guests, the host laptop GPU is not exposed as a usable NVIDIA device

## Assets

### Firefox Bookmark Assets

- Source folder: `assets/firefox/bookmarks/`
- `bookmarks.html` is imported as direct top-level toolbar links
- `LINKS_2024.html` is imported into a toolbar folder named `LINKS`
- `OSINT_Combine_bookmarks_11_12_25.html` is imported into a toolbar folder named `OSINT Combine`

After bookmark updates:

```bash
sudo python3 main.py --refresh-assets firefox
```

### Obsidian Vault Seeds

- Source path: `assets/obsidian/vaults/Study Vault/`
- Seeded content: `TRAINING RESOURCES/` and `OPEN SOURCE RESEARCH - MIND MAP.canvas`
- `.obsidian/` is intentionally not seeded

After Obsidian asset updates:

```bash
sudo python3 main.py --refresh-assets obsidian
```

## Training Workflow

- Keep one pristine master VM or snapshot as baseline
- Perform research and student exercises in disposable clones
- Rebuild the baseline from master when needed instead of carrying forward long-lived drift

## Deferred Tools

- SearXNG (planned for Beans 2.0)
- Maigret
- GHunt
- Waybackpack
- gallery-dl
- Amass

## Sources Used For Packaging Decisions

- Whisper: <https://github.com/openai/whisper>
- theHarvester installation guidance: <https://github.com/laramies/theHarvester/wiki/Installation>
- theHarvester Python requirement: <https://github.com/laramies/theHarvester/blob/master/pyproject.toml>
- PyTorch CUDA wheel guidance: <https://pytorch.org/get-started/previous-versions/>
