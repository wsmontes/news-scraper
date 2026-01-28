"""
The Economist Scraper - Global business and financial news.

Site: https://www.economist.com
Características:
- Paywall forte
- Análise profunda
- Perspectiva global
- Semanal + online
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


class EconomistScraper(BaseScraper):
    """Scraper especializado para The Economist."""
    
    MIN_SUCCESS_RATE = 0.2
    HAS_PAYWALL = True
    
    CATEGORIES = {
        "finance": "https://www.economist.com/finance-and-economics",
        "business": "https://www.economist.com/business",
        "briefing": "https://www.economist.com/briefing",
        "leaders": "https://www.economist.com/leaders",
        "world": "https://www.economist.com/the-world-this-week",
    }
    
    SELECTORS = {
        "article_links": [
            "a.headline-link",
            "a[data-analytics='headline']",
            "article a",
        ],
        "title": [
            "h1.article__headline",
            "h1 span[itemprop='headline']",
        ],
        "text": [
            "div[itemprop='articleBody'] p",
            "section.article__body-text p",
        ],
        "date": [
            "time[datetime]",
            "time[itemprop='datePublished']",
        ],
        "author": [
            "span[itemprop='author']",
            "span.article__author",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="economist")
    
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
            category: Categoria (finance, business, briefing, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "finance"
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching The Economist articles from {category}: {url}")
        
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
                        if href and "economist.com" in href:
                            # Filtrar seções específicas
                            if any(section in href for section in ["/finance-", "/business/", "/briefing/", "/leaders/"]):
                                urls.add(href)
                                if len(urls) >= limit:
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} The Economist articles")
            return result
        
        except Exception as e:
            logger.error(f"Error fetching The Economist articles: {e}")
            return []
