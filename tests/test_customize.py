import json
from types import SimpleNamespace

from installer import customize
from installer.customize import (
    PANEL_APPLET_ENTRY,
    PANEL_SLOTS,
    _arranged_panel_applets,
    _grouped_window_list_instance_ids,
)


ENABLED_APPLETS = (
    "['panel1:left:0:menu@cinnamon.org:0', "
    "'panel1:left:1:separator@cinnamon.org:1', "
    "'panel1:left:2:grouped-window-list@cinnamon.org:2']"
)


def test_panel_launcher_precedes_grouped_windows_without_position_collision() -> None:
    assert _arranged_panel_applets(ENABLED_APPLETS) == (
        "['panel1:left:0:menu@cinnamon.org:0', "
        "'panel1:left:1:separator@cinnamon.org:1', "
        f"'{PANEL_APPLET_ENTRY}', "
        "'panel1:left:3:grouped-window-list@cinnamon.org:2']"
    )


def test_firefox_is_first_beans_launcher() -> None:
    assert PANEL_SLOTS[0] == ("Firefox", ["firefox.desktop"])


def test_grouped_firefox_pin_is_removed(tmp_path, monkeypatch) -> None:
    context = SimpleNamespace(user_home=tmp_path)
    monkeypatch.setattr(
        customize,
        "ensure_directory_for_user",
        lambda ctx, path: path.mkdir(parents=True, exist_ok=True),
    )
    monkeypatch.setattr(customize, "chown_path", lambda ctx, path: None)

    customize._remove_grouped_firefox_pin(
        context, _grouped_window_list_instance_ids(ENABLED_APPLETS)
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
        "nemo.desktop",
        "org.gnome.Terminal.desktop",
    ]
