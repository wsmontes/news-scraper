from __future__ import annotations

import io
import sys
from datetime import datetime, timezone
from pathlib import Path

from news_scraper.dataset import write_parquet_dataset
from news_scraper.query import dataset_stats, query_dataset
from news_scraper.types import Article


def test_query_dataset_sql(tmp_path: Path):
    dataset_dir = tmp_path / "articles"
    articles = [
        Article(
            url="https://example.com/1",
            source="example.com",
            title="Article 1",
            date_published=datetime(2020, 1, 1, tzinfo=timezone.utc),
            scraped_at=datetime(2020, 1, 2, tzinfo=timezone.utc),
        ),
        Article(
            url="https://example.com/2",
            source="example.com",
            title="Article 2",
            date_published=datetime(2020, 1, 1, tzinfo=timezone.utc),
            scraped_at=datetime(2020, 1, 2, tzinfo=timezone.utc),
        ),
    ]
    write_parquet_dataset(dataset_dir, articles)

    # Query via SQL
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        query_dataset(dataset_dir, "SELECT count(*) FROM articles", output_format="table")
        output = sys.stdout.getvalue()
        # A query retorna 1 linha (o count), não 2
        assert "(1 rows)" in output or "(1 row)" in output
        assert "2" in output  # o valor do count
    finally:
        sys.stdout = old_stdout


def test_dataset_stats(tmp_path: Path):
    dataset_dir = tmp_path / "articles"
    articles = [
        Article(
            url="https://a.com/1",
            source="a.com",
            title="A1",
            date_published=datetime(2020, 1, 1, tzinfo=timezone.utc),
            scraped_at=datetime(2020, 1, 2, tzinfo=timezone.utc),
        ),
    ]
    write_parquet_dataset(dataset_dir, articles)

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        dataset_stats(dataset_dir)
        output = sys.stdout.getvalue()
        assert "Total de artigos: 1" in output
    finally:
        sys.stdout = old_stdout
