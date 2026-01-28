from __future__ import annotations

from pathlib import Path

from news_scraper.sources import enabled_rss_feeds, load_sources_csv


def test_load_sources_csv_and_enabled_rss(tmp_path: Path):
    csv_path = tmp_path / "sources.csv"
    csv_path.write_text(
        "enabled,source_id,name,type,url,tags\n"
        "1,g1,G1,rss,https://g1.globo.com/rss/g1/,geral\n"
        "0,x,Disabled,rss,https://example.com/rss.xml,teste\n",
        encoding="utf-8",
    )

    sources = load_sources_csv(csv_path)
    feeds = enabled_rss_feeds(sources)
    assert "https://g1.globo.com/rss/g1/" in feeds
    assert "https://example.com/rss.xml" not in feeds
