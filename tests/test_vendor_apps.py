from installer.vendor_apps import BEANS_HELP_LAUNCHER


def test_beans_help_reads_system_owned_command_reference() -> None:
    assert "exec cat /usr/local/share/beans/help.txt" in BEANS_HELP_LAUNCHER
