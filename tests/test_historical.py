from __future__ import annotations

from datetime import date
from pathlib import Path

from news_scraper.historical import (
    extract_date_from_url,
    generate_urls_by_date_pattern,
    generate_urls_by_month_pattern,
)


def test_generate_urls_by_date_pattern(tmp_path: Path):
    out = tmp_path / "urls.txt"
    urls = generate_urls_by_date_pattern(
        "https://example.com/{YYYY}/{MM}/{DD}/",
        date(2020, 1, 1),
        date(2020, 1, 3),
        out,
    )
    assert len(urls) == 3
    assert "2020/01/01" in urls[0]
    assert "2020/01/03" in urls[2]
    assert out.exists()


def test_generate_urls_by_month_pattern(tmp_path: Path):
    out = tmp_path / "urls.txt"
    urls = generate_urls_by_month_pattern(
        "https://example.com/{YYYY}/{MM}/",
        2020,
        1,
        2020,
        3,
        out,
    )
    assert len(urls) == 3
    assert "2020/01" in urls[0]
    assert "2020/03" in urls[2]


def test_extract_date_from_url():
    assert extract_date_from_url("https://example.com/2020/01/15/noticia") == date(2020, 1, 15)
    assert extract_date_from_url("https://example.com/20200115/noticia") == date(2020, 1, 15)
    assert extract_date_from_url("https://example.com/noticia") is None
