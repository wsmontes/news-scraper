from __future__ import annotations

from pathlib import Path

from news_scraper.sources_cli import add_source, list_sources, toggle_source


def test_sources_cli_add_list_toggle(tmp_path: Path):
    csv_path = tmp_path / "sources.csv"

    # Add
    add_source(csv_path, "test1", "Test Source", "rss", "https://example.com/feed", tags="news")
    assert csv_path.exists()

    # List (smoke test - não trava)
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        list_sources(csv_path)
        output = sys.stdout.getvalue()
        assert "test1" in output
    finally:
        sys.stdout = old_stdout

    # Toggle
    toggle_source(csv_path, "test1", enable=False)
    content = csv_path.read_text()
    assert "0,test1" in content
