from types import SimpleNamespace

from installer import runner


def test_desktop_refresh_reinstalls_assets_before_customizations(monkeypatch) -> None:
    calls: list[str] = []
    context = SimpleNamespace(refresh_targets=["desktop"])
    monkeypatch.setattr(
        runner.vendor_apps,
        "install_desktop_assets",
        lambda ctx: calls.append("assets"),
    )
    monkeypatch.setattr(
        runner.customize,
        "apply_desktop_customizations",
        lambda ctx: calls.append("customize"),
    )
    monkeypatch.setattr(runner, "record_result", lambda *args: None)
    monkeypatch.setattr(runner, "write_summary", lambda ctx: None)

    assert runner.refresh_assets(context) == 0
    assert calls == ["assets", "customize"]
