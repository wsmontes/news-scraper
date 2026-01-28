"""
Barron's Scraper - Dow Jones premium financial weekly.

Site: https://www.barrons.com
Características:
- Paywall
- Análise aprofundada
- Recomendações de investimento
- Parte do grupo Dow Jones (WSJ)
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


class BarronsScraper(BaseScraper):
    """Scraper especializado para Barron's."""
    
    MIN_SUCCESS_RATE = 0.2
    HAS_PAYWALL = True
    
    CATEGORIES = {
        "market-news": "https://www.barrons.com/market-news",
        "stocks": "https://www.barrons.com/topics/stocks",
        "investing": "https://www.barrons.com/topics/investing",
        "advisor": "https://www.barrons.com/advisor",
        "features": "https://www.barrons.com/news/features",
    }
    
    SELECTORS = {
        "article_links": [
            "a.WSJTheme--headline--unZqjb45",
            "h3.WSJTheme--headline--unZqjb45 a",
            "a[data-type='article']",
        ],
        "title": [
            "h1.article-headline",
            "h1[data-testid='headline']",
        ],
        "text": [
            "div.article-content p",
            "section[data-testid='article-content'] p",
        ],
        "date": [
            "time[data-testid='timestamp']",
            "time.timestamp",
        ],
        "author": [
            "span[itemprop='name']",
            "a.author",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="barrons")
    
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
            category: Categoria (market-news, stocks, investing, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "market-news"
            
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching Barron's articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 10).until(
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
                        if href and "barrons.com" in href and "/articles/" in href:
                            urls.add(href)
                            if len(urls) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} Barron's articles")
            return result
        
        except Exception as e:
            logger.error(f"Error fetching Barron's articles: {e}")
            return []
