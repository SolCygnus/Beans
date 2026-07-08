from pathlib import Path
from types import SimpleNamespace

from installer.firefox import (
    _firefox_extension_settings,
    _firefox_permission_settings,
    _managed_bookmarks,
    _managed_pai_tree,
    _netscape_bookmark_tree,
    _policy_bookmarks,
)


NESTED_BOOKMARKS = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Bookmarks Toolbar</H3>
    <DL><p>
        <DT><H3>Research</H3>
        <DL><p>
            <DT><A HREF="https://example.com/research">Research Link</A>
        </DL><p>
    </DL><p>
</DL><p>
"""

CONSOLIDATED_BOOKMARKS = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Bookmarks bar</H3>
    <DL><p>
    </DL><p>
    <DT><H3>Bookmarks Toolbar</H3>
    <DL><p>
        <DT><H3>PAI</H3>
        <DL><p>
            <DT><H3>Research</H3>
            <DL><p>
                <DT><H3>Search Engines</H3>
                <DL><p>
                    <DT><A HREF="https://example.com/search">Search Tool</A>
                </DL><p>
            </DL><p>
        </DL><p>
    </DL><p>
</DL><p>
"""


def _write_bookmark(tmp_path: Path, filename: str, content: str) -> Path:
    bookmarks_dir = tmp_path / "firefox" / "bookmarks"
    bookmarks_dir.mkdir(parents=True, exist_ok=True)
    path = bookmarks_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def test_netscape_bookmark_tree_preserves_nested_folders(tmp_path: Path) -> None:
    path = _write_bookmark(tmp_path, "LINKS_2024.html", NESTED_BOOKMARKS)

    assert _netscape_bookmark_tree(path) == [
        {
            "name": "Research",
            "children": [
                {"name": "Research Link", "url": "https://example.com/research"}
            ],
        },
    ]


def test_managed_pai_tree_removes_export_wrappers_and_preserves_headers(tmp_path: Path) -> None:
    path = _write_bookmark(tmp_path, "PAI_bookmarks_2026.html", CONSOLIDATED_BOOKMARKS)

    assert _managed_pai_tree(path) == [
        {
            "name": "Research",
            "children": [
                {
                    "name": "Search Engines",
                    "children": [
                        {
                            "name": "Search Tool",
                            "url": "https://example.com/search",
                        }
                    ],
                }
            ],
        }
    ]


def test_consolidated_source_is_one_toolbar_pai_folder(tmp_path: Path) -> None:
    _write_bookmark(tmp_path, "PAI_bookmarks_2026.html", CONSOLIDATED_BOOKMARKS)
    context = SimpleNamespace(assets_dir=tmp_path)

    assert _managed_bookmarks(context) == [
        {"toplevel_name": "PAI"},
        {
            "name": "Research",
            "children": [
                {
                    "name": "Search Engines",
                    "children": [
                        {
                            "name": "Search Tool",
                            "url": "https://example.com/search",
                        }
                    ],
                }
            ],
        },
    ]
    assert _policy_bookmarks(context) == []


def test_current_assets_keep_toolbar_links_separate_from_pai_hierarchy() -> None:
    assets_dir = Path(__file__).parents[1] / "assets"
    context = SimpleNamespace(assets_dir=assets_dir)

    managed = _managed_bookmarks(context)
    top_level_names = [entry.get("name") for entry in managed[1:]]
    assert managed[0] == {"toplevel_name": "PAI"}
    assert "Bookmarks bar" not in top_level_names
    assert "Bookmarks Toolbar" not in top_level_names
    assert "PAI" not in top_level_names
    assert "BASIC COMPUTE CONCEPTS" in top_level_names
    assert "OSINT Combine Stack" in top_level_names

    basic_computing = next(
        entry for entry in managed if entry.get("name") == "BASIC COMPUTE CONCEPTS"
    )
    assert basic_computing["children"][0]["name"] == "Number Conversion"
    assert any(
        child.get("name") == "Academic"
        for child in basic_computing.get("children", [])
    )
    assert [entry["Title"] for entry in _policy_bookmarks(context)] == [
        "Bellingcat",
        "VirusTotal",
        "OSINT Framework",
    ]


def test_firefox_extension_settings_force_install_ublock_origin() -> None:
    assert _firefox_extension_settings() == {
        "uBlock0@raymondhill.net": {
            "installation_mode": "force_installed",
            "install_url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi",
        }
    }


def test_firefox_permission_settings_block_sensitive_new_requests() -> None:
    assert _firefox_permission_settings() == {
        "Camera": {
            "BlockNewRequests": True,
            "Locked": True,
        },
        "Microphone": {
            "BlockNewRequests": True,
            "Locked": True,
        },
        "Location": {
            "BlockNewRequests": True,
            "Locked": True,
        },
    }
