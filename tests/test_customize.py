from installer.customize import LEGACY_PANEL_APPLET_ENTRY, _without_legacy_panel_applet


def test_legacy_panel_launcher_is_removed_from_enabled_applets() -> None:
    enabled = (
        "['panel1:left:0:menu@cinnamon.org:0', "
        f"'{LEGACY_PANEL_APPLET_ENTRY}', "
        "'panel1:left:1:grouped-window-list@cinnamon.org:2']"
    )

    assert _without_legacy_panel_applet(enabled) == (
        "['panel1:left:0:menu@cinnamon.org:0', "
        "'panel1:left:1:grouped-window-list@cinnamon.org:2']"
    )


def test_enabled_applets_without_legacy_launcher_are_unchanged() -> None:
    enabled = "['panel1:left:0:menu@cinnamon.org:0']"

    assert _without_legacy_panel_applet(enabled) is None
