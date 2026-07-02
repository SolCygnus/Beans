from pathlib import Path
from types import SimpleNamespace

from installer.firefox import _managed_bookmarks, _netscape_bookmark_tree, _policy_bookmarks


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

OSINT_BOOKMARKS = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
    <DT><H3>Bookmarks bar</H3>
    <DL><p>
        <DT><H3>Search Engines</H3>
        <DL><p>
            <DT><A HREF="https://example.com/search">Search Tool</A>
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


def test_nested_sources_are_managed_bookmarks_not_flat_duplicates(tmp_path: Path) -> None:
    _write_bookmark(tmp_path, "LINKS_2024.html", NESTED_BOOKMARKS)
    _write_bookmark(tmp_path, "OSINT_Combine_bookmarks_11_12_25.html", OSINT_BOOKMARKS)
    context = SimpleNamespace(assets_dir=tmp_path)

    assert _managed_bookmarks(context) == [
        {"toplevel_name": "PAI"},
        {
            "name": "Research",
            "children": [
                {
                    "name": "Research Link",
                    "url": "https://example.com/research",
                }
            ],
        },
        {
            "name": "OSINT Combine",
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
