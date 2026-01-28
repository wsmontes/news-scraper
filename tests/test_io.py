from __future__ import annotations

from datetime import datetime
from pathlib import Path

from news_scraper.io import write_csv, write_jsonl
from news_scraper.types import Article


def test_write_jsonl(tmp_path: Path):
    out = tmp_path / "out.jsonl"
    write_jsonl(out, [Article(url="https://example.com", date_published=datetime(2020, 1, 1), text="x")])
    content = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1
    assert "example.com" in content[0]


def test_write_csv(tmp_path: Path):
    out = tmp_path / "out.csv"
    write_csv(out, [Article(url="https://example.com", title="t", text="x")])
    content = out.read_text(encoding="utf-8")
    assert "url" in content
    assert "https://example.com" in content
