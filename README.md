# Beans

Beans is a Linux Mint 22.3 Cinnamon bootstrap for Open Source Research VMs in VirtualBox. It targets a fresh guest and installs a research-ready baseline with security defaults and desktop customizations.

## Quick Start

### ⚠️ Requirements — Complete Before Running Beans

> [!IMPORTANT]
> **Install VirtualBox Guest Additions before running Beans.** Beans expects Guest Additions to create the `vboxsf` group. If that group is missing, the `virtualbox-prep` step fails and the user will not have access to VirtualBox shared folders.

- **Operating system:** Linux Mint Cinnamon 22.3
- **VirtualBox:** Guest Additions installed inside the VM
- **Network:** Internet connectivity during installation
- **Account:** A normal user account with `sudo` access

Verify Guest Additions before continuing:

```bash
getent group vboxsf
```

The command must return a `vboxsf` group entry. If it returns no output, install VirtualBox Guest Additions and reboot before running Beans.

### Recommended VM Sizing

- Minimum RAM: `8 GB`
- Practical middle ground: `12 GB`
- Recommended for heavier concurrent Firefox + Chrome use: `16 GB`
- Recommended CPU allocation: `4 vCPUs`
- Disk: enough space for browsers, SpiderFoot, SearXNG, Whisper, logs, and Obsidian vault assets

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
sudo apt install git
git clone https://github.com/SolCygnus/Beans.git
cd beans
sudo python3 main.py --profile default
```

### Other Commands

```bash
beans-help
sudo python3 main.py --dry-run
sudo python3 main.py --only searxng
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
- `beans-searxng-start` opens the local interface at `http://127.0.0.1:8888`
- `beans-searxng-status` reports that the local interface is responding
- Firefox and Chrome open with visible bookmark toolbars and imported bookmarks
- Firefox shows uBlock Origin installed in `about:addons`
- Firefox blocks new location, camera, and microphone permission requests
- Wallpaper and Beans panel launchers are applied before Mint's grouped taskbar without duplicating Firefox
- User is in `vboxsf` group (`id <user>`; change takes effect after logout/reboot)

## What Beans Installs

### Default Browsers

- Firefox: configured as the research browser with Beans-managed `user.js`, a default profile, visible bookmarks toolbar, imported toolbar bookmark assets, and force-installed uBlock Origin
- Brave: installed and otherwise unmodified
- Google Chrome: installed with a visible bookmark bar and the same Beans-managed `PAI` bookmark tree used by Firefox
- Tor Browser: installed via `torbrowser-launcher`; first-run setup is user-completed

### Default Applications and Tools

- VS Code
- Obsidian
- SpiderFoot
- SearXNG
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
- Beans taskbar launchers begin with Firefox, followed by Brave, Chrome, Tor Browser, calculator, Obsidian, KeePassXC, VS Code, VLC, and Mint Notes

## Operational Notes

- Beans is intended for a fresh VM
- Reboot after install is recommended
- Reboot or logout is required for new `vboxsf` group membership to take effect
- Beans does not auto-mount or link host shares
- `shodan` still requires later API-key configuration
- SearXNG is installed in `/opt/beans/searxng/venv`, listens only on `127.0.0.1:8888`, and is started manually
- Whisper prefers GPU acceleration when `nvidia-smi` is present and a compatible PyTorch CUDA wheel validates; if validation fails, Beans falls back to CPU mode automatically
- Beans does not automatically install `nvidia-utils-*`; in most VirtualBox guests, the host laptop GPU is not exposed as a usable NVIDIA device

### SearXNG Commands

Run the launcher commands as the normal desktop user, not with `sudo`.

Start SearXNG and open it in the default browser:

```bash
beans-searxng-start
```

To install or repair only SearXNG on an existing Beans VM, update the Beans repository and run:

```bash
sudo python3 main.py --only searxng
```

Check or stop the local instance:

```bash
beans-searxng-status
beans-searxng-stop
```

SearXNG runs from its dedicated Python virtual environment and stores its per-user runtime log at `~/.local/state/beans/searxng.log`. If startup fails, inspect the log with:

```bash
tail -n 50 ~/.local/state/beans/searxng.log
```

The launcher binds SearXNG to localhost only; it is not exposed to the VM network.

## Assets

### Browser Bookmark Assets

- Shared Firefox and Chrome source folder: `assets/firefox/bookmarks/`
- `bookmarks.html` is imported as direct top-level toolbar links
- `PAI_bookmarks_2026.html` supplies the complete managed `PAI` toolbar folder for Firefox and Chrome
- Export wrapper folders are removed while all headers beneath `PAI` retain their original folder hierarchy

After bookmark updates:

```bash
sudo python3 main.py --refresh-assets firefox
```

To refresh both browsers:

```bash
sudo python3 main.py --refresh-assets firefox chrome
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
- SearXNG step-by-step installation: <https://docs.searxng.org/admin/installation-searxng.html>
- SearXNG settings: <https://docs.searxng.org/admin/settings/settings.html>
