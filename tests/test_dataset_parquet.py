from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import duckdb

from news_scraper.dataset import write_parquet_dataset
from news_scraper.types import Article


def test_write_parquet_dataset_partitions_and_reads(tmp_path: Path):
    dataset_dir = tmp_path / "articles"

    articles = [
        Article(
            url="https://example.com/a",
            source="example.com",
            title="A",
            date_published=datetime(2020, 1, 2, tzinfo=timezone.utc),
            scraped_at=datetime(2020, 1, 3, tzinfo=timezone.utc),
            text="hello",
            extra={"http_status": 200},
        ),
        Article(
            url="https://example.com/b",
            source="example.com",
            title="B",
            date_published=datetime(2020, 1, 2, tzinfo=timezone.utc),
            scraped_at=datetime(2020, 1, 3, tzinfo=timezone.utc),
            text="world",
            extra={"http_status": 200},
        ),
    ]

    written = write_parquet_dataset(dataset_dir, articles)
    assert written
    assert all(p.exists() for p in written)

    # DuckDB: lê tudo via glob
    con = duckdb.connect()
    count = con.execute(
        "SELECT count(*) FROM read_parquet(?)",
        [str(dataset_dir / "**" / "*.parquet")],
    ).fetchone()[0]
    assert count == 2
