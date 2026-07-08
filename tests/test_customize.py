from installer.customize import (
    PANEL_APPLET_ENTRY,
    PANEL_SLOTS,
    _enabled_with_panel_applet,
)


def test_panel_applet_is_added_once() -> None:
    enabled = "['panel1:left:0:menu@cinnamon.org:0']"

    assert _enabled_with_panel_applet(enabled) == (
        "['panel1:left:0:menu@cinnamon.org:0', "
        f"'{PANEL_APPLET_ENTRY}']"
    )
    assert _enabled_with_panel_applet(
        f"['panel1:left:0:menu@cinnamon.org:0', '{PANEL_APPLET_ENTRY}']"
    ) is None


def test_beans_launcher_set_does_not_duplicate_firefox() -> None:
    candidates = [candidate for _, slot in PANEL_SLOTS for candidate in slot]

    assert "firefox.desktop" not in candidates
    assert "google-chrome.desktop" in candidates
    assert "obsidian.desktop" in candidates
    assert "sticky.desktop" in candidates
