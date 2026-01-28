"""
Investing.com Scraper
Specialized scraper for Investing.com News section.

Section:
- News: https://www.investing.com/news
"""

from __future__ import annotations
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, List
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class InvestingComScraper(BaseScraper):
    """Scraper para Investing.com News."""

    BASE_URL = "https://www.investing.com"
    
    # Configurações específicas
    MIN_SUCCESS_RATE = 0.5  # 50%
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "news": "https://www.investing.com/news/",
        "stock-market-news": "https://www.investing.com/news/stock-market-news",
        "economy": "https://www.investing.com/news/economy",
        "cryptocurrency-news": "https://www.investing.com/news/cryptocurrency-news",
        "commodities-news": "https://www.investing.com/news/commodities-news",
        "forex-news": "https://www.investing.com/news/forex-news",
    }
    
    SELECTORS = {
        "article_links": [
            "article a[data-test='article-title-link']",
            "div.largeTitle article a",
            "div.mediumTitle1 article a",
            "a.title",
            "article.js-article-item a",
        ],
        "title": [
            "h1",
            "h1.articleHeader",
            "div.articleHeader h1",
        ],
        "body": [
            "div.articlePage",
            "div[class*='article_WYSIWYG']",
            "div.WYSIWYG",
            "article",
        ],
        "date": [
            "time",
            "span[data-test='article-publish-date']",
            "div.contentSectionDetails span.date",
        ],
    }

    def __init__(self, browser_scraper):
        """Inicializa o scraper."""
        super().__init__(browser_scraper, source_id="investing")

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
            category: Categoria específica (news, stock-market-news, economy, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if category and category in self.CATEGORIES:
            url = self.CATEGORIES[category]
        else:
            # Default: news general
            url = self.CATEGORIES["news"]

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
                        "#", "?", "/pro/", "/academy/", "/tools/",
                        "login", "signin", "register", "subscribe",
                        "/analysis/", "/opinion/", "/video/"
                    ]):
                        continue
                    
                    # Aceita apenas artigos de notícias
                    # Investing.com usa padrão: /news/something/article-title-12345
                    if "/news/" in href:
                        full_url = urljoin(self.BASE_URL, href)
                        
                        # Remove query params
                        full_url = full_url.split("?")[0].split("#")[0]
                        
                        # Valida domínio e formato
                        if "investing.com" in full_url and full_url.startswith("http"):
                            # Garante que é um artigo (tem ID numérico no final)
                            if any(char.isdigit() for char in full_url.split("/")[-1]):
                                urls.add(full_url)
                    
                    if len(urls) >= limit:
                        break
                
                if len(urls) >= limit:
                    break

            return sorted(list(urls))[:limit]

        except Exception as e:
            logger.error(f"Erro ao coletar URLs do Investing.com: {e}")
            return []

    def get_article_urls(self, category: str = "news", limit: int = 20) -> List[str]:
        """
        Alias para get_latest_articles (compatibilidade).
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs de artigos
        """
        return self.get_latest_articles(category=category, limit=limit)


def scrape_investing_com(
    browser_scraper,
    category: Optional[str] = None,
    limit: int = 20,
) -> List[str]:
    """
    Função de conveniência para scraping rápido do Investing.com.
    
    Args:
        browser_scraper: Instância do browser scraper
        category: Categoria específica (news, stock-market-news, economy)
        limit: Número máximo de URLs
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.browser import BrowserScraper
        >>> from news_scraper.sources.en.investing_scraper import scrape_investing_com
        >>> 
        >>> browser = BrowserScraper()
        >>> urls = scrape_investing_com(browser, category="stock-market-news", limit=10)
    """
    scraper = InvestingComScraper(browser_scraper)
    return scraper.get_latest_articles(category=category, limit=limit)
