from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .types import Article


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_jsonl(path: Path, articles: list[Article]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(asdict(article), ensure_ascii=False, default=_json_default))
            f.write("\n")


def write_csv(path: Path, articles: list[Article]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "url",
        "title",
        "author",
        "date_published",
        "scraped_at",
        "language",
        "source",
        "text",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(
                {
                    "url": article.url,
                    "title": article.title,
                    "author": article.author,
                    "date_published": article.date_published.isoformat() if article.date_published else None,
                    "scraped_at": article.scraped_at.isoformat() if article.scraped_at else None,
                    "language": article.language,
                    "source": article.source,
                    "text": article.text,
                }
            )
