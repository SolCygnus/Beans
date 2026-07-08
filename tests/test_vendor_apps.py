from types import SimpleNamespace

from installer import vendor_apps
from installer.vendor_apps import BEANS_HELP_LAUNCHER


def test_sticky_feature_cleanup_removes_beans_files_and_disables_autostart(
    tmp_path, monkeypatch
) -> None:
    context = SimpleNamespace(
        user_home=tmp_path,
        user_local_share_dir=tmp_path / ".local" / "share" / "beans",
        user_state_dir=tmp_path / ".local" / "state" / "beans",
        real_user="student",
    )
    autostart = tmp_path / ".config" / "autostart" / "sticky.desktop"
    autostart.parent.mkdir(parents=True)
    autostart.write_text("Exec=/usr/local/bin/beans-sticky-note\n", encoding="utf-8")
    note = context.user_local_share_dir / "sticky-note.txt"
    note.parent.mkdir(parents=True)
    note.write_text("Beans", encoding="utf-8")
    wrapper = tmp_path / "beans-sticky-note"
    wrapper.write_text("#!/bin/sh\n", encoding="utf-8")
    commands: list[list[str]] = []
    monkeypatch.setattr(vendor_apps, "STICKY_WRAPPER_PATH", wrapper)
    monkeypatch.setattr(
        vendor_apps,
        "run_command",
        lambda ctx, command, **kwargs: commands.append(command),
    )

    vendor_apps._remove_sticky_note_feature(context)

    assert not autostart.exists()
    assert not note.exists()
    assert not wrapper.exists()
    assert [command[-2:] for command in commands] == [
        ["autostart", "false"],
        ["autostart-notes-visible", "false"],
    ]


def test_beans_help_reads_system_owned_command_reference() -> None:
    assert "exec cat /usr/local/share/beans/help.txt" in BEANS_HELP_LAUNCHER
