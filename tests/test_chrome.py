from types import SimpleNamespace

from installer import chrome, runner


def test_chrome_policy_reuses_firefox_tree_with_quick_links(monkeypatch) -> None:
    context = object()
    monkeypatch.setattr(
        chrome.firefox,
        "_managed_bookmarks",
        lambda ctx: [
            {"toplevel_name": "PAI"},
            {"name": "Research", "children": [{"name": "Example", "url": "https://example.com"}]},
        ],
    )
    monkeypatch.setattr(
        chrome.firefox,
        "_policy_bookmarks",
        lambda ctx: [{"Title": "Bellingcat", "URL": "https://bellingcat.com", "Placement": "toolbar"}],
    )

    assert chrome._policy_payload(context) == {
        "BookmarkBarEnabled": True,
        "ManagedBookmarks": [
            {"toplevel_name": "PAI"},
            {"name": "Bellingcat", "url": "https://bellingcat.com"},
            {"name": "Research", "children": [{"name": "Example", "url": "https://example.com"}]},
        ],
    }


def test_research_browsers_configures_chrome(monkeypatch) -> None:
    calls = []
    context = SimpleNamespace()
    monkeypatch.setattr(runner.vendor_apps, "install_browsers", lambda ctx: calls.append("install"))
    monkeypatch.setattr(runner.firefox, "seed_firefox", lambda ctx: calls.append("firefox"))
    monkeypatch.setattr(runner.chrome, "seed_chrome", lambda ctx: calls.append("chrome"))

    runner.execute_component(context, "research-browsers")

    assert calls == ["install", "firefox", "chrome"]


def test_chrome_is_a_refresh_target() -> None:
    args = runner.parse_args(["--refresh-assets", "chrome"])
    assert args.refresh_assets == ["chrome"]
