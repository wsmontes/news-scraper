from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from .extract import extract_article
from .dataset import write_parquet_dataset
from .io import write_csv, write_jsonl
from .polite import PoliteSettings, PoliteSession
from .types import Article


def scrape_urls(
    urls: list[str],
    out_path: Path | None = None,
    out_format: str = "jsonl",
    *,
    dataset_dir: Path | None = None,
    delay_seconds: float = 1.0,
    respect_robots: bool = True,
    user_agent: str | None = None,
    timeout_seconds: float = 20.0,
    max_articles: int | None = None,
) -> list[Article]:
    if out_path is None and dataset_dir is None:
        raise ValueError("Informe out_path e/ou dataset_dir")

    settings = PoliteSettings(
        delay_seconds=delay_seconds,
        respect_robots=respect_robots,
        user_agent=user_agent or PoliteSettings.user_agent,
        timeout_seconds=timeout_seconds,
    )
    session = PoliteSession(settings)

    selected_urls = urls
    if max_articles is not None:
        selected_urls = urls[: max(0, int(max_articles))]

    articles: list[Article] = []
    for url in tqdm(selected_urls, desc="Scraping"):
        scraped_at = datetime.now(timezone.utc)
        try:
            resp = session.get(url)
            html = resp.text
            article = extract_article(html, url)
            article.scraped_at = scraped_at
            # Se extração vier vazia, ainda registramos para debug acadêmico
            if not article.extra:
                article.extra = {}
            article.extra.update({"http_status": resp.status_code})
            articles.append(article)
        except Exception as e:
            articles.append(Article(url=url, scraped_at=scraped_at, extra={"error": str(e)}))

    if out_path is not None:
        fmt = out_format.lower().strip()
        if fmt == "jsonl":
            write_jsonl(out_path, articles)
        elif fmt == "csv":
            write_csv(out_path, articles)
        else:
            raise ValueError(f"Formato inválido: {out_format}. Use jsonl ou csv.")

    if dataset_dir is not None:
        write_parquet_dataset(dataset_dir, articles)

    return articles


def scrape_to_dicts(articles: list[Article]) -> list[dict]:
    return [asdict(a) for a in articles]
