from installer.vendor_apps import BEANS_HELP_LAUNCHER, STICKY_AUTOSTART, STICKY_NOTE_LAUNCHER


def test_sticky_autostart_uses_beans_launcher() -> None:
    assert "Exec=/usr/local/bin/beans-sticky-note" in STICKY_AUTOSTART
    assert "X-GNOME-Autostart-enabled=true" in STICKY_AUTOSTART


def test_sticky_launcher_creates_welcome_note_once() -> None:
    assert "sticky --autostart" in STICKY_NOTE_LAUNCHER
    assert "gsettings set org.x.sticky autostart true" in STICKY_NOTE_LAUNCHER
    assert "gsettings set org.x.sticky autostart-notes-visible true" in STICKY_NOTE_LAUNCHER
    assert "gdbus wait --session --timeout 1 org.x.sticky" in STICKY_NOTE_LAUNCHER
    assert "org.x.sticky.NewNote" in STICKY_NOTE_LAUNCHER
    assert 'marker="$state_dir/sticky-note-created-v2"' in STICKY_NOTE_LAUNCHER
    assert 'touch "$marker"' in STICKY_NOTE_LAUNCHER


def test_beans_help_reads_system_owned_command_reference() -> None:
    assert "exec cat /usr/local/share/beans/help.txt" in BEANS_HELP_LAUNCHER
