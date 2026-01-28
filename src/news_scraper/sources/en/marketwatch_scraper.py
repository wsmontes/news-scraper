"""
MarketWatch Scraper - Dow Jones financial news.

Site: https://www.marketwatch.com
Características:
- Livre
- Foco em mercados e ações
- Dados em tempo real
- Análise de investimentos
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


class MarketWatchScraper(BaseScraper):
    """Scraper especializado para MarketWatch."""
    
    BASE_URL = "https://www.marketwatch.com"
    MIN_SUCCESS_RATE = 0.6  # 60% - livre, estável
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "latest": "https://www.marketwatch.com/latest-news",
        "markets": "https://www.marketwatch.com/markets",
        "investing": "https://www.marketwatch.com/investing",
        "personal-finance": "https://www.marketwatch.com/personal-finance",
        "economy-politics": "https://www.marketwatch.com/economy-politics",
    }
    
    SELECTORS = {
        "article_links": [
            "a.link",
            "h3.article__headline a",
            "a[data-type='article']",
        ],
        "title": [
            "h1.article__headline",
            "h1#article-headline",
        ],
        "text": [
            "div.article__body p",
            "div#js-article__body p",
        ],
        "date": [
            "time.article__timestamp",
            "time[datetime]",
        ],
        "author": [
            "a.author__link",
            "span.author__name",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="marketwatch")
    
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
            category: Categoria (latest, markets, investing, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "latest"
            
        if category not in self.CATEGORIES:
            logger.error(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
            return []
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching MarketWatch articles from {category}: {url}")
        
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
                        if href and "marketwatch.com" in href and "/story/" in href:
                            urls.add(href)
                            if len(urls) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} MarketWatch articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting MarketWatch URLs: {e}")
            return []
