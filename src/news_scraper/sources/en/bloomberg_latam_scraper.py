"""
Bloomberg Latin America Scraper
Specialized scraper for Bloomberg's Latin America section.

Section:
- Latin America: https://www.bloomberg.com/latinamerica
"""

from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, List
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BloombergLatAmScraper(BaseScraper):
    """Scraper para Bloomberg Latin America."""

    BASE_URL = "https://www.bloomberg.com"
    
    # Configurações específicas
    MIN_SUCCESS_RATE = 0.5  # 50%
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "latinamerica": "https://www.bloomberg.com/latinamerica",
        "latin-america": "https://www.bloomberg.com/latin-america",
        "news": "https://www.bloomberg.com/news",
        "markets": "https://www.bloomberg.com/markets",
    }
    
    SELECTORS = {
        "article_links": [
            "article a[href*='/news/']",
            "a[data-component='headline-link']",
            "div[data-component='story-card'] a",
            "a[href*='/articles/']",
            "a.story-list-story__info__headline-link",
        ],
        "title": [
            "h1",
            "h1[data-component='headline']",
            "div.lede-text-only__highlight",
        ],
        "body": [
            "div[data-component='article-body']",
            "div.body-content",
            "article",
        ],
        "date": [
            "time",
            "div.published-at",
            "time[datetime]",
        ],
    }

    def __init__(self, browser_scraper):
        """Inicializa o scraper."""
        super().__init__(browser_scraper, source_id="bloomberg-latam")

    def _collect_urls(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[str]:
        """
        Implementação da coleta de URLs (método abstrato da classe base).
        
        Args:
            category: Categoria específica (latinamerica, news, markets)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if category and category in self.CATEGORIES:
            url = self.CATEGORIES[category]
        else:
            # Default: latinamerica
            url = self.CATEGORIES["latinamerica"]

        try:
            # Carrega a página com espera
            html = self.scraper.get_page(url, wait_time=5)
            
            # Scroll para carregar mais conteúdo
            html = self.scraper.scroll_and_load(scroll_pause=3.0, max_scrolls=5)
            
            soup = BeautifulSoup(html, "lxml")
            urls: set[str] = set()

            # Tenta todos os seletores de links
            for selector in self.SELECTORS["article_links"]:
                links = soup.select(selector)
                
                for link in links:
                    href = link.get("href", "")
                    
                    if not href:
                        continue
                    
                    # Evita URLs indesejadas
                    if any(skip in href for skip in [
                        "#", "?utm_", "/subscribe", "/account",
                        "/live/", "/video/", "/audio/", "/graphics/",
                        "login", "signin"
                    ]):
                        continue
                    
                    # Aceita apenas artigos de notícias
                    # Bloomberg usa padrões: /news/articles/, /news/features/
                    if any(pattern in href for pattern in [
                        "/news/articles/", "/news/features/", 
                        "/opinion/articles/", "/articles/"
                    ]):
                        full_url = urljoin(self.BASE_URL, href)
                        
                        # Remove query params
                        full_url = full_url.split("?")[0].split("#")[0]
                        
                        # Valida domínio
                        if "bloomberg.com" in full_url and full_url.startswith("http"):
                            urls.add(full_url)
                    
                    if len(urls) >= limit:
                        break
                
                if len(urls) >= limit:
                    break

            return sorted(list(urls))[:limit]

        except Exception as e:
            logger.error(f"Erro ao coletar URLs do Bloomberg Latin America: {e}")
            return []

    def get_article_urls(self, category: str = "latinamerica", limit: int = 20) -> List[str]:
        """
        Alias para get_latest_articles (compatibilidade).
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs de artigos
        """
        return self.get_latest_articles(category=category, limit=limit)


def scrape_bloomberg_latam(
    browser_scraper,
    category: Optional[str] = None,
    limit: int = 20,
) -> List[str]:
    """
    Função de conveniência para scraping rápido do Bloomberg Latin America.
    
    Args:
        browser_scraper: Instância do browser scraper
        category: Categoria específica (latinamerica, news, markets)
        limit: Número máximo de URLs
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.browser import BrowserScraper
        >>> from news_scraper.sources.en.bloomberg_latam_scraper import scrape_bloomberg_latam
        >>> 
        >>> browser = BrowserScraper()
        >>> urls = scrape_bloomberg_latam(browser, category="latinamerica", limit=10)
    """
    scraper = BloombergLatAmScraper(browser_scraper)
    return scraper.get_latest_articles(category=category, limit=limit)
