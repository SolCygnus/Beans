Beans desktop notes

Important Admin Notes:

- Beans was built for Linux Mint 22.3 Cinnamon on VirtualBox.
- Use a master VM or snapshot as a baseline and perform research in disposable clones.
- If this desktop file is deleted, display it anytime from a terminal with `beans-help`.

Web Research:

- Chrome is installed without security modifications and includes the Beans-managed PAI bookmarks.
- Firefox is the default research browser. It is hardened without fully locking it down, helping websites remain usable.
- Brave is installed but not modified.
- Tor Browser finishes setup on first launch.

Beans Commands:

- Start local SearXNG: `beans-searxng-start`
- Check or stop SearXNG: `beans-searxng-status` or `beans-searxng-stop`
- Transcribe media with WhisperAI: `beans-whisper INPUT_FILE`
- Show WhisperAI options: `beans-whisper --help`
- Print common file hashes: `beans-hash-check FILE`
- Verify a known hash: `beans-hash-check FILE --hash DIGEST`
- Run the managed malware scan: `sudo beans-clamav-scan`

Research Tools:

- SpiderFoot local web interface: `spiderfoot`, then open `http://127.0.0.1:5001`
- Search usernames with Sherlock: `sherlock USERNAME`
- Show theHarvester data-source options: `theHarvester --help`
- Configure Shodan before first use: `shodan init API_KEY`
- Look up an IP with Shodan: `shodan host IP_ADDRESS`
- Start the recon-ng console: `recon-ng`
- Complete or launch Tor Browser setup: `torbrowser-launcher`

File and Media Tools:

- Read file metadata: `exiftool FILE`
- Inspect a steganography container: `steghide info FILE`
- Scan a QR code or barcode image: `zbarimg IMAGE_FILE`
- Inspect media streams: `ffmpeg -i MEDIA_FILE`
- Open a SQLite database: `sqlitebrowser DATABASE_FILE`
- Run a command through a configured proxy: `proxychains4 COMMAND`
- Open media in VLC: `vlc MEDIA_FILE`

Security and Status:

- Review firewall rules: `sudo ufw status verbose`
- Check the weekly malware-scan timer: `systemctl status beans-clamav-scan.timer`
- Read the latest malware-scan log: `sudo less /var/log/beans/clamav-scan.log`

Run SearXNG, WhisperAI, and research tools as the normal desktop user. Run only commands marked with `sudo` as administrator.

Beans-Installer Commands:

- Run installer and refresh commands from the Beans repository directory.
- Preview an installer run: `sudo python3 main.py --dry-run`
- Install or repair one component: `sudo python3 main.py --only COMPONENT`
- Refresh all managed assets: `sudo python3 main.py --refresh-assets all`
- Refresh selected assets: `sudo python3 main.py --refresh-assets firefox chrome obsidian desktop`
