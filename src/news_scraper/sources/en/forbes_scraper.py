"""
Forbes Scraper - Business, investing, and wealth.

Site: https://www.forbes.com
Características:
- Livre com anúncios
- Foco em negócios e fortuna
- Rankings e listas
- Artigos de contribuidores
"""

from __future__ import annotations

import logging
from typing import Optional, List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ForbesScraper(BaseScraper):
    """Scraper especializado para Forbes."""
    
    MIN_SUCCESS_RATE = 0.5
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "investing": "https://www.forbes.com/investing/",
        "markets": "https://www.forbes.com/markets/",
        "business": "https://www.forbes.com/business/",
        "money": "https://www.forbes.com/money/",
        "crypto": "https://www.forbes.com/crypto-blockchain/",
    }
    
    SELECTORS = {
        "article_links": [
            "a[data-ga-track='InternalLink']",
            "a.stream-item__title",
            "h3 a",
        ],
        "title": [
            "h1.article-headline",
            "h1.fs-headline",
        ],
        "text": [
            "div.article-body p",
            "div.article-body-container p",
        ],
        "date": [
            "time[datetime]",
            "span.article-timestamp",
        ],
        "author": [
            "a.contrib-link",
            "span.contrib-name",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="forbes")
    
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
            category: Categoria (investing, markets, business, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "investing"
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching Forbes articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Forbes tem muitos anúncios, esperar mais
            time.sleep(3)
            
            # Esperar carregar
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll
            self.scraper._scroll_page(driver, scroll_times=3)
            
            # Coletar links
            urls = set()
            for selector in self.SELECTORS["article_links"]:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute("href")
                        if href and "forbes.com" in href and "/sites/" in href:
                            # Filtrar páginas especiais
                            if "/video/" not in href and "/pictures/" not in href:
                                urls.add(href)
                                if len(urls) >= limit:
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} Forbes articles")
            return result
        
        except Exception as e:
            logger.error(f"Error fetching Forbes articles: {e}")
            return []
