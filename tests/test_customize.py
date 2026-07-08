import json
from types import SimpleNamespace

from installer import customize
from installer.customize import (
    LEGACY_PANEL_APPLET_ENTRY,
    _grouped_window_list_instance_ids,
    _without_legacy_panel_applet,
)


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


def test_grouped_window_list_instance_ids_are_read_from_enabled_applets() -> None:
    enabled = (
        "['panel1:left:0:menu@cinnamon.org:0', "
        "'panel1:left:1:grouped-window-list@cinnamon.org:2']"
    )

    assert _grouped_window_list_instance_ids(enabled) == ["2"]


def test_grouped_window_list_favorites_use_pinned_apps_setting(
    tmp_path, monkeypatch
) -> None:
    context = SimpleNamespace(user_home=tmp_path)
    monkeypatch.setattr(
        customize,
        "ensure_directory_for_user",
        lambda ctx, path: path.mkdir(parents=True, exist_ok=True),
    )
    monkeypatch.setattr(customize, "chown_path", lambda ctx, path: None)

    customize._write_grouped_window_list_favorites(
        context, ["2"], ["firefox.desktop", "google-chrome.desktop"]
    )

    config_path = (
        tmp_path
        / ".cinnamon"
        / "configs"
        / "grouped-window-list@cinnamon.org"
        / "2.json"
    )
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["pinned-apps"]["value"] == [
        "firefox.desktop",
        "google-chrome.desktop",
    ]
