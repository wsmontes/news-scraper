"""
Seeking Alpha Scraper - Investing insights and analysis.

Site: https://seekingalpha.com
Características:
- Análises de investimento
- Foco em ações e ETFs
- Artigos de contribuidores
- Alguns com paywall
"""

from __future__ import annotations

import logging
from typing import Optional, List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SeekingAlphaScraper(BaseScraper):
    """Scraper especializado para Seeking Alpha."""
    
    BASE_URL = "https://seekingalpha.com"
    MIN_SUCCESS_RATE = 0.3  # 30% - paywall parcial
    HAS_PAYWALL = "partial"
    
    CATEGORIES = {
        "market-news": "https://seekingalpha.com/market-news",
        "top-news": "https://seekingalpha.com/news/top-news",
        "wall-street-breakfast": "https://seekingalpha.com/news/wall-street-breakfast",
        "etfs": "https://seekingalpha.com/etfs-and-funds",
        "analysis": "https://seekingalpha.com/stock-ideas",
    }
    
    SELECTORS = {
        "article_links": [
            "a[data-test-id='post-list-item-title']",
            "a.fKDIJc",
            "h3 a",
        ],
        "title": [
            "h1[data-test-id='post-title']",
            "h1.article-title",
        ],
        "text": [
            "div[data-test-id='content-container'] p",
            "div.paywall-full-content p",
        ],
        "date": [
            "time[datetime]",
            "span[data-test-id='post-date']",
        ],
        "author": [
            "span[data-test-id='post-author']",
            "a.author-link",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="seekingalpha")
    
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
            category: Categoria (market-news, top-news, analysis, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "market-news"
            
        if category not in self.CATEGORIES:
            logger.error(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
            return []
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching Seeking Alpha articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll
            self.scraper._scroll_page(driver, scroll_times=2)
            
            # Coletar links
            urls = set()
            for selector in self.SELECTORS["article_links"]:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute("href")
                        if href and "seekingalpha.com" in href and ("/article/" in href or "/news/" in href):
                            if not href.startswith("http"):
                                href = "https://seekingalpha.com" + href
                            urls.add(href)
                            if len(urls) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} Seeking Alpha articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting Seeking Alpha URLs: {e}")
            return []
