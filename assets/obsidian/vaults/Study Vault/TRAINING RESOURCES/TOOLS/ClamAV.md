# ClamAV

ClamAV is a malware-scanning toolkit. Beans installs ClamAV, creates the `beans-clamav-scan` command, and enables a weekly systemd scan timer.

> [!note]
> Beans schedules its scan for Sunday at 3:00 AM. A missed scan runs after the machine is next available because the timer is persistent.

## Beans Scan Command

Run the Beans-configured scan manually:

```bash
sudo beans-clamav-scan
```

The Beans scan:

- Recursively scans `/tmp`, `/var/tmp`, `/dev/shm`, `/home`, `/media`, and `/run/user`.
- Displays infected files rather than every scanned file.
- Excludes user cache and Trash directories.
- Writes its report to `/var/log/beans/clamav-scan.log`.

The Beans wrapper uses a fixed scan configuration and does not accept a custom file or directory argument. Use `clamscan` directly for targeted scans.

View the latest Beans scan log:

```bash
sudo less /var/log/beans/clamav-scan.log
```

## Check the Scheduled Scan

```bash
systemctl status beans-clamav-scan.timer
systemctl list-timers --all | grep beans-clamav-scan
```

Run the systemd scan immediately:

```bash
sudo systemctl start beans-clamav-scan.service
```

Check its result:

```bash
systemctl status beans-clamav-scan.service
```

## Update Virus Signatures

ClamAV uses `freshclam` to download official malware signatures. Check the automatic updater:

```bash
systemctl status clamav-freshclam
```

Run a manual update when the automatic service is not running:

```bash
sudo freshclam
```

## Targeted Scans with `clamscan`

Scan one file:

```bash
clamscan "$HOME/Downloads/example.zip"
```

Scan the current directory without descending into subdirectories:

```bash
clamscan .
```

Recursively scan Downloads and only print infected files:

```bash
clamscan --recursive --infected "$HOME/Downloads"
```

Save a scan report:

```bash
clamscan --recursive --infected --log="$HOME/clamav-scan.log" "$HOME/Downloads"
```

See all options:

```bash
clamscan --help
man clamscan
```

## Quarantine Instead of Delete

Create a quarantine directory and move detections into it:

```bash
mkdir -p "$HOME/Quarantine"
clamscan --recursive --infected --move="$HOME/Quarantine" "$HOME/Downloads"
```

> [!warning]
> Avoid the `--remove` option. False positives are possible, and automatic deletion can destroy legitimate files. Quarantine suspicious files and investigate them instead.

## Understanding Results

At the end of a scan, ClamAV displays a summary including scanned files, infected files, data scanned, and elapsed time.

Common exit codes:

| Code | Meaning |
|---|---|
| `0` | No malware found |
| `1` | Malware found |
| `2` | An error occurred |

## Common Problems

- **Outdated signatures:** Check `clamav-freshclam` or run `sudo freshclam` when that service is stopped.
- **Permission denied:** Use `sudo` only when scanning protected system locations or running the Beans system scan.
- **Scan takes a long time:** Target a specific directory. Full-system recursive scans can be slow.
- **Infected file reported:** Do not open it. Record the detection name, quarantine the file, and verify the finding before deleting anything.

## Reference

- [ClamAV scanning documentation](https://docs.clamav.net/manual/Usage/Scanning.html)
- [ClamAV signature management](https://docs.clamav.net/manual/Usage/SignatureManagement.html)
