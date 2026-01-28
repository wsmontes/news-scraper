"""
Business Insider Scraper
Specialized scraper for Business Insider and Business Insider Markets.

Sections:
- Main: https://www.businessinsider.com/
- Markets: https://markets.businessinsider.com/
"""

from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, List
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BusinessInsiderScraper(BaseScraper):
    """Scraper para Business Insider e Business Insider Markets."""

    BASE_URL = "https://www.businessinsider.com"
    MARKETS_URL = "https://markets.businessinsider.com"
    
    # Configurações específicas
    MIN_SUCCESS_RATE = 0.5  # 50% para Business Insider (pode ter paywall)
    HAS_PAYWALL = "partial"  # Paywall parcial
    
    CATEGORIES = {
        "main": "https://www.businessinsider.com/",
        "markets": "https://markets.businessinsider.com/",
        "finance": "https://www.businessinsider.com/finance",
        "investing": "https://www.businessinsider.com/investing",
        "stocks": "https://markets.businessinsider.com/stocks",
        "news": "https://markets.businessinsider.com/news",
    }
    
    SELECTORS = {
        "article_links": [
            "a[data-test='article-link']",
            "h2 a",
            "h3 a",
            "div.tout-title-link a",
            "a.tout-title-link",
            "div[data-e2e-name='post-card'] a",
        ],
        "title": [
            "h1",
            "h1.post-headline",
            "h1[data-e2e-name='post-title']",
            "div.content-lock-content h1",
        ],
        "body": [
            "div[data-piano-inline-content-wrapper]",
            "div.content-lock-content",
            "div.post-content",
            "article",
        ],
        "date": [
            "time",
            "span[data-e2e-name='post-date']",
            "div.byline-timestamp time",
        ],
    }

    def __init__(self, browser_scraper):
        """Inicializa o scraper."""
        super().__init__(browser_scraper, source_id="businessinsider")

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
            category: Categoria específica (main, markets, finance, investing, stocks, news)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if category and category in self.CATEGORIES:
            url = self.CATEGORIES[category]
        else:
            # Default: main site
            url = self.CATEGORIES["main"]

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
                        "#", "/subscribe", "/newsletters", "/podcasts",
                        "login", "signin", "register", "/category/",
                        "/author/", "/tag/", "?utm_", "/search"
                    ]):
                        continue
                    
                    # Aceita apenas artigos
                    # Business Insider usa slugs como: /title-with-words-2024-1
                    if href.startswith("/") or "businessinsider.com" in href:
                        # Determina base URL correta
                        if "markets.businessinsider.com" in url or "markets.businessinsider.com" in href:
                            base = self.MARKETS_URL
                        else:
                            base = self.BASE_URL
                        
                        full_url = urljoin(base, href)
                        
                        # Remove query params
                        full_url = full_url.split("?")[0].split("#")[0]
                        
                        # Valida domínio e formato
                        if "businessinsider.com" in full_url and full_url.startswith("http"):
                            # Evita páginas de categoria/homepage
                            path = full_url.replace(self.BASE_URL, "").replace(self.MARKETS_URL, "")
                            if path and len(path) > 5 and path.count("/") >= 2:
                                urls.add(full_url)
                    
                    if len(urls) >= limit:
                        break
                
                if len(urls) >= limit:
                    break

            return sorted(list(urls))[:limit]

        except Exception as e:
            logger.error(f"Erro ao coletar URLs do Business Insider: {e}")
            return []

    def get_article_urls(self, category: str = "main", limit: int = 20) -> List[str]:
        """
        Alias para get_latest_articles (compatibilidade).
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs de artigos
        """
        return self.get_latest_articles(category=category, limit=limit)


def scrape_business_insider(
    browser_scraper,
    category: Optional[str] = None,
    limit: int = 20,
) -> List[str]:
    """
    Função de conveniência para scraping rápido do Business Insider.
    
    Args:
        browser_scraper: Instância do browser scraper
        category: Categoria específica (main, markets, finance, investing)
        limit: Número máximo de URLs
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.browser import BrowserScraper
        >>> from news_scraper.sources.en.businessinsider_scraper import scrape_business_insider
        >>> 
        >>> browser = BrowserScraper()
        >>> urls = scrape_business_insider(browser, category="markets", limit=10)
    """
    scraper = BusinessInsiderScraper(browser_scraper)
    return scraper.get_latest_articles(category=category, limit=limit)
