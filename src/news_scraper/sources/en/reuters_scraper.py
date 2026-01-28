"""
Reuters Scraper - Global news agency.

Site: https://www.reuters.com
Características:
- Livre (sem paywall)
- Cobertura global
- Alta frequência de publicação
- Categorias: markets, world, business, technology
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


class ReutersScraper(BaseScraper):
    """Scraper especializado para Reuters."""
    
    BASE_URL = "https://www.reuters.com"
    MIN_SUCCESS_RATE = 0.6  # 60% - sem paywall, estável
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "markets": "https://www.reuters.com/markets/",
        "business": "https://www.reuters.com/business/",
        "technology": "https://www.reuters.com/technology/",
        "world": "https://www.reuters.com/world/",
        "breakingviews": "https://www.reuters.com/breakingviews/",
    }
    
    SELECTORS = {
        "article_links": [
            "a[data-testid='Heading']",
            "a.text__text__1FZLe",
            "h3 a",
        ],
        "title": [
            "h1[data-testid='Heading']",
            "h1.article-header__title",
        ],
        "text": [
            "div[data-testid='paragraph-0']",
            "p[data-testid^='paragraph']",
            "div.article-body__content p",
        ],
        "date": [
            "time[datetime]",
            "span.article__time",
        ],
        "author": [
            "a.author__author-name",
            "span.author-name",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="reuters")
    
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
            category: Categoria (markets, business, technology, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "markets"
            
        if category not in self.CATEGORIES:
            logger.error(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
            return []
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching Reuters articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll para carregar mais
            self.scraper._scroll_page(driver, scroll_times=3)
            
            # Coletar links
            urls = set()
            for selector in self.SELECTORS["article_links"]:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute("href")
                        if href and ("/article/" in href or "/markets/" in href or "/business/" in href):
                            # Filtrar anúncios e páginas especiais
                            if "sponsored" not in href.lower() and "video" not in href.lower():
                                urls.add(href)
                                if len(urls) >= limit:
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} Reuters articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting Reuters URLs: {e}")
            return []
