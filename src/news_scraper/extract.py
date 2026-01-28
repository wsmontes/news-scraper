from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .types import Article

try:
    import trafilatura
except Exception:  # pragma: no cover
    trafilatura = None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return date_parser.parse(value)
    except Exception:
        return None


def _fallback_extract(html: str, url: str) -> Article:
    soup = BeautifulSoup(html, "lxml")
    title = _title_from_html(soup)

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n".join([p for p in paragraphs if p]) if paragraphs else None

    return Article(url=url, title=title, text=text, extra={"method": "bs4_fallback"})


def _title_from_html(soup: BeautifulSoup) -> str | None:
    og = soup.find("meta", attrs={"property": "og:title"})
    if og is not None:
        content = og.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)

    h1 = soup.find("h1")
    if h1 is not None:
        text = h1.get_text(" ", strip=True)
        if text:
            return text

    return None


def _text_from_html_paragraphs(soup: BeautifulSoup) -> str | None:
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n".join([p for p in paragraphs if p]) if paragraphs else None
    return text or None


def extract_article(html: str, url: str) -> Article:
    """Extrai metadados e texto de uma página HTML.

    Preferência: trafilatura (melhor extração de conteúdo principal).
    Fallback: BeautifulSoup (heurística simples baseada em <p>).
    """

    if trafilatura is None:
        return _fallback_extract(html, url)

    extracted_json: str | None = None
    try:
        extracted_json = trafilatura.extract(
            html,
            url=url,
            output_format="json",
            include_comments=False,
            include_tables=False,
        )
    except Exception:
        extracted_json = None

    if not extracted_json:
        return _fallback_extract(html, url)

    try:
        payload: dict[str, Any] = json.loads(extracted_json)
    except Exception:
        return _fallback_extract(html, url)

    article = Article(
        url=url,
        title=payload.get("title"),
        author=payload.get("author"),
        date_published=_parse_date(payload.get("date")),
        text=payload.get("text"),
        language=payload.get("language"),
        source=payload.get("sitename") or payload.get("hostname"),
        extra={k: v for k, v in payload.items() if k not in {"title", "author", "date", "text", "language", "sitename", "hostname"}},
    )

    # Completa campos faltantes com heurísticas do HTML.
    soup: BeautifulSoup | None = None
    if article.title is None or article.text is None:
        soup = BeautifulSoup(html, "lxml")

    if article.title is None and soup is not None:
        article.title = _title_from_html(soup)

    if article.text is None and soup is not None:
        article.text = _text_from_html_paragraphs(soup)

    # Normalização leve
    if article.text:
        article.text = "\n".join(line.rstrip() for line in article.text.splitlines()).strip() or None

    return article
