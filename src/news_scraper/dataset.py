from __future__ import annotations

import json
import re
import time
import urllib.parse
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq

from .types import Article


def _normalize_datetime(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _safe_source(source: str) -> str:
    # Mantém algo que funcione bem em partições de diretório.
    source = source.strip().lower() or "unknown"
    source = re.sub(r"\s+", "-", source)
    source = re.sub(r"[^a-z0-9._-]+", "_", source)
    return source[:120] or "unknown"


def _source_from_url(url: str) -> str:
    netloc = urllib.parse.urlparse(url).netloc.lower().strip()
    return netloc or "unknown"


def _partition_for(article: Article) -> tuple[int, int, int, str]:
    # Para séries temporais, preferimos o publicado; se não existir, usamos o scraped_at.
    dt = _normalize_datetime(article.date_published or article.scraped_at)
    source = article.source or _source_from_url(article.url)
    return dt.year, dt.month, dt.day, _safe_source(source)


def _row_for(article: Article) -> dict:
    payload = asdict(article)
    # Serialização “estável” para Parquet (evita campos heterogêneos em extra)
    extra = payload.get("extra") or {}

    date_published = article.date_published
    scraped_at = article.scraped_at

    def to_iso(dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return _normalize_datetime(dt).isoformat()

    http_status = None
    error = None
    if isinstance(extra, dict):
        http_status = extra.get("http_status")
        error = extra.get("error")

    return {
        "url": article.url,
        "source": article.source or _source_from_url(article.url),
        "title": article.title,
        "author": article.author,
        "date_published": to_iso(date_published),
        "scraped_at": to_iso(scraped_at),
        "language": article.language,
        "text": article.text,
        "http_status": http_status,
        "error": error,
        "extra_json": json.dumps(extra, ensure_ascii=False, sort_keys=True),
    }


def write_parquet_dataset(dataset_dir: Path, articles: list[Article]) -> list[Path]:
    """Escreve artigos em Parquet particionado por data e fonte.

    Layout:
      dataset_dir/year=YYYY/month=MM/day=DD/source=<source>/part-*.parquet

    Esse layout funciona bem com DuckDB, Spark e engines colunares.
    """

    dataset_dir.mkdir(parents=True, exist_ok=True)

    by_partition: dict[tuple[int, int, int, str], list[dict]] = defaultdict(list)
    for article in articles:
        by_partition[_partition_for(article)].append(_row_for(article))

    written: list[Path] = []
    for (year, month, day, source), rows in by_partition.items():
        partition_path = (
            dataset_dir
            / f"year={year:04d}"
            / f"month={month:02d}"
            / f"day={day:02d}"
            / f"source={source}"
        )
        partition_path.mkdir(parents=True, exist_ok=True)

        filename = f"part-{int(time.time() * 1000)}-{uuid4().hex[:10]}.parquet"
        path = partition_path / filename

        table = pa.Table.from_pylist(rows)
        pq.write_table(table, path, compression="zstd")
        written.append(path)

    return written
