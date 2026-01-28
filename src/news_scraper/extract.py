from __future__ import annotations

import json
from datetime import datetime
from typing import Any
import logging

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .types import Article

# Novas ferramentas profissionais
try:
    from .extractors import ExtractionPipeline, ExtractedContent
    from .tools import (
        TextCleaner,
        DateNormalizer,
        ContentValidator,
        PaywallDetector,
        LanguageDetector,
    )
    ADVANCED_TOOLS_AVAILABLE = True
except ImportError:
    ADVANCED_TOOLS_AVAILABLE = False

try:
    import trafilatura
except Exception:  # pragma: no cover
    trafilatura = None

logger = logging.getLogger(__name__)


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


def _date_from_html(soup: BeautifulSoup) -> datetime | None:
    """Extrai data de publicação de meta tags e time tags."""
    # Meta tags comuns
    date_metas = [
        'article:published_time',
        'datePublished',
        'date',
        'pubdate',
        'publish_date',
        'dc.date',
        'sailthru.date',
    ]
    
    for meta_name in date_metas:
        # Tenta property
        tag = soup.find('meta', {'property': meta_name})
        if tag and tag.get('content'):
            date = _parse_date(tag.get('content'))
            if date:
                return date
        
        # Tenta name
        tag = soup.find('meta', {'name': meta_name})
        if tag and tag.get('content'):
            date = _parse_date(tag.get('content'))
            if date:
                return date
    
    # Time tags
    time_tag = soup.find('time', {'datetime': True})
    if time_tag:
        date = _parse_date(time_tag.get('datetime'))
        if date:
            return date
    
    return None


def _source_from_html(soup: BeautifulSoup) -> str | None:
    """Extrai nome da fonte de meta tags."""
    source_metas = [
        'og:site_name',
        'twitter:site',
        'application-name',
        'publisher',
    ]
    
    for meta_name in source_metas:
        # Tenta property
        tag = soup.find('meta', {'property': meta_name})
        if tag and tag.get('content'):
            content = tag.get('content')
            if isinstance(content, str) and content.strip():
                return content.strip()
        
        # Tenta name
        tag = soup.find('meta', {'name': meta_name})
        if tag and tag.get('content'):
            content = tag.get('content')
            if isinstance(content, str) and content.strip():
                return content.strip()
    
    return None


def extract_article(html: str, url: str) -> Article:
    """
    Extrai metadados e texto de uma página HTML.
    
    Usa múltiplas estratégias de extração com fallback automático:
    1. ExtractionPipeline (múltiplos extratores com qualidade)
    2. trafilatura (extração robusta)
    3. BeautifulSoup (fallback básico)
    
    Inclui validação, limpeza e detecção de paywall.
    """
    
    # Tentar método avançado com múltiplos extratores
    if ADVANCED_TOOLS_AVAILABLE:
        try:
            article = _extract_with_pipeline(html, url)
            if article:
                logger.debug(f"Extracted with advanced pipeline: {article.title}")
                return article
        except Exception as e:
            logger.debug(f"Advanced extraction failed: {e}")
    
    # Fallback para trafilatura
    if trafilatura is not None:
        try:
            article = _extract_with_trafilatura(html, url)
            if article:
                logger.debug(f"Extracted with trafilatura: {article.title}")
                return article
        except Exception as e:
            logger.debug(f"Trafilatura extraction failed: {e}")
    
    # Fallback final para BeautifulSoup
    logger.debug("Using BeautifulSoup fallback")
    return _fallback_extract(html, url)


def _extract_with_pipeline(html: str, url: str) -> Article | None:
    """Extrai usando pipeline de múltiplos extratores."""
    pipeline = ExtractionPipeline()
    result = pipeline.extract(html, url, min_quality=0.3)
    
    if not result:
        return None
    
    # Detectar paywall
    paywall_info = None
    if ADVANCED_TOOLS_AVAILABLE:
        detector = PaywallDetector()
        paywall_info = detector.detect(html, result.text)
        
        if paywall_info['has_paywall']:
            logger.warning(f"Paywall detected (confidence: {paywall_info['confidence']:.2f})")
    
    # Limpar texto
    clean_text = result.text
    if ADVANCED_TOOLS_AVAILABLE and clean_text:
        cleaner = TextCleaner()
        clean_text = cleaner.remove_boilerplate(clean_text)
        clean_text = cleaner.clean(clean_text)
    
    # Normalizar data
    normalized_date = None
    if result.date:
        if ADVANCED_TOOLS_AVAILABLE:
            normalizer = DateNormalizer()
            normalized_date = normalizer.normalize(result.date)
        if normalized_date:
            normalized_date = _parse_date(normalized_date)
        else:
            normalized_date = _parse_date(result.date)
    
    # Criar Article
    article = Article(
        url=url,
        title=result.title,
        author=result.authors[0] if result.authors else None,
        date_published=normalized_date,
        text=clean_text,
        language=result.language,
        source=result.source,
        extra={
            "extractor": result.extractor,
            "confidence": result.confidence,
            "quality_score": result.quality_score(),
            "has_paywall": paywall_info['has_paywall'] if paywall_info else False,
            "paywall_confidence": paywall_info['confidence'] if paywall_info else 0.0,
            "text_length": len(clean_text) if clean_text else 0,
        },
    )
    
    # Validar
    if ADVANCED_TOOLS_AVAILABLE:
        validator = ContentValidator()
        if not validator.validate_title(article.title):
            logger.warning("Title validation failed")
        if not validator.validate_text(article.text):
            logger.warning("Text validation failed")
    
    return article


def _extract_with_trafilatura(html: str, url: str) -> Article | None:
    """Extrai usando trafilatura (método legado)."""

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
        return None

    try:
        payload: dict[str, Any] = json.loads(extracted_json)
    except Exception:
        return None

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
    if article.title is None or article.text is None or article.date_published is None or article.source is None:
        soup = BeautifulSoup(html, "lxml")

    if article.title is None and soup is not None:
        article.title = _title_from_html(soup)

    if article.text is None and soup is not None:
        article.text = _text_from_html_paragraphs(soup)
    
    if article.date_published is None and soup is not None:
        article.date_published = _date_from_html(soup)
    
    if article.source is None and soup is not None:
        article.source = _source_from_html(soup)

    # Normalização leve
    if article.text:
        article.text = "\n".join(line.rstrip() for line in article.text.splitlines()).strip() or None

    return article


def extract_article_metadata(url: str, driver) -> Article:
    """
    Extrai metadados de um artigo a partir de um driver Selenium.
    
    Args:
        url: URL do artigo
        driver: Instância do Selenium WebDriver
        
    Returns:
        Article com metadados extraídos
    """
    html = driver.page_source
    article = extract_article(html, url)
    
    # Adicionar timestamp de coleta
    article.scraped_at = datetime.now()
    
    return article
