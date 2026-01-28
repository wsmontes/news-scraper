"""
Yahoo Finance Scraper - US Edition
Specialized scraper for Yahoo Finance's stock market and latest news sections.

Sections:
- Stock Market News: https://finance.yahoo.com/topic/stock-market-news/
- Latest News: https://finance.yahoo.com/topic/latest-news/
"""

from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, List
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class YahooFinanceUSScraper(BaseScraper):
    """Scraper para Yahoo Finance US - seções especializadas."""

    BASE_URL = "https://finance.yahoo.com"
    
    # Configurações específicas
    MIN_SUCCESS_RATE = 0.6  # 60% para Yahoo (geralmente tem muitos artigos)
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "stock-market-news": "https://finance.yahoo.com/topic/stock-market-news/",
        "latest-news": "https://finance.yahoo.com/topic/latest-news/",
        "markets": "https://finance.yahoo.com/markets/",
        "news": "https://finance.yahoo.com/news/",
    }
    
    SELECTORS = {
        "article_links": [
            "h3 a",
            "div[data-test-locator='stream-item'] a",
            "a[data-ylk*='title']",
            "div.js-stream-content a",
        ],
        "title": [
            "h1",
            "header h1",
            "div[data-test-locator='headline'] h1",
        ],
        "body": [
            "div.caas-body",
            "div[data-test-locator='article-body']",
            "div.article-wrap article",
        ],
        "date": [
            "time",
            "div[data-test-locator='article-header'] time",
            "div.caas-attr-meta time",
        ],
    }

    def __init__(self, browser_scraper):
        """Inicializa o scraper."""
        super().__init__(browser_scraper, source_id="yahoofinance")
    
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
            category: Categoria específica (stock-market-news, latest-news, markets, news)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if category and category in self.CATEGORIES:
            url = self.CATEGORIES[category]
        else:
            # Default: stock market news
            url = self.CATEGORIES["stock-market-news"]

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
                        "?", "#", "/video", "/videos", "/search", "/finance.yahoo.com/m/",
                        "login", "signin", "subscribe", "newsletter"
                    ]):
                        continue
                    
                    # Aceita URLs de notícias
                    if any(pattern in href for pattern in [
                        "/news/", "/story/", "finance.yahoo.com/news",
                        "finance.yahoo.com/m/", "-"  # Yahoo usa slugs com hífens
                    ]):
                        full_url = urljoin(self.BASE_URL, href)
                        
                        # Remove query params
                        full_url = full_url.split("?")[0].split("#")[0]
                        
                        # Valida domínio
                        if "finance.yahoo.com" in full_url:
                            urls.add(full_url)
                
                if len(urls) >= limit:
                    break

            return sorted(list(urls))[:limit]

        except Exception as e:
            logger.error(f"Erro ao coletar URLs do Yahoo Finance US: {e}")
            return []
    
    def get_article_urls(self, category: str = "stock-market-news", limit: int = 20) -> List[str]:
        """
        Alias para get_latest_articles (compatibilidade).
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs de artigos
        """
        return self.get_latest_articles(category=category, limit=limit)


def scrape_yahoo_finance_us(
    browser_scraper,
    category: Optional[str] = None,
    limit: int = 20,
) -> List[str]:
    """
    Função de conveniência para scraping rápido do Yahoo Finance US.
    
    Args:
        browser_scraper: Instância do browser scraper
        category: Categoria específica (stock-market-news, latest-news)
        limit: Número máximo de URLs
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.browser import BrowserScraper
        >>> from news_scraper.sources.en.yahoofinance_scraper import scrape_yahoo_finance_us
        >>> 
        >>> browser = BrowserScraper()
        >>> urls = scrape_yahoo_finance_us(browser, category="stock-market-news", limit=10)
    """
    scraper = YahooFinanceUSScraper(browser_scraper)
    return scraper.get_latest_articles(category=category, limit=limit)
